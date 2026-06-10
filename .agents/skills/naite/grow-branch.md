# /naite grow — branch 모드 (장기 과정)

장기 과정 학습 세션. 과목 하나·책 한 권·시리즈 하나 = 가지 (branch) 하나. 세션 시작부터 끝까지 상주하며 튜터/리마인드 모드로 진행하고, 서브챕터마다 tree에 페이지를 grow한다. grow 단발 모드가 단발성 학습 이벤트라면 branch 모드는 구조화된 **과목·책·시리즈 단위 작업**.

All data paths below resolve against **NAITE_ROOT** (the root of the naite vault). Sub-skill references resolve against **SKILL_DIR** (`<NAITE_ROOT>/.agents/skills/naite`). See `SKILL.md` for context.

## Context routing and role split

Read `CONTEXT.md` before any branch mutation. Branch work is source-heavy and contract-heavy, so `subchapter-note` and `backfill` should use the Reader / Writer / Verifier split from `CONTEXT.md` whenever the active tool surface supports it and the user has authorized delegation.

- **Reader** reads the lecture PDF, transcript, notes, rendered images, and current dialogue. It returns compact claims, concepts, examples, equations, handwriting insights, and candidate wikilinks.
- **Writer** reads this workflow, `CONVENTIONS.md`, generated maps, ontology files, style references, and the Reader chunk. It writes `course-*` pages and any autonomy A concept pages.
- **Verifier** runs content guard, rebuilds `ontology/tree-manifest.json` and `ontology/tree-dependencies.json`, checks touched pages, and surfaces inbound semantic dependents.

If separate agents are not available, run the same three phases sequentially in one session. Do not let the full source bundle displace this workflow's output contract from context.

## When to use

사용자가 **과목 단위 학습**을 시작·진행·마무리할 때. 신호:

- "X 과목 공부할게 / 정리할게", "MA101 선형대수 학습 시작", "이번 학기 X 복습"
- 분류·과목코드·syllabus·목차 스크린샷·강의자료 pdf를 함께 공유
- 이미 시작된 과목의 다음 챕터 자료 업로드
- "1.3 정리해줘", "Ch1 끝", "이 과목 다 끝났어"

### grow 단발 모드와의 구분

| | grow 단발 | grow branch |
|---|---|---|
| 단위 | 단발성 학습 이벤트 (논문 1편, 아티클 1편, 강의 1편) | 과목·책·시리즈 (10-20 챕터, 100+ 페이지) |
| 세션 | 1회 마무리 시점에 capture + ingest | 세션 전체 상주, 서브챕터마다 개별 ingest |
| 출력 | 보통 1~3개 페이지 | 과목 메타 + 챕터 메타 + 서브챕터 노트 (수십 페이지 누적) |
| 스테이징 | `roots/articles/` | `roots/courses/{slug}/` |

단발성인지 과목 단위인지 불명확하면 사용자에게 물음.

## Hard rules

- **Staging**: 강의자료 pdf/이미지는 `roots/courses/{slug}/` 아래 **정규화된 파일명**으로 staging. flat 구조.
- **Filename convention (tree pages)** — `CONVENTIONS.md § Naming` (lowercase-kebab-case, 영문) 준수:
  - 과목 메타: `course-{slug}-00-index.md` (`kind=source-record`, `form=index`)
  - 챕터 메타: `course-{slug}-ch{NN}-00-index.md` (`kind=source-record`, `form=index`)
  - 서브챕터 노트: `course-{slug}-ch{NN}-{SS}-{title-slug}.md` (`kind=source-record`, `form=prose`)
