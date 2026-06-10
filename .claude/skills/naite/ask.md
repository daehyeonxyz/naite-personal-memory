# /naite ask

Answer a question from the tree. Cite pages. Offer to file the answer.

## Workflow

### 1. Ground in the tree

- Read `tree/trunk.md` in full. This is the cheap way to find relevant pages without grepping the whole repo.
- Identify candidate pages from trunk entries and one-line summaries.
- Read each candidate page. If the question crosses domains, follow `[[wikilinks]]` between pages.

### 2. If the tree is silent

If no page touches the question:
- Say so explicitly ("nothing in the tree covers this yet").
- Offer two options:
  1. Answer from general knowledge, clearly labeled as outside-tree.
  2. Suggest a source to grow first (if the user has one in mind).

Do **not** silently answer from general knowledge as if it were tree-grounded. That corrupts the tree's value proposition.

### 3. Synthesize

Write the answer with:

- **Citations inline** as `[[page-slug]]`.
- **Conflicts surfaced**: if two tree pages disagree, quote both and flag the disagreement.
- **Gaps named**: if the answer depends on something the tree doesn't yet cover, say so and consider proposing a stub.

Choose the output format based on the question:
- Narrative prose for an explanation.
- A table for a comparison.
- A short list for a lookup.

### 4. Offer to file

At the end of any non-trivial answer, ask:

> This looks like it's worth keeping. File as a tree page? Proposed: `[[<slug>]]` under domain `<x>`, kind `<concept|entity|source-record|decision|insight|comparison|project>`.

If the user accepts:
- Create `tree/<slug>.md` with full ontology frontmatter (5 facets + cached domains) per `CONVENTIONS.md § Ontology`. `subject` 는 `ontology/subject-tree.md` 의 path 1개 (cross-domain 진짜일 때만 multi). `source-types` 는 거의 항상 `[conversation]` (ask 가 대화에서 발생) — 단 ask 가 외부 자료를 cite 한 답이면 `[paper]` / `[article]` / `[docs]` / `[book]` / `[external]` 사용 가능, multi-source 일 때 list 로 합쳐 `[conversation, paper]` 같이 표현. Page-shape 이 A-vs-B 비교면 `kind: comparison`, 결정 thread 면 `kind: decision` (decision page 는 파일명 `decision-YYYY-MM-DD-<slug>.md` 형식). `form` 은 거의 항상 `prose` (ask 산출물은 산문). Page provenance ("from an ask, not a grow") 는 본문 첫 paragraph 또는 `## Provenance` 헤딩에 prose 로.
- Paste the answer as the page body (clean up citations — they become `[[...]]` to internal pages, not to this conversation).
- **Update `tree/trunk.md` only if the new page is a hub candidate** (likely to receive multiple inbound links). hub 자격 없으면 trunk 미등재 (`CONVENTIONS.md § trunk.md discipline` 참조).
- Append to `tree/rings.md`:
  ```
  ## [YYYY-MM-DD] ask-filed | <topic>
  - filed: [[new-slug]]
  - subject: <path>  (ontology/subject-tree.md 참조, cross-domain 일 때만 복수)
  - cited: [[a]], [[b]], [[c]]
  ```

If the user declines, do not write anything. The conversation stands.

### 5. Update an existing page, optionally

If the ask produced material new content that belongs in an existing page (e.g. clarified trade-offs on `[[k-means]]`), propose an edit to that page instead of a new one. The same log entry applies, just with `- updated:` instead of `- filed:`.

## What this command never does

- Never answers without first reading `trunk.md`.
- Never writes to the tree without explicit user consent.
- Never mixes tree-grounded and out-of-tree claims without labeling which is which.
- Never commits to git.
