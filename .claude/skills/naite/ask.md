# /naite ask

Answer a question from the tree. Cite pages. Offer to file the answer.

## 언제 켜는가 (그리고 언제 켜지 않는가)

이 절차는 **tree 내용 (개념·entity·decision·source·rings·trunk·page) 의 조회나 추론이 필요한 질문**, 또는 사용자가 명시적으로 `/naite ask` 를 호출했을 때만 실행한다.

정체성·말투·선호·라우팅·단순 operational 질문 ("너는 누구야?", "네 역할이 뭐야?", "어떻게 답해?") 은 `/naite ask` 로 처리하지 않는다. tree 를 읽지 말고, `CLAUDE.md § 기본 정체성과 라우팅` 과 `SOUL.md § 보이는 정체성과 런타임` 의 기본 정체성으로 바로 답한다.

## Workflow

### 1. Grasp the index once, then answer from what you know — read page bodies only on demand

The tree **index** tells you what the tree covers. It is small and cheap. Read it **once, early** in a conversation — in a continuing thread it is already in your context, so do **not** re-read it:

- `tree/trunk.md` — the map: domains, hub pages, one-line summaries. This is the primary index.
- For status / progress questions ("오늘 뭘 공부할까", "뭐가 진행 중이지", "다음은 뭐야", "최근 활동") also read the **recent tail of `tree/rings.md`** (it is append-chronological — the newest entries are at the bottom; read the tail, not the whole file). Use `.naite/ontology/subject-tree.md` or `.naite/ontology/tree-manifest.json` only when you specifically need the subject structure or per-domain counts.

Then **answer from the index plus your own knowledge.** You are a capable model — for navigational questions, overviews, recommendations, and any topic the index shows the tree already covers, reason from the map and your own understanding, and cite the relevant pages by `[[slug]]` (you know the slugs from the index). This is the **fast default and it is enough for most asks.**

**Open an individual page's body only when the answer genuinely needs its specifics** — an exact definition, number, or wording the tree recorded; the actual content to compare what two pages say; or detail the index and your own knowledge don't already give. Then read just those pages, following `[[wikilinks]]` only as far as the answer actually uses. Never open a page "to be safe".

Speed comes from **reading the index once and reasoning from it**, not from re-spelunking files every turn — and from keeping the model and effort steady across a conversation so the session's prompt cache stays warm (do not switch engine per question). This grounding is internal work: never narrate it in the answer ("trunk.md 를 먼저 읽겠습니다", 후보 페이지 목록). See `SOUL.md § 응답 스타일`.

### 1b. Completeness questions — enumerate, don't estimate

"몇 개야", "전부 나열해", "빠짐없이 보여줘", "어떤 것들이 있어" 류의 **열거 질문**은 index 를 훑어 답을 추정하는 위의 기본 경로로 처리하지 않는다. 하나라도 빠지면 답이 틀리기 때문에, 완전성을 증거로 확보하는 절차를 순서대로 따른다:

1. **문자 검색 먼저.** `grep` 으로 tree 전체에서 후보를 뽑는다. 정확한 slug, 키워드, frontmatter 값을 문자 그대로 훑어 명백한 항목부터 확보한다.
2. **의미 검색을 여러 번.** 같은 개념의 다른 표현, 동의어, 상위어와 하위어로 질의를 바꿔가며 여러 차례 찾는다. 한 번의 질의로 끝내지 않는다. 문자 검색이 놓친, 다르게 표기된 항목을 여기서 건진다.
3. **중복 제거 표.** 두 경로에서 모인 후보를 한 표에 모아 같은 항목의 중복을 접는다. 각 항목의 slug 와 근거(어느 검색에서 나왔는지)를 표에 남긴다.
4. **재검증.** 최종 목록의 각 항목이 실제로 질문 조건에 맞는지 페이지로 되짚어 확인하고, 빠졌을 만한 이웃(inbound/outbound 링크, 같은 subject 의 페이지)을 한 번 더 훑어 누락을 점검한다.

이 절차의 목적은 속도가 아니라 완전성이다. 열거 질문에 index 추정만으로 답하면 조용히 항목을 빠뜨리게 된다. 이 네 단계는 내부 작업이므로 답변 본문에 과정으로 서술하지 않고, 완성된 목록만 사용자에게 보인다. (계보: honcho, plastic-labs/honcho AGPL @4f9a413. 개념만 증류했고 코드는 복사하지 않았다.)

### 2. If the index shows the tree is silent

If nothing in the index (trunk, and the pages it points to) touches the question:
- Say so explicitly ("nothing in the tree covers this yet").
- Offer two options:
  1. Answer from general knowledge, clearly labeled as outside-tree.
  2. Suggest a source to grow first (if the user has one in mind).

Do **not** silently answer from general knowledge as if it were tree-grounded. That corrupts the tree's value proposition.

**Current or time-sensitive external facts need the web, not stale memory.** If the question turns on something recent or live — today's or the latest updates, current versions, release news, prices, "오늘 기준", "최신", "요즘", "방금 나온" — neither the tree nor your own training knowledge is current. Use the web search tool to fetch the actual current facts first, then answer and label the web-sourced parts as outside-tree. Never answer a "what changed today / latest version" question from memory as if it were current; that silently ships stale claims dressed as fact.

### 3. Synthesize