- **Output quality contract**: `CONVENTIONS.md § Output quality contract` 준수. 본문은 page 자체로 의미를 가져야 하며, raw/PDF/필기/source-processing 설명은 `## Source` 앞 본문에 쓰지 않는다. 필기·슬라이드 강조·예시는 본문 설명으로 흡수한다.
- **Slug**: 영소문자·숫자 **단일 토큰** (하이픈 금지 — 레벨 구분자 `-`와 충돌). 공식 과목코드 있으면 소문자화(`MA101` → `ma101`), 없으면 prefix+NNN 임의(`aa101`, `aa102`, ...). 과목 내내 고정, 이후 절대 변경 금지.
- **Subject**: branch 페이지는 그 과목·책·시리즈가 다루는 **콘텐츠 path 1개** (예: `[statistics]` 또는 더 narrow `[engineering-math/ode]`). 메타·챕터·서브챕터 모두 동일 단일 path 또는 narrower. Canonical tree: `ontology/subject-tree.md`. `course`, `course-{slug}` 같은 컬렉션 태그는 subject 에 절대 넣지 않는다 — `CONVENTIONS.md § Ontology` 참조. Branch 멤버십은 파일명 prefix `course-{slug}-*` 로 보장. `domains` 는 care --check 가 subject 의 top-level 을 cache.
- **Trunk 분리**: trunk.md 에는 과목 메타 1줄만 등록 (`## Branches § <institution>` 섹션). 챕터/서브챕터 발견 경로는 `course-{slug}-00-index.md § Chapters` → `course-{slug}-ch{NN}-00-index.md § Subchapters` drill-down. **trunk.md 에 서브챕터/챕터 절대 나열하지 않는다.**
- **Grow 단위**: **서브챕터 단위 즉시 페이지 작성**. 챕터 메타는 챕터 완료 시점에 일괄. **단 rings.md 에는 서브챕터마다 쓰지 않는다** — frontmatter `created`/`updated` 가 정보 운반. rings entry 는 `branch-chapter` 마무리 시점에 1줄 (subchapter 수만 명시), `branch-start`/`branch-finish` 도 1줄씩.
- **`ingest` 모듈 직접 호출 금지**: `ingest.md`는 "raw 파일 하나 → 여러 페이지"용 워크플로. branch 모드는 "대화 맥락 → 페이지 1개"라 구조 불일치. 단 **결과물 규격**(frontmatter, `trunk.md`·`rings.md` 업데이트 포맷)은 `ingest.md` 와 정합되게 맞춘다.
- **Raw 보존**: `roots/courses/{slug}/*.pdf`는 서브챕터 grow 시점에 `_archive/`로 옮기지 않는다. **과목 완료(`branch-finish`) 시점에 일괄 이동.** (이유: 여러 서브챕터에서 같은 pdf를 페이지 범위로 참조하므로 챕터 진행 중엔 원본이 살아있어야 함.)
- **유일한 archive**: `roots/courses/_archive/` 는 이 프로젝트 전체에서 **유일하게 존재하는 `_archive/` 디렉토리**다. `roots/articles/` 와 `roots/conversations/` 에는 archive layer 가 없다 (파일은 제자리 상주, `conversations/` 의 claim summary 만 grow 후 삭제). `CONVENTIONS.md § Post-grow handling` 참조.
- **학술 정보만**: syllabus/about에서 수업 시간, 교수명, 시험 일정, 평가 기준 등 행정 정보는 tree에 담지 않는다. 내용·범위·선후수 관계만.
- 기타 `AGENTS.md § Secrets & privacy`, `§ Obsidian co-editing` (operational gotchas), `CONVENTIONS.md § Schema evolution` 전부 그대로 적용.

## Schema autonomy

이 skill 은 `CONVENTIONS.md § Schema evolution` 의 graded autonomy 를 따른다. 요약:

- **Autonomy A (자율 추가)** — 사용자 confirm 없이 작성:
  - 새 일반 개념 페이지 (`[[bayes-theorem]]` 같은 추출 페이지). 입자도 가드 통과 필수 — `ontology/topics.md § Topic granularity guidance` (broad domain 도 page-specific 도 아닐 것).
  - 새 canonical topic — `ontology/topics.md § canonical_topics` 에 직접 append.
  - 명백한 topic alias (`cot ↔ chain-of-thought` 처럼 morphology 또는 well-known abbrev) — `ontology/topics.md § aliases` 에 직접 append.
- **Autonomy B (제안)** — 후보 추가 + summary 에 surface, 사용자가 다음 검토 사이클에 confirm/revert:
  - 새 subject narrower — `ontology/subject-tree.md § narrower:` 에 candidate append.
  - Subject rename / move (reparent) — altLabel 함께 제안.
- **Autonomy C (사용자 결정)** — LLM 절대 추가 금지:
  - 새 top-level domain, 새 enum 값 (`type` / `role` / `source-type`), 새 facet field, subject deprecation.

`subchapter-note` 와 `backfill` 양 모드 동일 적용. 차이는 표면화 방식 — active 는 takeaways 단계에서 surface, backfill 은 chapter-finish log 에서 surface. 입자도 검사 실패한 후보는 어떤 모드에서도 자율 추가 금지 — log 의 surface 항목으로만 남긴다.

## Sub-operations (auto-selected)

스킬 호출 시 **사용자 의도 + 현재 tree 상태**를 보고 아래 중 하나로 자동 분기. 분기 직전 **1줄로 사용자에게 확인** ("지금 {op} 맞지?"). 혼동되면 선택지 제시.

| Op | 트리거 | Tree 변경 |
|---|---|---|
| `start` | 신규 과목 시작. slug가 `tree/trunk.md § Branches` 어느 institution 섹션에도 없음 | 과목 메타 생성, trunk·rings 갱신 |
| `resume` | 기존 slug가 이미 존재 | 없음 (진행 상태만 요약) |
| `chapter-start` | 새 챕터 pdf 업로드, 챕터 시작 선언 | 없음 (staging + 맥락 세팅만) |
| `subchapter-note` | "1.3 정리해줘", "이 서브챕터 반영" | 서브챕터 노트 1개 생성 (+선택적 일반 개념 페이지). **rings.md 작성 없음.** |
| `chapter-finish` | "이 챕터 끝", 챕터 메타 요청 | 챕터 메타 생성, 과목 메타 갱신, rings 1줄 |
| `branch-finish` | "과목 끝", "학기 종강" | 과목 메타 상태 변경, raw archive, rings 1줄 |
| `stage-source` | start/chapter-start 밖에서 자료만 업로드됨 | 없음 (roots 쪽만 staging) |
| `backfill` | 사용자 학습 완료 과목 mass automation, `/naite grow backfill {slug}` 명시 호출 | chapter loop sweep — `grow-backfill.md § Workflow` 로 위임 |

