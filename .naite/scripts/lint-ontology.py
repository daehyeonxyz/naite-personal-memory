#!/usr/bin/env python3
"""
lint-ontology.py — Deterministic ontology validator for naite.

Implements the deterministic checks of `.claude/skills/naite/care-check.md § 3 Ontology validation`:

  3a Frontmatter completeness  — required facets + valid enum values
  3b Subject tree validation   — subject path against .naite/ontology/subject-tree.md
  3c Topic canonical           — topic against .naite/ontology/topics.md (with alias resolution)
  3d Domain cache freshness    — domains == derive_domains(subject)
  3e Kind / form / source-types distribution
  3f BOM detection
  3g Legacy collection drift   — pre-migration tags surfaced
  3h Language-shape review candidates
  3i Schema integrity (drift detector)
  3j Output quality contract guard
  3k Leaf-depth guard
  7  Non-tree scratch dirt

Cluster detection (Louvain) and topic alias clustering are LLM-driven —
see `.claude/skills/naite/care-check.md` for the full workflow.

Usage:
    python .naite/scripts/lint-ontology.py                    # report only
    python .naite/scripts/lint-ontology.py --strip-bom        # also normalize BOM in-place
    python .naite/scripts/lint-ontology.py --refresh-domains  # rewrite stale domains cache in-place

Exit codes:
    0 — clean
    1 — at least one blocking issue (incomplete / invalid subject / cache stale / legacy drift / body em dash)
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths + canonical sources
# ---------------------------------------------------------------------------

NAITE_ROOT = Path(__file__).resolve().parent.parent.parent
TREE_DIR = NAITE_ROOT / 'tree'
ONTOLOGY_DIR = NAITE_ROOT / '.naite' / 'ontology'
SPECIALS = {'trunk.md', 'rings.md', 'seeds.md'}
OUTPUT_QUALITY_SPECIALS = {'trunk.md', 'rings.md', 'seeds.md'}
BOM = b'\xef\xbb\xbf'

# Schema enums (current facet schema).
# Single source: .naite/ontology/facets.json (shared with naite-app filter UI).
# Hardcoded tuples below are the fallback when facets.json is missing/corrupt.
# Rationale: docs/ARCHITECTURE.md § 3 (facet redesign).
# personal: user-declared kind, core:false (schema_version 2 facets.json).
FACETS_PATH = ONTOLOGY_DIR / 'facets.json'


def _facet_values(name, fallback):
    # schema_version 1: values is a list of strings.
    # schema_version 2: kind values are {value, core} objects (core kinds are
    # harness-known and fixed; user kinds are vault-declared). Normalize both.
    try:
        data = json.loads(FACETS_PATH.read_text(encoding='utf-8'))
        values = data['facets'][name]['values']
        out = []
        for v in values:
            if isinstance(v, str):
                out.append(v)
            elif isinstance(v, dict) and isinstance(v.get('value'), str):
                out.append(v['value'])
        if out:
            return tuple(out)
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return fallback


KINDS = _facet_values('kind', ('concept', 'entity', 'source-record', 'project', 'decision', 'insight', 'comparison', 'essay', 'personal'))
FORMS = _facet_values('form', ('prose', 'index'))
SOURCE_TYPES_NEW = _facet_values('source-types', ('course', 'conversation', 'paper', 'article', 'docs', 'book', 'essay', 'external'))

# Legacy schema enums — kept ONLY for diagnostic (detect_schema returns 'legacy' to flag drift).
# Legacy schema fields from an earlier design. Legacy pages are errors.
LEGACY_ROLES = ('concept', 'project', 'decision', 'insight', 'question', 'comparison', 'reference')
LEGACY_SOURCE_TYPES = ('course', 'paper', 'article', 'docs', 'conversation', 'external')
LEGACY_TYPES = ('concept', 'entity', 'source')

# Pre-migration legacy tags that should never appear in `subject` (3g).
# Keep only genuinely generic tokens here. Vault-specific tags (e.g. ode,
# laplace-transform, anthropic-academy, engineering-mathematics) belong in a
# per-clone local denylist, not in this neutral starter.
LEGACY_TAGS = {
    'course',
    'education',
}

OUTPUT_QUALITY_PATTERNS = [
    ('em-dash', re.compile('\u2014')),
    ('roots-path', re.compile(r'`?roots[\\/][^`\s)]*', re.IGNORECASE)),
    ('source-process', re.compile(
        r'\b(?:Staging|Source Staging|Archived source bundle|PDF page|raw PDF|source PDF|source page|lecture notes|page range|render|image-read|backfill|run-log|extraction)\b',
        re.IGNORECASE,
    )),
    ('korean-source-voice', re.compile(
        r'(필기에는|필기에서|강의 노트|노트에서는|원문에서는|원자료|자료에서는|페이지에서는|이 페이지에서는|이 자료)'
    )),
    ('mojibake', re.compile(r'(\?\?\?|�|Ã|Â)')),
]

GENERIC_EN_COURSE_HEADINGS = {
    'status',
    'scope',
    'chapters',
    'projects',
    'connections',
    'also known as',
    'overview',
    'related',
    'sequence logic',
    'practice & assignments',
    'course bridges',
    'concept extraction',
    'source staging',
    'names',
    'maps to',
}


def detect_schema(fm):
    """Detect which schema a page uses based on facet field names.

    Returns one of: 'new', 'legacy', 'mixed', 'unknown'.
    - 'new': has new facets (kind / form / source-types), no legacy
    - 'legacy': has legacy facets (type / role / source-type), no new
    - 'mixed': has both — warning (drift signal, must be 0 for clean state)
    - 'unknown': no schema fields detected at all
    """
    has_new = any(k in fm for k in ('kind', 'form', 'source-types'))
    has_legacy = any(k in fm for k in ('type', 'role', 'source-type'))
    if has_new and has_legacy:
        return 'mixed'
    if has_new:
        return 'new'
    if has_legacy:
        return 'legacy'
    return 'unknown'


# ---------------------------------------------------------------------------
# Subject tree loader
# ---------------------------------------------------------------------------

def parse_yaml_list(value):
    """Parse the small flow/block-list subset used by .naite/ontology/*.md."""
    value = value.strip()
    if not value:
        return None
    if value == '[]':
        return []
    if value.startswith('[') and value.endswith(']'):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip('"\'') for item in inner.split(',') if item.strip()]
    return None


def _read_ontology_source(name: str) -> str:
    """Read an ontology source file, failing with an actionable message (not a raw
    traceback) if it is missing — e.g. run outside a vault or a partial clone."""
    path = ONTOLOGY_DIR / name
    if not path.exists():
        sys.exit(f'lint-ontology: missing ontology source: {path}\n'
                 f'  Run from a naite vault root (the starter ships .naite/ontology/{name}).')
    return path.read_text(encoding='utf-8')


def load_subject_tree():
    """Parse subjects + top-level altLabels from .naite/ontology/subject-tree.md."""
    text = _read_ontology_source('subject-tree.md')
    match = re.search(r'```yaml\s*\n\s*subjects:\s*\n(.*?)\n```', text, re.DOTALL)
    if not match:
        raise RuntimeError('Could not find subjects YAML block in .naite/ontology/subject-tree.md')

    tree, aliases = {}, {}
    current, field = None, None
    for raw in match.group(1).splitlines():
        if not raw.strip() or raw.strip().startswith('#'):
            continue

        top_match = re.match(r'^ {2}([a-z0-9-]+):\s*$', raw)
        if top_match:
            current = top_match.group(1)
            tree[current] = []
            field = None
            continue

        field_match = re.match(r'^ {4}(altLabels|narrower):\s*(.*)$', raw)
        if current and field_match:
            field = field_match.group(1)
            values = parse_yaml_list(field_match.group(2))
            if values is not None:
                if field == 'narrower':
                    tree[current] = values
                else:
                    for alias in values:
                        aliases[alias] = current
            continue

        item_match = re.match(r'^ {6}-\s+(.+?)\s*$', raw)
        if current and field and item_match:
            value = item_match.group(1).strip().strip('"\'')
            if field == 'narrower':
                tree[current].append(value)
            else:
                aliases[value] = current

    return tree, aliases


CANONICAL_TREE, SUBJECT_ALIASES = load_subject_tree()


# ---------------------------------------------------------------------------
# Topic governance loader
# ---------------------------------------------------------------------------

def load_topic_governance():
    """Parse canonical_topics + aliases from .naite/ontology/topics.md YAML blocks."""
    text = _read_ontology_source('topics.md')
    canonical, aliases = [], {}

    m = re.search(r'```yaml\s*\n\s*canonical_topics:\s*\n(.*?)\n```', text, re.DOTALL)
    if m:
        for line in m.group(1).splitlines():
            line = line.strip()
            if line.startswith('- '):
                canonical.append(line[2:].strip())

    m = re.search(r'```yaml\s*\n\s*aliases:\s*\n(.*?)\n```', text, re.DOTALL)
    if m:
        for line in m.group(1).splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ':' in line:
                k, v = line.split(':', 1)
                aliases[k.strip()] = v.strip()

    return canonical, aliases


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

def parse_frontmatter(path):
    """Returns (fm_dict, has_bom)."""
    raw = path.read_bytes()
    has_bom = raw.startswith(BOM)
    text = raw.decode('utf-8-sig')
    if not text.startswith('---'):
        return None, has_bom
    end = text.find('\n---', 3)
    if end == -1:
        return None, has_bom
    fm_text = text[3:end].strip()
    fm = {}
    for line in fm_text.split('\n'):
        m = re.match(r'^([A-Za-z0-9_-]+):\s*(.*)$', line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm, has_bom


def parse_list_value(val):
    """YAML flow list `[a, b]` → ['a', 'b']. Empty `[]` → []. Quoted items
    (`["a", 'b']`) are unquoted, matching build-tree-manifest.py's parser —
    the two must agree or a valid page passes manifest but fails lint."""
    if val.startswith('[') and val.endswith(']'):
        inner = val[1:-1].strip()
        if not inner:
            return []
        return [x.strip().strip('"\'') for x in inner.split(',')]
    return [val.strip('"\'')]


def derive_domains(subject_paths):
    """First-occurrence dedupe, canonicalizing top-level aliases."""
    seen = []
    for p in subject_paths:
        top = p.split('/')[0]
        top = SUBJECT_ALIASES.get(top, top)
        if top not in seen:
            seen.append(top)
    return seen


def validate_subject_path(path):
    """Return error message or None if valid."""
    parts = path.split('/')
    top = parts[0]
    canonical_top = SUBJECT_ALIASES.get(top, top)
    if canonical_top not in CANONICAL_TREE:
        return f'unknown top-level: {path}'
    if len(parts) > 1:
        narrower = parts[1]
        if narrower not in CANONICAL_TREE[canonical_top]:
            return f'unknown narrower: {path}'
    if len(parts) > 2:
        return f'path too deep (only top-level/narrower supported): {path}'
    return None


# ---------------------------------------------------------------------------
# Lint pass
# ---------------------------------------------------------------------------

def is_hangul(ch):
    return '가' <= ch <= '힯' or '㄰' <= ch <= '㆏'


def is_latin_letter(ch):
    return ('a' <= ch <= 'z') or ('A' <= ch <= 'Z')


def find_language_shape_candidates(path):
    """Return list of (line_no, kind) where kind in {'prose-no-hangul', 'heading-no-latin'}.

    Surface candidate lines per docs/CONVENTIONS.md § Naming policy (Korean prose +
    English headings/terms). false positive expected — manual review required.
    No ratios, no thresholds.
    """
    text = path.read_text(encoding='utf-8', errors='replace')
    lines = text.splitlines()
    in_frontmatter = False
    in_code_block = False
    in_math_block = False
    candidates = []

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Frontmatter (YAML between ---)
        if i == 1 and stripped == '---':
            in_frontmatter = True
            continue
        if in_frontmatter:
            if stripped == '---':
                in_frontmatter = False
            continue

        # Code block toggle
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # Math block toggle
        if stripped == '$$':
            in_math_block = not in_math_block
            continue
        if in_math_block:
            continue

        if not stripped:
            continue

        is_heading = stripped.startswith('#')
        has_hangul = any(is_hangul(ch) for ch in line)
        has_latin = any(is_latin_letter(ch) for ch in line)

        if is_heading:
            # heading should have English. Latin absence -> candidate.
            # require any alpha presence to skip empty/symbol-only headings
            if (has_hangul or has_latin) and not has_latin:
                candidates.append((i, 'heading-no-latin'))
        else:
            # prose context. Skip lines that have no alpha at all
            # (pure formula / list bullets / wikilinks etc.)
            if not (has_hangul or has_latin):
                continue
            # prose should have Korean. Hangul absence -> candidate.
            if not has_hangul:
                candidates.append((i, 'prose-no-hangul'))

    return candidates


def body_line_bounds_before_source(text):
    """Return 0-based [start, end) line bounds after frontmatter and before trailing Source."""
    lines = text.splitlines()
    start = 0
    if lines and lines[0].strip() == '---':
        for idx in range(1, len(lines)):
            if lines[idx].strip() == '---':
                start = idx + 1
                break

    last_h2 = None
    in_code_block = False
    in_math_block = False
    for idx in range(start, len(lines)):
        stripped = lines[idx].strip()
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if stripped == '$$':
            in_math_block = not in_math_block
            continue
        if in_math_block:
            continue
        match = re.match(r'^##\s+(.+?)\s*$', stripped)
        if match:
            last_h2 = (idx, match.group(1))

    end = len(lines)
    if last_h2 and last_h2[1].lower() == 'source':
        end = last_h2[0]
    return lines, start, end


def strip_inline_code_literals(line):
    return re.sub(r'(`+)(.*?)\1', '', line)


def git_added_line_numbers(path):
    try:
        relative = path.resolve().relative_to(NAITE_ROOT.resolve()).as_posix()
    except ValueError:
        return None

    tracked = subprocess.run(
        ['git', '-C', str(NAITE_ROOT), 'ls-files', '--error-unmatch', '--', relative],
        capture_output=True, text=True, encoding='utf-8', errors='replace',
    )
    if tracked.returncode != 0:
        return None

    diff = subprocess.run(
        ['git', '-C', str(NAITE_ROOT), 'diff', 'HEAD', '--unified=0', '--no-color', '--', relative],
        capture_output=True, text=True, encoding='utf-8', errors='replace', check=True,
    ).stdout
    added = set()
    new_line = None
    for raw in diff.splitlines():
        if raw.startswith('@@'):
            match = re.search(r'\+(\d+)(?:,\d+)?', raw)
            new_line = int(match.group(1)) if match else None
            continue
        if new_line is None or raw.startswith(('+++', '---')):
            continue
        if raw.startswith('+'):
            added.add(new_line)
            new_line += 1
        elif raw.startswith('-'):
            continue
        elif raw.startswith(' '):
            new_line += 1
    return added


def find_rings_output_quality_findings(path):
    findings = find_output_quality_findings(path)
    added = git_added_line_numbers(path)
    if added is None:
        return findings
    return [finding for finding in findings if finding[0] in added]


def count_historical_rings_em_dash(path):
    lines = path.read_text(encoding='utf-8-sig', errors='replace').splitlines()
    added = git_added_line_numbers(path)
    if added is None:
        return 0
    return sum(line.count('—') for line_no, line in enumerate(lines, start=1)
               if line_no not in added)


def normalize_heading_text(line):
    """Return a plain heading label for exact generic-heading checks."""
    text = re.sub(r'^#{1,6}\s+', '', line.strip()).strip()
    text = re.sub(r'[`*_]', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def find_output_quality_findings(path):
    is_course_page = path.name.startswith('course-')

    # Course/chapter meta index pages (course-*-00-index.md) are template-driven:
    # grow-branch.md § Templates mandates the generic headings and a
    # `Staging: roots/...` pointer there. Only mojibake applies to them; the
    # heading/leakage guard targets prose pages (subchapter notes, leaves).
    is_meta_index = is_course_page and path.name.endswith('-00-index.md')

    text = path.read_text(encoding='utf-8-sig', errors='replace')
    lines, start, end = body_line_bounds_before_source(text)
    findings = []
    in_code_block = False
    in_math_block = False

    for idx in range(start, end):
        line = lines[idx]
        stripped = line.strip()
        line_no = idx + 1

        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if stripped == '$$':
            in_math_block = not in_math_block
            continue
        if in_math_block or not stripped:
            continue

        if is_course_page and not is_meta_index and stripped.startswith('#'):
            heading = normalize_heading_text(stripped).lower()
            if heading in GENERIC_EN_COURSE_HEADINGS:
                findings.append((line_no, 'generic-heading', normalize_heading_text(stripped)))

        for kind, pattern in OUTPUT_QUALITY_PATTERNS:
            if kind == 'em-dash':
                if re.match(r'^#\s+', stripped):
                    continue
                match = pattern.search(strip_inline_code_literals(line))
                if match:
                    findings.append((line_no, kind, match.group(0)))
                continue
            if not is_course_page:
                continue
            if is_meta_index and kind != 'mojibake':
                continue
            match = pattern.search(line)
            if match:
                findings.append((line_no, kind, match.group(0)))

    return findings


LEAF_DEPTH_MIN_BODY_CHARS = 400  # tunable floor: prose chars (heading/code/math 제외) before ## Source


def find_leaf_depth_findings(path, form):
    """Warn-only leaf-depth proxy for form=prose leaves.

    Flags (a) no in-body wikilink, (b) prose body below the char floor.
    Deterministic proxy only. The real depth bar is the write-time self-check
    against docs/QUALITY.md § 4 (LEAF-1..4). Never blocking.
    """
    if form != 'prose':
        return []
    text = path.read_text(encoding='utf-8-sig', errors='replace')
    lines, start, end = body_line_bounds_before_source(text)
    in_code_block = False
    in_math_block = False
    prose_chars = 0
    wikilinks = 0
    for idx in range(start, end):
        stripped = lines[idx].strip()
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if stripped == '$$':
            in_math_block = not in_math_block
            continue
        if in_math_block or not stripped:
            continue
        if stripped.startswith('#'):
            continue
        wikilinks += len(re.findall(r'\[\[[^\][]+\]\]', stripped))  # exclude '[' → no O(n^2) on "[[[[..."
        prose_chars += len(stripped)
    findings = []
    if wikilinks == 0:
        findings.append((0, 'no-inbody-link', 'body has no [[wikilink]]'))
    if prose_chars < LEAF_DEPTH_MIN_BODY_CHARS:
        findings.append((0, 'thin-body', f'{prose_chars} prose chars (< {LEAF_DEPTH_MIN_BODY_CHARS})'))
    return findings


def find_non_tree_dirt(repo_root):
    """Return list of (tracked_path, reason) for files matching agent/IDE scratch patterns.

    Surfaces accumulation of codex / agent / IDE scratch under the naite vault —
    these should be gitignored, not committed. Per `care-check.md § 7 Non-tree scratch dirt`.
    Warn-only (non-blocking).
    """
    try:
        out = subprocess.run(
            ['git', '-C', str(repo_root), '-c', 'core.quotePath=false', 'ls-files'],
            capture_output=True, text=True, encoding='utf-8', errors='replace', check=True,
        ).stdout.splitlines()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []

    # Strong-signal scratch dirs (almost never intentional in naite vault).
    # NOTE: .codex-work/ is intentionally NOT in this list — the user may use it
    # as a deliberate sub-project workspace. node_modules/ at any depth is the
    # canonical dirt signal.
    SCRATCH_DIR_PREFIXES = [
        ('.codex-cache/', 'codex CLI cache'),
        ('.aider/', 'aider scratch'),
        ('.cursor/', 'cursor IDE local state'),
        ('.windsurfai/', 'windsurfai local state'),
    ]

    matches = []
    for path in out:
        matched = False
        for prefix, reason in SCRATCH_DIR_PREFIXES:
            if path.startswith(prefix):
                matches.append((path, reason))
                matched = True
                break
        if matched:
            continue
        # node_modules/ at any depth — should always be gitignored.
        if path.startswith('node_modules/') or '/node_modules/' in path:
            matches.append((path, 'node_modules/ tracked'))
            continue
        # ad-hoc scratch markdown at repo root (no slash, lowercase gpt-* / claude-* prefix, .md suffix).
        # Case-sensitive: CLAUDE.md (project policy, uppercase) is sentinel, not scratch.
        if '/' not in path and path.endswith('.md'):
            if path.startswith('gpt-') or path.startswith('claude-'):
                matches.append((path, 'ad-hoc scratch markdown at repo root'))
    return matches


def lint(args):
    canonical_topics, aliases = load_topic_governance()
    pages = sorted(p for p in TREE_DIR.glob('*.md') if p.name not in SPECIALS)

    incomplete = []
    invalid_subject = []
    uncanonical_topics = {}
    cache_stale = []
    # New schema distribution (current facet schema)
    kind_counts = {}
    form_counts = {}
    source_types_new_counts = {}
    # Schema drift detector — legacy/mixed schema = drift signal (alias phase ended)
    schema_counts = {}  # 'new' / 'legacy' / 'mixed' / 'unknown'
    mixed_schema_pages = []  # (page_name, reason) — drift signal
    bom_files = []
    legacy_drift = []
    language_candidates = []  # list of (page_name, line_no, kind)
    output_quality_findings = []  # list of (page_name, line_no, kind, match)
    leaf_depth_findings = []  # list of (page_name, line_no, kind, match)

    for p in pages:
        fm, has_bom = parse_frontmatter(p)
        if has_bom:
            bom_files.append(p.name)

        if fm is None:
            incomplete.append((p.name, 'no valid frontmatter'))
            continue

        # 3a frontmatter completeness — new schema only (alias phase ended 2026-05-18).
        # Legacy schema (type/role/source-type) is now an error — surfaced as incomplete
        # so the user runs the migration script.
        schema = detect_schema(fm)
        schema_counts[schema] = schema_counts.get(schema, 0) + 1

        if schema == 'mixed':
            mixed_schema_pages.append(
                (p.name, 'kind+role or type+form fields coexist — drift signal'))
            incomplete.append(
                (p.name, 'mixed schema (legacy+new fields) — convert to kind/form/source-types'))
            continue

        if schema == 'legacy':
            incomplete.append(
                (p.name, 'legacy schema (type/role/source-type) — convert to kind/form/source-types'))
            continue

        if schema == 'unknown':
            incomplete.append(
                (p.name, 'no schema fields (need kind / form / source-types)'))
            continue

        # New schema (current facet schema): kind, form, source-types
        common_required = ['topics', 'subject', 'domains', 'created', 'updated']
        new_required = common_required + ['kind', 'form', 'source-types']
        missing = [f for f in new_required if f not in fm]
        if missing:
            incomplete.append((p.name, f'missing: {missing}'))
            continue
        if fm['kind'] not in KINDS:
            incomplete.append((p.name, f'invalid kind: {fm["kind"]}'))
        if fm['form'] not in FORMS:
            incomplete.append((p.name, f'invalid form: {fm["form"]}'))
        # source-types is a list; each value must be in enum
        source_types_list = parse_list_value(fm['source-types'])
        for st in source_types_list:
            if st and st not in SOURCE_TYPES_NEW:
                incomplete.append((p.name, f'invalid source-types value: {st}'))
        # 3e distribution
        kind_counts[fm['kind']] = kind_counts.get(fm['kind'], 0) + 1
        form_counts[fm['form']] = form_counts.get(fm['form'], 0) + 1
        for st in source_types_list:
            if st:
                source_types_new_counts[st] = source_types_new_counts.get(st, 0) + 1

        # 3b subject tree validation
        subject = parse_list_value(fm['subject'])
        if not subject:
            incomplete.append((p.name, 'empty subject (must have >= 1 path)'))
            continue
        for sp in subject:
            err = validate_subject_path(sp)
            if err:
                invalid_subject.append((p.name, err))

        # 3g legacy collection drift
        for sp in subject:
            top = sp.split('/')[0]
            if top in LEGACY_TAGS:
                legacy_drift.append((p.name, f'legacy tag in subject: {sp}'))

        # 3c topic canonical
        topics = parse_list_value(fm['topics'])
        for t in topics:
            if t and t not in canonical_topics and t not in aliases:
                uncanonical_topics.setdefault(t, []).append(p.name)

        # 3d domain cache freshness
        domains_stored = parse_list_value(fm['domains'])
        domains_derived = derive_domains(subject)
        if domains_stored != domains_derived:
            cache_stale.append((p.name, fm.get('domains', ''), str(domains_derived)))

        # 3h language-shape review candidates
        for line_no, kind in find_language_shape_candidates(p):
            language_candidates.append((p.name, line_no, kind))

        for line_no, kind, match in find_output_quality_findings(p):
            output_quality_findings.append((p.name, line_no, kind, match))

        # 3k leaf-depth guard (warn-only)
        for line_no, kind, match in find_leaf_depth_findings(p, fm['form']):
            leaf_depth_findings.append((p.name, line_no, kind, match))

    rings_em_dash_debt = 0
    for p in sorted(TREE_DIR / name for name in OUTPUT_QUALITY_SPECIALS):
        if not p.exists():
            continue
        if p.name == 'rings.md':
            rings_em_dash_debt = count_historical_rings_em_dash(p)
            findings = find_rings_output_quality_findings(p)
        else:
            findings = find_output_quality_findings(p)
        for line_no, kind, match in findings:
            output_quality_findings.append((p.name, line_no, kind, match))

    # ---------------------------------------------------------------------
    # Report
    # ---------------------------------------------------------------------
    print(f'## Ontology validation report — {len(pages)} pages')
    print()

    print(f'### 3a Frontmatter incomplete: {len(incomplete)}')
    for name, reason in incomplete[:15]:
        print(f'  {name}: {reason}')
    if len(incomplete) > 15:
        print(f'  ... +{len(incomplete) - 15} more')
    if not incomplete:
        print('  OK')
    print()

    print(f'### 3b Subject tree drift: {len(invalid_subject)}')
    for name, err in invalid_subject[:15]:
        print(f'  {name}: {err}')
    if not invalid_subject:
        print('  OK — all subjects canonical')
    print()

    total_uncanon = sum(len(v) for v in uncanonical_topics.values())
    print(f'### 3c Topic uncanonicalized: {total_uncanon} mentions across {len(uncanonical_topics)} topics')
    promotion_candidates = [t for t, v in uncanonical_topics.items() if len(v) >= 3]
    for t, plist in sorted(uncanonical_topics.items(), key=lambda x: -len(x[1]))[:15]:
        flag = ' [promotion candidate]' if len(plist) >= 3 else ''
        print(f'  {t}: {len(plist)} pages{flag}')
    if not uncanonical_topics:
        print('  OK — all topics canonical or aliased')
    if promotion_candidates:
        print(f'  -> {len(promotion_candidates)} promotion candidates: {promotion_candidates}')
    print()

    print(f'### 3d Domain cache stale: {len(cache_stale)}')
    for name, stored, derived in cache_stale[:15]:
        print(f'  {name}: stored={stored} -> derived={derived}')
    if not cache_stale:
        print('  OK — all caches fresh')
    print()

    # New schema distributions (post-2026-05-18)
    print('### 3e Kind distribution (new schema)')
    for k in KINDS:
        c = kind_counts.get(k, 0)
        marker = '   ' if c > 0 else ' (unused)'
        print(f'  {k:14s} {c:4d}{marker}')
    print()
    print('### 3e Form distribution (new schema)')
    for f in FORMS:
        c = form_counts.get(f, 0)
        marker = '   ' if c > 0 else ' (unused)'
        print(f'  {f:6s} {c:4d}{marker}')
    print()
    print('### 3e Source-types distribution (new schema, multi-value)')
    for s in SOURCE_TYPES_NEW:
        c = source_types_new_counts.get(s, 0)
        marker = '   ' if c > 0 else ' (unused)'
        print(f'  {s:14s} {c:4d}{marker}')
    print()

    # 3i Schema drift detector (alias phase ended 2026-05-18 — legacy/mixed = drift)
    total_schema = sum(schema_counts.values())
    new_count = schema_counts.get('new', 0)
    legacy_count = schema_counts.get('legacy', 0)
    mixed_count = schema_counts.get('mixed', 0)
    unknown_count = schema_counts.get('unknown', 0)

    print('### 3i Schema integrity (drift detector)')
    print(f'  new schema:    {new_count:4d}')
    print(f'  legacy schema: {legacy_count:4d}  (must be 0; if >0, convert pages to the new schema)')
    print(f'  mixed (drift): {mixed_count:4d}  (must be 0; surface for manual fix)')
    print(f'  unknown:       {unknown_count:4d}')
    if mixed_schema_pages:
        print('  Mixed-schema pages (drift signal):')
        for name, reason in mixed_schema_pages[:15]:
            print(f'    {name}: {reason}')
        if len(mixed_schema_pages) > 15:
            print(f'    ... +{len(mixed_schema_pages) - 15} more')
    print()

    print(f'### 3f BOM-prefixed files: {len(bom_files)}')
    for name in bom_files[:15]:
        print(f'  {name}')
    if not bom_files:
        print('  OK — all UTF-8 no-BOM')
    print()

    print(f'### 3g Legacy collection drift: {len(legacy_drift)}')
    for name, err in legacy_drift[:10]:
        print(f'  {name}: {err}')
    if not legacy_drift:
        print('  OK — no legacy tags in subjects')
    print()

    print(f'### 3h Language-shape review candidates: {len(language_candidates)} lines')
    print('  (false positive expected — manual review per docs/CONVENTIONS.md § Naming)')
    # group by page for readability
    by_page = {}
    for name, line_no, kind in language_candidates:
        by_page.setdefault(name, []).append((line_no, kind))
    pages_with_candidates = sorted(by_page.items(), key=lambda x: -len(x[1]))
    for name, items in pages_with_candidates[:15]:
        kind_summary = {}
        for _, k in items:
            kind_summary[k] = kind_summary.get(k, 0) + 1
        summary = ', '.join(f'{c} {k}' for k, c in kind_summary.items())
        sample_lines = ', '.join(str(ln) for ln, _ in items[:5])
        more = f' (+{len(items) - 5} more)' if len(items) > 5 else ''
        print(f'  {name}: {summary}; lines {sample_lines}{more}')
    if len(pages_with_candidates) > 15:
        print(f'  ... +{len(pages_with_candidates) - 15} more pages')
    if not language_candidates:
        print('  OK — no candidates')
    print()

    print(f'### 3j Output quality contract guard: {len(output_quality_findings)} lines')
    print('  (mixed severity: em dash blocking; other deterministic body findings warn-only)')
    if (TREE_DIR / 'rings.md').exists():
        print(f'  rings.md historical intentional debt: {rings_em_dash_debt} U+2014 occurrences')
    by_page_quality = {}
    for name, line_no, kind, match in output_quality_findings:
        by_page_quality.setdefault(name, []).append((line_no, kind, match))
    pages_with_quality = sorted(by_page_quality.items(), key=lambda x: -len(x[1]))
    for name, items in pages_with_quality[:20]:
        kind_summary = {}
        for _, k, _ in items:
            kind_summary[k] = kind_summary.get(k, 0) + 1
        summary = ', '.join(f'{c} {k}' for k, c in kind_summary.items())
        samples = '; '.join(f'line {ln}: {match}' for ln, _, match in items[:3])
        more = f' (+{len(items) - 3} more)' if len(items) > 3 else ''
        print(f'  {name}: {summary}; {samples}{more}')
    if len(pages_with_quality) > 20:
        print(f'  ... +{len(pages_with_quality) - 20} more pages')
    if not output_quality_findings:
        print('  OK — no deterministic output-quality findings')
    print()

    print(f'### 3k Leaf-depth guard: {len(leaf_depth_findings)} findings')
    print('  (warn — form=prose leaf 깊이 proxy: 본문 wikilink 0 또는 thin body. 진짜 판정은 작성 시점 self-check)')
    by_page_depth = {}
    for name, line_no, kind, match in leaf_depth_findings:
        by_page_depth.setdefault(name, []).append((line_no, kind, match))
    for name, items in sorted(by_page_depth.items(), key=lambda x: -len(x[1]))[:20]:
        summary = ', '.join(kind for _, kind, _ in items)
        print(f'  {name}: {summary}')
    if len(by_page_depth) > 20:
        print(f'  ... +{len(by_page_depth) - 20} more pages')
    if not leaf_depth_findings:
        print('  OK — no leaf-depth warnings')
    print()

    # ---------------------------------------------------------------------
    # § 7 Non-tree scratch dirt (warn only, non-blocking)
    # ---------------------------------------------------------------------
    non_tree_dirt = find_non_tree_dirt(NAITE_ROOT)
    print(f'### 7 Non-tree scratch dirt: {len(non_tree_dirt)} tracked entries')
    print('  (warn — agent/IDE scratch tracked in naite vault, see care-check.md § 7)')
    if non_tree_dirt:
        # group by reason
        by_reason = {}
        for path, reason in non_tree_dirt:
            by_reason.setdefault(reason, []).append(path)
        for reason, paths in sorted(by_reason.items(), key=lambda x: -len(x[1])):
            print(f'  {reason}: {len(paths)} entries')
            for p in paths[:5]:
                print(f'    {p}')
            if len(paths) > 5:
                print(f'    ... +{len(paths) - 5} more')
        print('  recommended: add path to .gitignore + `git rm --cached <path>` + commit')
    else:
        print('  OK — no scratch dirt tracked')
    print()

    # ---------------------------------------------------------------------
    # Repair operations (only with explicit flag)
    # ---------------------------------------------------------------------
    if args.strip_bom and bom_files:
        print(f'### Stripping BOM from {len(bom_files)} files...')
        for name in bom_files:
            p = TREE_DIR / name
            raw = p.read_bytes()
            if raw.startswith(BOM):
                p.write_bytes(raw[len(BOM):])
        print(f'  Stripped BOM from {len(bom_files)} files.')

    if args.refresh_domains and cache_stale:
        print(f'### Refreshing domain cache for {len(cache_stale)} pages')
        for name, _stored, _derived in cache_stale:
            p = TREE_DIR / name
            fm, _ = parse_frontmatter(p)
            new_domains = '[' + ', '.join(derive_domains(parse_list_value(fm['subject']))) + ']'
            text = p.read_text(encoding='utf-8-sig')
            new_text = re.sub(r'(?m)^domains:.*$', f'domains: {new_domains}', text, count=1)
            p.write_bytes(new_text.encode('utf-8'))  # explicit LF (write_text emits CRLF on Windows)
            print(f'  {name}: domains -> {new_domains}')
        cache_stale.clear()

    body_em_dash = any(kind == 'em-dash' for _, _, kind, _ in output_quality_findings)
    blocking = bool(incomplete or invalid_subject or cache_stale or legacy_drift or body_em_dash)
    return 1 if blocking else 0


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser()
    parser.add_argument('--strip-bom', action='store_true',
                        help='Normalize BOM-prefixed files to UTF-8 no-BOM in-place')
    parser.add_argument('--refresh-domains', action='store_true',
                        help='Rewrite stale domains: cache in place from each page subject paths')
    args = parser.parse_args()
    sys.exit(lint(args))


if __name__ == '__main__':
    main()
