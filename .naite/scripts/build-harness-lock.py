#!/usr/bin/env python3
"""Build .naite/harness-lock.json — the harness file hash lock for /naite upgrade.

The lock records, at release time, the sha256 of every file the starter kit owns
(the "harness"). An installed vault carries the lock of its installed version.
`/naite upgrade` compares local file hashes against this lock to tell
"unmodified, safe to auto-replace" apart from "user-customized, propose 3-way".

Harness set (tracked and nonignored files):
    CLAUDE.md, AGENTS.md, SOUL.md, README.md, LICENSE, .gitignore,
    .claude/**, .agents/**, .claude-plugin/**, docs/**, .naite/scripts/**,
    .naite/templates/**, .naite/hooks/**

Excluded (user-owned or generated, never overwritten by upgrade):
    roots/**, tree/**, .naite/ontology/**, .naite/reports/**,
    USER.md, MEMORY.md (gitignored, per-clone user state),
    .naite/harness-lock.json itself

Usage:
    python .naite/scripts/build-harness-lock.py          # rewrite the lock
    python .naite/scripts/build-harness-lock.py --check  # exit 1 if lock is stale
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

NAITE_ROOT = Path(__file__).resolve().parent.parent.parent
LOCK_PATH = NAITE_ROOT / '.naite' / 'harness-lock.json'
PLUGIN_PATH = NAITE_ROOT / '.claude-plugin' / 'plugin.json'
MARKETPLACE_PATH = NAITE_ROOT / '.claude-plugin' / 'marketplace.json'

HARNESS_FILES = ('CLAUDE.md', 'AGENTS.md', 'SOUL.md', 'README.md', 'LICENSE', '.gitignore')
HARNESS_DIR_PREFIXES = ('.claude/', '.agents/', '.claude-plugin/', 'docs/', '.naite/scripts/', '.naite/templates/', '.naite/hooks/')


def list_harness_files() -> list[str]:
    out = subprocess.run(
        ['git', '-C', str(NAITE_ROOT), '-c', 'core.quotePath=false',
         'ls-files', '--cached', '--others', '--exclude-standard'],
        capture_output=True, text=True, encoding='utf-8', check=True,
    ).stdout.splitlines()
    selected = []
    for path in out:
        if path in HARNESS_FILES or path.startswith(HARNESS_DIR_PREFIXES):
            selected.append(path)
    return sorted(selected)


def sha256_of(path: Path) -> str:
    # Normalize CRLF -> LF before hashing so git autocrlf settings on the
    # installing machine cannot masquerade as user customization.
    data = path.read_bytes().replace(b'\r\n', b'\n')
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def build_lock() -> dict:
    version = json.loads(PLUGIN_PATH.read_text(encoding='utf-8'))['version']
    # docs/VERSIONING.md declares plugin.json AND marketplace.json as the single
    # version source; enforce that they agree (nothing else cross-checked this).
    mkt_version = json.loads(MARKETPLACE_PATH.read_text(encoding='utf-8'))['plugins'][0]['version']
    if mkt_version != version:
        raise SystemExit(f'version mismatch: plugin.json={version} '
                         f'marketplace.json={mkt_version} — make them equal.')
    files = {p: sha256_of(NAITE_ROOT / p) for p in list_harness_files()}
    return {
        'schema_version': 1,
        'version': version,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'files': files,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true',
                        help='exit 1 if the committed lock does not match the working tree')
    args = parser.parse_args()

    lock = build_lock()

    if args.check:
        if not LOCK_PATH.exists():
            print('harness-lock: MISSING (.naite/harness-lock.json not found)')
            return 1
        current = json.loads(LOCK_PATH.read_text(encoding='utf-8'))
        stale = []
        if current.get('version') != lock['version']:
            stale.append(f"version: lock={current.get('version')} plugin={lock['version']}")
        for path, digest in lock['files'].items():
            if current.get('files', {}).get(path) != digest:
                stale.append(f'hash drift: {path}')
        for path in current.get('files', {}):
            if path not in lock['files']:
                stale.append(f'removed from harness: {path}')
        if stale:
            print(f'harness-lock: STALE ({len(stale)} finding(s))')
            for line in stale:
                print(f'  - {line}')
            return 1
        print(f"harness-lock: OK ({len(lock['files'])} files, v{lock['version']})")
        return 0

    # write_bytes with explicit LF (not write_text, which emits CRLF on Windows) so
    # the committed lock is byte-identical on every platform.
    LOCK_PATH.write_bytes((json.dumps(lock, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))
    print(f"wrote .naite/harness-lock.json ({len(lock['files'])} files, v{lock['version']})")
    return 0


if __name__ == '__main__':
    sys.exit(main())