## Workflow

### 0. Pre-flight (every invocation)

1. Read `<NAITE_ROOT>/AGENTS.md`.
2. Read `<NAITE_ROOT>/CONTEXT.md`.
3. If `<NAITE_ROOT>/ontology/tree-manifest.json` is missing or stale for the current task, run `python scripts/build-tree-manifest.py`.
4. Read `<NAITE_ROOT>/ontology/tree-manifest.json` before searching for existing course, concept, or entity pages.
5. Read `<NAITE_ROOT>/ontology/tree-dependencies.json` before changing existing course or concept pages when semantic dependents may need review. If missing, run `python scripts/build-tree-dependencies.py`.
6. Read `<NAITE_ROOT>/tree/trunk.md` — 특히 `## Branches` 섹션 (institution 그룹별 과목 메타 목록) 과 `## Knowledge domains § <domain>` 의 hub 페이지들.
7. Read last ~30 lines of `<NAITE_ROOT>/tree/rings.md` — 최근 `branch-*` 엔트리로 진행 상태 파악 (branch-note 는 더 이상 rings 에 없음 — frontmatter `updated` 또는 `course-{slug}-*` 파일 mtime 으로 파악).
8. Op 결정, 사용자에게 1줄 확인.

### A. `start` — 신규 과목

1. 사용자로부터 수집 (한번에 또는 단계적):
   - 분류 (예: "{대학·학과} 전공", "Anthropic Academy", "3Blue1Brown")
   - 과목코드 (있으면)
   - 과목명 (한글·영어 가능하면 둘 다)
   - 목차 (스크린샷 또는 텍스트)
   - syllabus / about (pdf, 텍스트, 또는 생략)
2. Slug 결정:
   - 과목코드 있음 → 소문자화. `MA101` → `ma101`.
   - 없음 → 기관 prefix + NNN 제안. `tree/trunk.md § Branches` 와 `roots/courses/` 디렉토리에서 기존 slug 확인 후 다음 번호.
   - slug는 반드시 단일 토큰 (영소문자·숫자, 하이픈 없음).
3. Staging: `roots/courses/{slug}/` 생성. 업로드 자료 복사 (`§ Staging rules` 참조).
4. Takeaways 논의 (3-8 bullet):
   - 이 과목이 다루는 범위·핵심 thread
   - **Subject path 결정**: `ontology/subject-tree.md` 의 path 1개 (예: `[statistics]` 또는 `[engineering-math/ode]`). 어느 path 에도 분류 곤란하면 사용자와 새 narrower 또는 top-level 도입 결정 후 `ontology/subject-tree.md` 갱신부터.
   - 기존 tree 개념 페이지와의 접점 (`[[probability]]` 있으면 메타 페이지에서 링크)
   - 유사 과목/선후수 관계
   사용자 확인 후 진행.
5. `tree/course-{slug}-00-index.md` 작성 (`kind=source-record`, `form=index`). 템플릿 `§ Templates § 과목 메타` 사용. frontmatter `subject` 는 단일 path; `domains` 는 빈 배열로 두면 care --check 가 cache 채움.
6. `tree/trunk.md` 업데이트:
   - `## Branches § <institution>` 섹션에 한 줄: `- [[course-{slug}-00-index]] — {과목명, 짧은 설명}`. institution 섹션이 없으면 신설.
   - **챕터/서브챕터는 절대 trunk 에 나열하지 않는다.** drill-down 으로 발견.
7. `tree/rings.md`:
   ```
   ## [YYYY-MM-DD] branch-start | course-{slug}
   - pages created: [[course-{slug}-00-index]]
   - subject: <path>  (ontology/subject-tree.md 참조)
   - staged: roots/courses/{slug}/<files>
   ```
8. Checkpoint: "과목 셋업 완료. 첫 챕터 자료 주면 `chapter-start` 로 넘어갈게."

### B. `resume` — 기존 과목 재개

1. `tree/course-{slug}-00-index.md` 읽음.
2. `grep "^## \[" tree/rings.md | grep "course-{slug}"` 로 진행 이력 파악 (branch-start, branch-chapter, branch-finish 만 보임).
3. 진행 상태 추론은 `course-{slug}-00-index.md § Chapters` 본문의 챕터 status + `course-{slug}-ch{NN}-00-index.md` 존재 여부 + 서브챕터 페이지 glob 으로.
4. 완료된 챕터 / 진행 중 / 남은 챕터를 **한 화면에 요약**.
5. 사용자에게 다음 의도 확인 ("새 챕터 시작? 특정 서브챕터 정리? 챕터 마무리?").
6. 파일 쓰지 않음. `rings.md`에도 쓰지 않음.

### C. `chapter-start` — 새 챕터 진입