Write the answer as the finished, user-facing result, not a log of how it was found. Voice and format (this is the working copy of `SOUL.md § 응답 스타일` — follow it inline, no need to open SOUL.md for a normal answer): **존댓말** by default (English if the user writes in English); **no emoji, no em-dash (`—`), no process narration, no meta-preamble, no naite-internal jargon** ("나무 기준", "개인 hub", "/naite ask 절차"). **Open with the answer itself — never a thinking or transition sentence** ("이제 답하겠습니다", "좋은 질문입니다", "Now I have solid grounding. Let me answer."); those belong in the collapsed thinking lane, and an English meta-sentence must never leak into the first line of a Korean answer. **Do not wrap the answer body in a ```markdown code fence** — the app renders it as markdown, so a fence would show the reader raw symbols.

**Use markdown actively — this is a rendered document, not a chat blob:**
- Any answer longer than two paragraphs gets `##`/`###` headings that name its sections. Do not pour long prose without structure.
- Wrap identifiers, commands, file names, terms of art, and values in **inline code** (`` `like-this` ``). Code or command blocks get a language-tagged fence.
- Comparisons → GFM table. Enumerations → lists. Quoted source lines → blockquote.
- Promote the single key takeaway to a callout when the answer teaches or warns: GFM alert syntax only (`> [!IMPORTANT]` / `[!TIP]` / `[!WARNING]`; also `[!NOTE]` / `[!CAUTION]`), one or two per answer, never one per paragraph.

- **Citations** as `[[page-slug]]`, placed **only at the end of the sentence or clause** the page supports — a trailing source marker. **Never open a sentence with a citation**; if a reference wants to lead, bold the sentence's key phrase instead and move the citation to the end. Natural inline wikilinks (mentioning a concept by name mid-sentence) are fine. Reuse the same `[[slug]]` for the same page.
- **Conflicts surfaced**: if two tree pages disagree, quote both and flag the disagreement.
- **Gaps named**: if the answer depends on something the tree doesn't yet cover, say so and consider proposing a stub.

### 4. Offer to file

At the end of any non-trivial answer, ask:

> This looks like it's worth keeping. File as a tree page? Proposed: `[[<slug>]]` under domain `<x>`, kind `<concept|entity|source-record|decision|insight|comparison|project|essay|personal>`.

If the user accepts:
- Create `tree/<slug>.md` with full ontology frontmatter (5 facets + cached domains) per `docs/CONVENTIONS.md § Ontology`. `subject` 는 `.naite/ontology/subject-tree.md` 의 path 1개 (cross-domain 진짜일 때만 multi). `source-types` 는 거의 항상 `[conversation]` (ask 가 대화에서 발생) — 단 ask 가 외부 자료를 cite 한 답이면 `[paper]` / `[article]` / `[docs]` / `[book]` / `[external]` 사용 가능, multi-source 일 때 list 로 합쳐 `[conversation, paper]` 같이 표현. Page-shape 이 A-vs-B 비교면 `kind: comparison`, 결정 thread 면 `kind: decision` (decision page 는 파일명 `decision-YYYY-MM-DD-<slug>.md` 형식). `form` 은 거의 항상 `prose` (ask 산출물은 산문). Page provenance ("from an ask, not a grow") 는 본문 첫 paragraph 또는 `## Provenance` 헤딩에 prose 로.
- Rewrite the answer as a page body that passes `docs/CONVENTIONS.md § Study-note quality dimensions` and `§ Page-kind quality contracts`; do not paste a conversational answer unchanged. Make the H hierarchy expose the reasoning sequence, keep examples and formulas interpretable, clean up citations so they become load-bearing `[[...]]` links or source-record provenance, and preserve uncertainty from the answer.
- **Update `tree/trunk.md` only if the new page is a hub candidate** (likely to receive multiple inbound links). hub 자격 없으면 trunk 미등재 (`docs/CONVENTIONS.md § trunk.md discipline` 참조).
- Append to `tree/rings.md`:
  ```
  ## [YYYY-MM-DD] ask-filed | <topic>
  - filed: [[new-slug]]
  - subject: <path>  (.naite/ontology/subject-tree.md 참조, cross-domain 일 때만 복수)
  - cited: [[a]], [[b]], [[c]]
  ```
- **Filing a page is a tree mutation, so the same post-write duties apply as `grow`/`ingest`** (`docs/CONVENTIONS.md § Output quality contract`, `§ Study-note quality dimensions`, `§ Page-kind quality contracts`, `docs/CONTEXT.md § Verification checklist`): self-check the selected kind's claim spine and the four study-note axes, run the content guard on the new page body (no raw/source-process voice, self-contained prose), then rebuild the generated maps that the new page changed — `python .naite/scripts/build-tree-manifest.py` (new page + coordinates) and, if it links to or from other pages, `python .naite/scripts/build-tree-dependencies.py`. Skipping this leaves the maps stale and the next orphan/inbound calculation wrong.

If the user declines, do not write anything. The conversation stands.

### 5. Update an existing page, optionally

If the ask produced material new content that belongs in an existing page (e.g. clarified trade-offs on `[[k-means]]`), propose an edit to that page instead of a new one. The same log entry applies, just with `- updated:` instead of `- filed:`.

## What this command never does

- Never answers a tree question without at least grasping `trunk.md` (the index) — but grasping the index once is enough; it does not require reading every candidate page.
- Never opens a tree page whose content the answer doesn't actually use. The index is the default; page bodies are on demand.
- Never re-reads the index or `SOUL.md` on a follow-up turn when they are already in the conversation's context.
- Never writes to the tree without explicit user consent.
- Never mixes tree-grounded and out-of-tree claims without labeling which is which.
- Never commits to git.