1. 챕터 자료 업로드 확인. 기본 staging 이름: `roots/courses/{slug}/ch{NN}-lecture.pdf`. 기존 파일 있으면 덮어쓰기 전 사용자 확인.
2. PDF Read 혹은 텍스트 추출. 추출 품질이 나쁘면(스캔본·OCR 필요 등) **중단**하고 사용자에게 보고. `rings.md`에 `aborted` 엔트리 append.
3. 목차·서브챕터 리스트 파악. 사용자에게 "이 챕터 서브챕터는 {리스트} 맞지?" 확인.
4. 파일 쓰지 않음. 이 단계는 맥락 세팅만 (리마인드·설명은 이제부터 진행). `rings.md`에도 쓰지 않음 — 챕터 메타는 `chapter-finish` 에서만 작성.
5. 서브챕터 단위로 리마인드/설명. 사용자가 "정리해줘"류 신호를 보내면 `subchapter-note`로 전환.

### D. `subchapter-note` — 서브챕터 ingest (핵심 동작)

한 번에 **한 서브챕터만**.

**작성 전 필수 캘리브레이션 — 절대 생략 금지:**

a. **기존 서브챕터 노트 1개 읽기**: 같은 과목(`course-{slug}-ch*-[^0]*.md`)의 기존 서브챕터 노트 중 가장 최근 것 1개를 Read한다. 없으면 같은 domain의 다른 과목 서브챕터 노트를 읽는다. **이 페이지의 깊이·서술 방식·수식 포맷이 현재 작성의 최저 기준이다.** 기존 페이지보다 얕으면 안 된다.

b. **해당 섹션 PNG 전체 읽기**: `chapter-start`에서 PDF가 이미 스테이징된 경우라도, 서브챕터 노트 작성 시점에 **해당 섹션 슬라이드를 PNG로 렌더링해서 1장씩 Read한다.** 텍스트 추출만으로는 수식·필기·그래프가 누락된다. 렌더링 파이프라인은 `§ PDF rendering pipeline` 참조. 섹션 경계를 모를 때는 5장 먼저 렌더링 후 범위 확정.

c. **학생 필기 인사이트 수집**: PNG를 읽는 과정에서 학생 필기(형광펜 강조, 여백 메모, 수식 옆 주석, 한국어 해설)를 모두 기록한다. 이것은 이 학생이 중요하다고 판단한 부분이므로 페이지 본문에 반드시 반영한다. 단 본문에서 "필기에는", "노트에서는"처럼 source 를 직접 말하지 말고, 강조점과 직관을 해당 개념 설명으로 흡수한다.

1. 현재 대화에서 해당 서브챕터 관련 논의 추출 (질문·설명·예시·유도·사용자 반응).
2. `tree/trunk.md` 재확인 — 관련 기존 hub 컨셉 페이지가 있는지 (`[[laplace-transform]]`, `[[generative-ai]]` 등). `[[...]]` 연결 후보 수집.
3. 사용자에게 **takeaways 3-8 bullet** 제시 (`ingest.md § 4` 원칙 그대로):
   - 이 서브챕터에 담을 내용
   - **일반 개념 페이지 추출 후보** — 강의에서 등장한 개념 중 *재사용 가능한 입자도* 에 부합하는 것을 LLM 이 식별해 제시 (예: `Bayes' Theorem`, `chain-of-thought`). 기준: `ontology/topics.md § Topic granularity guidance` — broad domain 도 page-specific 도 아닐 것. `§ Schema autonomy` 의 autonomy A 권한으로 step 5 에서 자동 생성한다 — 사용자가 명시적으로 빼라고 하지 않는 한 진행.
   - 기존 페이지 **업데이트** 필요한 것 (예: 기존 `[[laplace-transform]]`에 이번 강의의 formulation을 추가)
   - 강의 내용에 **trade-off / 결정 / 실패 분석**이 들어가 있으면 서브챕터 노트와 별도로 `/naite fruit` 페이지로 분리할지 — `CONVENTIONS.md § Decision thread shape` 참조.
   사용자 확인 후 진행.
4. 서브챕터 노트 파일 작성:
   - 경로: `tree/course-{slug}-ch{NN}-{SS}-{title-slug}.md`
   - Frontmatter: `kind=source-record`, `form=prose`, `domains: []` (care --check 가 subject 에서 cache)
   - 본문: `§ Templates § 서브챕터 노트` 참조.
5. **일반 개념 페이지 자율 생성** (`§ Schema autonomy` autonomy A): step 3 에서 식별된 추출 후보 — 사용자가 명시적으로 빼라고 한 것을 제외 — 를 이 시점에 별도 Write. frontmatter 5 facet 은 `ingest.md § 5` 규격. `topics` / `subject` 는 `ontology/` canonical 우선; 미등록 새 topic 이 입자도 가드 통과하면 `ontology/topics.md § canonical_topics` 에 직접 append (autonomy A); 새 narrower 가 자연스러우면 `ontology/subject-tree.md § narrower:` 에 candidate append + chapter-finish rings 의 surface 항목으로 기록 (autonomy B). 새 일반 페이지가 hub 후보면 (다른 페이지에서 자주 link 받을 만하면) `trunk.md § Knowledge domains § <domain>` 의 "주요" 라인에 추가 검토.
6. `tree/trunk.md` 업데이트:
   - **서브챕터 노트는 trunk 에 등록하지 않는다.**
   - 새 일반 개념 페이지가 hub 자격이 있다면 `## Knowledge domains § <domain>` 의 "주요" 리스트에 한 줄 추가 (4-7개 한도 내에서).
   - 기존 hub 페이지의 요약이 본질적으로 바뀌면 한 줄 revise.
7. `tree/rings.md`: **작성 안 함.** frontmatter `created`/`updated` 가 정보 운반.
8. Content guard: 방금 쓴/수정한 페이지의 `## Source` 앞 body 를 `/naite care § Content Guard` 기준으로 스캔하고, raw/source voice·불필요한 영어 generic heading·mojibake 를 즉시 고친다.
9. Rebuild generated maps:
   ```powershell
   python scripts/build-tree-manifest.py
   python scripts/build-tree-dependencies.py
   ```
10. Inspect `ontology/tree-dependencies.json` for inbound references to touched slugs. Surface semantic dependent candidates only; do not auto-rewrite them during `subchapter-note`.
11. Checkpoint: "반영 완료. 다음 서브챕터?"

### E. `chapter-finish` — 챕터 마무리

1. 해당 챕터 서브챕터 노트 전부 존재 확인 (glob `tree/course-{slug}-ch{NN}-*` 에서 `-00-index` 제외).
2. 누락 있으면 사용자 확인 — 의도적 스킵이면 진행, 실수면 해당 서브챕터 먼저 `subchapter-note`.
3. 챕터 메타 파일 작성: `tree/course-{slug}-ch{NN}-00-index.md` (`kind=source-record`, `form=index`). `§ Templates § 챕터 메타`. `domains` 는 care --check cache.
4. `tree/course-{slug}-00-index.md`의 Chapters 섹션 업데이트 (챕터 상태를 "완료"로, 요약 line refresh).
5. **trunk.md 갱신 없음** (챕터 메타는 course 메타에서만 발견 — trunk 직접 등록 안 함).
6. `tree/rings.md`:
   ```
   ## [YYYY-MM-DD] branch-chapter | course-{slug} Ch{NN} — {Chapter Title}
   - subchapters: N — {slug list}
   - source: roots/courses/{slug}/ch{NN}-lecture.pdf
   - drafter: {cowork | code | codex}
   ```
7. **Git commit (chapter = atomic unit, push 안 함)**:
   ```
   git add tree/course-{slug}-ch{NN}-*.md \
           tree/course-{slug}-00-index.md \
           tree/rings.md \
           ontology/tree-manifest.json \
           ontology/tree-dependencies.json \
           [해당 챕터에서 spawn 된 hub 페이지 슬러그] \
           [hub promotion 으로 trunk.md 변경된 경우 tree/trunk.md]
   git commit -m "course: {slug} ch{NN} — {Chapter Title} (drafter={cowork|code|codex})"
   ```
   - **Drafter tag** (필수): `cowork` (데스크톱 앱 Cowork 탭), `code` (CLI 또는 데스크톱 앱 Code 탭), `codex` (OpenAI Codex CLI). 사후 품질 비교·트래킹용 — `git log --grep "drafter=codex"` 같은 쿼리로 surface.
   - 한 commit = 한 챕터 (서브챕터 페이지 + 챕터 메타 + 과목 메타 갱신 + rings entry + 해당 챕터에서 spawn 된 일반 개념 페이지).
   - schema 파일·settings 같은 무관 변경은 staging 금지 — 별도 commit.
   - **Push 안 함** — `branch-finish` 시점에 누적 chapter commits + finish commit 이 한 번에 origin 으로.
   - 첫 챕터 commit 은 untracked `course-{slug}-00-index.md` (branch-start 산출물) 도 함께 staging.

### F. `branch-finish` — 과목 종료

1. `tree/course-{slug}-00-index.md` 상태 변경 (frontmatter `updated`, 본문 `상태: 완료 (YYYY-MM-DD)`).
2. `roots/courses/{slug}/` 전체를 `roots/courses/_archive/{slug}/`로 이동. `_archive/` 없으면 생성.
3. `tree/rings.md`:
   ```
   ## [YYYY-MM-DD] branch-finish | course-{slug}
   - chapters: N
   - subchapter pages: M
   - archived: roots/courses/_archive/{slug}/
   ```
4. **Git commit + push (과목 atomic 종료 + 원격 동기)**:
   ```
   git add tree/course-{slug}-00-index.md tree/rings.md roots/courses/_archive/{slug}/
   git add ontology/tree-manifest.json ontology/tree-dependencies.json
   git commit -m "course: {slug} — finished ({N} chapters, {M} pages)"
   git push origin main
   ```
   - 본 op 가 **자동 push trigger**. chapter-finish 는 local-only commit 이었고, 누적 chapter commits + 본 finish commit 이 한 번에 원격으로.
   - 현재 브랜치 확인: `main` 이 아니면 사용자에게 확인. 워크트리에서 진행 중이었으면 main 으로 merge/checkout 후 push.
   - Push 실패 (네트워크·인증·conflict) 시 사용자에게 보고하고 commit 까지는 보존. 자동 force-push 금지.

### G. `stage-source` — 자료 단독 스테이징

`start`/`chapter-start` 흐름에 포함되지만, 중간에 보조자료(필기, 보충 슬라이드)만 들어올 때 단독 호출.

1. 업로드 경로 확인 (`uploads/` 또는 사용자 제시 경로).
2. 정규화 파일명 결정 (`§ Staging rules`).
3. 복사 (bash `cp`; workspace 불가 시 정확한 경로·이름 제시하고 사용자에게 수동 복사 요청).
4. `rings.md`에 쓰지 않음 — roots 레이어 staging만이므로.

### H. `backfill` — Codex automation 모드

세부 워크플로는 `.agents/skills/naite/grow-backfill.md` 가 담당. 본 op 는 분기만 책임진다.

1. 트리거: 사용자가 `/naite grow backfill {slug}` 또는 `/naite grow start {slug} --mode=backfill` 호출. 자동 추론 안 함 — `§ 0 step 4` 의 op 결정 단계에서 사용자 입력으로 명시.
2. `§ A start` 의 step 1-3 (slug 결정, staging) 그대로 진행.
3. step 4-7 의 takeaways·dialogue 단계 **건너뛰기**. backfill 은 사용자 mental model 이 이미 안정된 콘텐츠 대상이므로 dialogue 가 페이지 가치에 기여하지 않는다. 다만 **`§ Schema autonomy` 의 autonomy A 는 그대로 적용** — 일반 개념 페이지 추출, canonical topic 추가, 명백한 alias 추가 모두 자율 진행 (입자도 가드 통과 시). autonomy B (narrower 제안) 는 candidate append + chapter-finish rings 의 surface 항목으로 기록, autonomy C 는 발견 시 rings 에 명시 후 사용자 결정 대기. backfill 의 "dialogue 생략" 은 *큐레이션 대화 생략*이지 *연결 생성 생략*이 아니다 — 일반 개념 페이지 추출이 빠지면 chapter silo 가 되어 graph 가 빈약해진다.
4. `grow-backfill.md § Workflow` 의 chapter loop 으로 위임.
5. 모든 chapter 완료 후 `branch-finish` 는 본 파일의 `§ F` 그대로 사용자 명시 승인 후 수행 (자동 push 포함).

backfill 모드는 `active` 모드 (`§ A`) 와 동시에 사용하지 않는다 — 학습 중 콘텐츠에 backfill 을 쓰면 dialogue takeaway 가 사라져서 페이지 가치가 떨어진다.

## Staging rules (`roots/courses/{slug}/`)

**flat** 구조. 한 챕터에 자료 3개 넘어가면 `/naite care --check`가 flag → nested 재구성 검토.

| 자료 종류 | 파일명 |
|---|---|
| Syllabus / about | `syllabus.pdf`, `syllabus.md` |
| 목차 스크린샷 | `toc.png` |
| 챕터 강의자료 | `ch{NN}-lecture.pdf` |
| 챕터 사용자 필기 | `ch{NN}-notes.pdf` |
| 챕터 교재 발췌 | `ch{NN}-textbook.pdf` |
| 챕터 슬라이드·보조자료 | `ch{NN}-slides.pdf`, `ch{NN}-handout.pdf` |

**원본 업로드명 자동 파싱**: `Ch1 Probability Theory.pdf` 같이 "Ch{N} {Title}" 구조면 `ch01-lecture.pdf`로 자동 변환. 파싱 실패하면 사용자에게 물음.

**Binary 복사**: PDF·이미지는 `Write` 도구로 못 씀 (텍스트 전용). `bash cp <src> <dst>`를 사용. workspace 불가 시 사용자에게 정확한 경로·파일명 제시하고 수동 복사 요청.

## External source folder access (선택)

강의자료가 클라우드 동기화 폴더 (OneDrive, Google Drive, Dropbox 등) 에 이미 정리돼 있으면, 사용자 업로드 없이 그 폴더에서 직접 staging 할 수 있다. 절차:

1. 사용자에게 원본 폴더 경로와 구조를 확인한다.
2. 파일 복사로 staging 한다 (원본은 절대 수정하지 않는다):
```powershell
Copy-Item "{원본 폴더}\{원본파일명}.pdf" "<NAITE_ROOT>\roots\courses\{slug}\ch{NN}-lecture.pdf"
```
3. 복사 완료 후 staging 경로(`roots/courses/{slug}/ch{NN}-lecture.pdf`)에서 렌더링. tree 페이지 Source 섹션에는 **staging 경로** 기록 (외부 원본 경로 아님 — 경로 누출 방지).

## PDF rendering pipeline (Read 도구가 PDF 를 직접 못 읽는 환경용)

환경에 따라 Read 도구가 PDF를 직접 읽지 못할 수 있다 (`pdftoppm` 미설치 등). 그 경우 PyMuPDF로 PNG 렌더링 후 Read하는 방식을 사용한다.

**전체 페이지 수 확인 + 렌더링** (NAITE_ROOT에서 실행):
```powershell
cd "<NAITE_ROOT>"
python -c "
import fitz
pdf = fitz.open(r'roots/courses/{slug}/ch{NN}-lecture.pdf')
print('Total pages:', len(pdf))
mat = fitz.Matrix(1.5, 1.5)   # 1.5x 배율 — 필기 판독 최적값
d = r'roots\assets'
for i in range(START, END):   # 0-indexed; 페이지 X → index X-1
    pdf[i].get_pixmap(matrix=mat).save(f'{d}\ch{NN}_p{i+1:02d}.png')
pdf.close()
print('done')
"
```

**Read 후 즉시 삭제**:
```powershell
Remove-Item "<NAITE_ROOT>\roots\assets\ch{NN}_p*.png" -Force
```

**운영 규칙**:
- PNG는 `roots/assets/`에 임시 — 서브챕터 노트 작성 완료 직후 삭제. git에 들어가면 안 됨.
- 한 번 렌더링 권장 범위: 5-15 페이지. 섹션 경계를 모를 때는 5-10장 먼저 렌더링해서 헤더 확인 후 범위 결정.
- 한 세션 적정 분량: 챕터 1개 (서브챕터 7-10개 기준). 컨텍스트 한계로 챕터 단위로 세션 분리 권장.

## Templates

### 과목 메타 (`course-{slug}-00-index.md`)

```markdown
---
kind: source-record
form: index
topics: []
subject: [<path-from-ontology/subject-tree.md>]
source-types: [course]
domains: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# {Course Title EN} ({과목코드 있으면})

## Also known as
- {한글 과목명}
- {영어 전체명}

## Overview

- **분류**: {예: {대학·학과} 전공, Anthropic Academy}
- **과목코드**: {MA101 또는 N/A}
- **상태**: 진행중 | 완료 (YYYY-MM-DD)
- **Staging**: `roots/courses/{slug}/`  (또는 완료 후 `roots/courses/_archive/{slug}/`)

## Scope

{이 과목이 다루는 범위·핵심 thread. prose 한두 단락, syllabus/about 기반. 학술 정보만.}

## Chapters

- [[course-{slug}-ch01-00-index|Ch1. {Title}]] — {one-line summary} (완료 | 진행중 | 예정)
- [[course-{slug}-ch02-00-index|Ch2. {Title}]] — ...
- ...

## Related

{prose로 인접 영역 연결. 예: "확률론 기초를 다루므로 [[probability]], [[conditional-probability]] 와 연결된다. [[statistical-inference]] 의 선수과목 역할."}
```

### 챕터 메타 (`course-{slug}-ch{NN}-00-index.md`)

```markdown
---
kind: source-record
form: index
topics: []
subject: [<과목과 동일 path 또는 narrower>]
source-types: [course]
domains: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# {과목코드} Ch{NN}. {Chapter Title}

## Subchapters

- [[course-{slug}-ch{NN}-01-{title}|{NN}.1 {Subchapter Title}]]
- [[course-{slug}-ch{NN}-02-{title}|{NN}.2 {Subchapter Title}]]
- ...

## Chapter summary

{챕터 전체 thread prose. 서브챕터 간 논리적 연결, 핵심 정리.}

## Maps to

- {위키 일반 개념 페이지 연결. 예: "이 챕터는 [[probability-theory]] 의 basics를 다룬다."}

## Source

- `roots/courses/{slug}/ch{NN}-lecture.pdf`  (과목 완료 후엔 `roots/courses/_archive/{slug}/ch{NN}-lecture.pdf`)
```

### 서브챕터 노트 (`course-{slug}-ch{NN}-{SS}-{title-slug}.md`)

**페이지 골격 — hard rules** (이 파일이 authoritative; 다른 skill 들은 이 섹션을 참조한다):

서브챕터 페이지의 H-tag 매핑은 강의의 자연 sub-division 을 그대로 따른다. tree 는 1 subchapter = 1 file 기준이므로, 1 chapter = 1 file 형태의 외부 노트의 H2 가 이 tree 에서는 페이지 자체 (H1) 에 해당한다.

- **H1**: subchapter 제목.
- **H2**: 강의의 그 subchapter 내부 자연 sub-division (큰 골자).
- **H3**: 그 골자 아래 개념 그룹.
- **H4**: 단일 개념·설명·공식·정리. 본문은 길이 제한 없이 충분한 설명 가능.
- H2/H3 아래 H4 없이 prose 만 두는 것도 필요시 OK (메타 설명·연결 문장).
- `---` 가 H2 사이 visual breakpoint.
- Korean prose by default. English headings/terms are allowed when they are course-native technical units; generic headings should be Korean (`CONVENTIONS.md § Output quality contract`).
- Frontmatter 5 facet 유지 (`CONVENTIONS.md § Ontology`).

**`## Source` 는 H2 규칙의 예외**: trailing provenance block. 파일 path 만 작성하고 page range 는 본문에 노출하지 않는다 — 페이지 범위는 backfill run-log 또는 commit message 에서 관리한다.

```md
## Source
- `roots/courses/_archive/{slug}/sessionNN-notes.pdf`
```

**원본 소스 참조 금지**: 본문 prose 가 원본 PDF 의 특정 페이지·위치·다이어그램을 가리키는 anchor 를 포함하지 않는다. 페이지 자체 + tree 의 인접 페이지로 self-contained 되어야 한다. 원본은 검토·보강 용도이지 본문 이해 의존물이 아니다.

**raw/필기/source-processing voice 금지**: `## Source` 앞 본문에는 roots 경로, PDF page, page range, staging, render, backfill, "필기에는", "강의 노트에는", "자료에서는", "이 페이지에서는" 같은 표현을 쓰지 않는다. 손필기와 시각 강조는 해당 개념 설명의 관점·직관·주의점으로 흡수한다.

**이미지 임베드**: default 안 함. load-bearing diagram 일 때만 예외.

**`## Core idea / ## Details / ## Also known as / ## Related` 같은 wiki-rubric 섹션 헤딩 안 만듦.** 그 정보들은 H4 prose 안에 자연스럽게 흐른다.

**Style reference (read-only)**: voice anchor 는 `tmp/style-reference/` 아래 manifest 가 관리. backfill / care sub-skill 이 manifest 가 있으면 참조, 없으면 manifest 의 fallback path 로 원본 노트를 read-only 로 참고. 어느 경우에도 tree 에 ingest 하지 않는다.

**작성 퀄리티 기준 — 이 수준 미만은 반려:**

- **공식 나열 금지**: 공식이 등장할 때는 반드시 (1) 유도 근거 또는 메커니즘, (2) 각 항이 의미하는 것, (3) 어떤 조건에서 성립하는지를 함께 쓴다. "E(X) = np" 한 줄만 쓰는 것은 퀄리티 미달.
- **앞 서브챕터·챕터와의 논리적 흐름**: 첫 H2 또는 opening prose 에서 "이 개념이 왜 필요한가 — 앞에서 뭘 다뤘고 이게 어디서 나오는가" 가 prose 안에 자연스럽게 드러난다. 별도 헤딩 아님.
- **필기 인사이트 통합**: 캘리브레이션 단계 c 에서 수집한 학생 필기 강조점을 해당 개념 H4 의 설명 prose 안에 자연스럽게 녹여 넣는다.
- **예시에 숫자 직접 계산**: 슬라이드 예시를 가져올 때 과정과 결과값을 실제로 쓴다.
- **유사·대비 개념 명시**: 이 개념과 혼동하기 쉬운 것·구조적으로 대응하는 것이 있으면 비교 prose 추가.
- **Korean alias 인라인**: 단일 alias 는 H4 정의 lead 안에 (`#### Bayes' theorem (베이즈 정리)`). 별도 `## Also known as` 섹션 만들지 않음.

```markdown
---
kind: source-record
form: prose
topics: []
subject: [<과목과 동일 path 또는 narrower>]
source-types: [course]
domains: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# {NN}.{SS} {Subchapter Title}

{optional opening prose — 이 subchapter 의 위치·맥락·앞 흐름과의 연결.}

## {first sub-division from lecture}

{optional H2 prose — 메타 설명·연결 문장.}

### {concept group}

#### {concept name} ({Korean alias if relevant})
정의 lead.
prose narrative 충분히 — 위 퀄리티 기준 따름.

$$
P(A|B) = \frac{P(A \cap B)}{P(B)}
$$

분모 $P(B)$ 는 $B$ 가 주어진 축소된 sample space; 분자 $P(A \cap B)$ 는 그 안에서 $A$ 가 차지하는 비율. $B$ 가 전체 sample space 면 $P(A|B)=P(A)$ 와 같다.

#### {next concept}
...

### {next concept group}
...

## {next sub-division}
...

---

## Source

- `roots/courses/_archive/{slug}/sessionNN-notes.pdf`
```

## What this command never does

- 과목 시작 시점에 빈 챕터·서브챕터 stub을 미리 생성하지 않는다 (`.agents/skills/naite/grow.md` 규칙과 동일).
- 서브챕터 노트 없이 챕터 메타를 작성하지 않는다.
- slug 충돌 허용하지 않는다 (`tree/trunk.md § Branches` + `ls roots/courses/` 중복 체크 필수).
- 서브챕터 grow 시점에 원본 pdf를 `_archive/`로 옮기지 않는다 (챕터·과목 완료 시점까지 보존).
- `ingest` 나 `capture` 내부 모듈을 직접 호출하지 않는다 (구조 불일치). 결과물 규격만 정합되게 맞춘다.
- **frontmatter `domains` 에 `course`, `course-{slug}` 같은 컬렉션 태그를 절대 넣지 않는다** (post-2026-04-28 schema). 단일 콘텐츠 도메인만.
- **서브챕터/챕터 메타를 `trunk.md` 에 등록하지 않는다.** drill-down 으로 발견.
- **`subchapter-note` 시점에 `rings.md` 를 갱신하지 않는다.** frontmatter `created`/`updated` 가 운반. 챕터 마무리 (`branch-chapter`) 1줄로 묶는다.
- tree를 건드리지 않는 op(`resume`, `chapter-start`, `stage-source`)에는 `rings.md` 엔트리를 남기지 않는다.
- 수업 시간·교수명·시험·평가 기준 등 행정 정보를 tree에 쓰지 않는다.
- `chapter-finish` / `branch-finish` 외 op 에서는 git commit 하지 않는다 — § E step 7, § F step 4 참조. `branch-finish` 외 op 에서는 git push 도 하지 않는다.
