# /naite grow backfill

`grow-branch.md § H` 의 sub-op 위임 대상. 사용자가 이미 충분히 학습한 과목을 dialogue 없이 일괄 정리하는 mode.

active 학습 (`grow-branch.md § A-G`) 과 분리된 운영 모델 — Codex 단독 실행 가능, 대량 PDF 추출, chapter 단위 sweep, deferred commit 패턴. 본 파일은 backfill 만의 invariant 와 chapter loop 를 담당하고, 공통 step (slug, frontmatter, raw 폴더 셋업, branch-finish archive 이동, rings 형식) 은 `grow-branch.md` 의 해당 섹션을 그대로 따른다.

## When to use

- 사용자가 이미 학습 완료한 과목 (예: 저학년 전공 과목, 외부 강의 archive) 을 backfill.
- 강의자료 PDF 와 (가능하면) 사용자 손필기가 staged 됨.
- chapter / subchapter 구조가 충분히 명확하거나, 미리 매핑이 가능함.
- 사용자가 자동화에 명시 승인 — `/naite grow backfill {slug}` 호출.

active 학습과 동시에 사용하지 않는다 — 학습 중 콘텐츠에 backfill 을 쓰면 dialogue takeaway 가 사라져서 페이지 가치가 떨어진다.

## Hard rules

- **PNG render mandatory (when visual layer present)**: **텍스트 추출 단독 시작 금지.** PDF → PyMuPDF PNG render + image-read 가 *mandatory pre-write step* (`grow-branch.md § D step b`). 강의 본체 + 사용자 손필기 + 도형·도식 모두 PNG 로 image-read 한 뒤에야 본문 작성. 텍스트 추출은 시각 강조·손글씨·다이어그램·수식 일부를 누락. 0-to-1 backfill 든 deepening pass 든 동일 적용 — 깊이 보강도 PNG 재로드부터. **단 source 가 시각 레이어 없는 순수 텍스트 (variant G) 면 적용 대상이 부재하므로 룰이 자동 무력화 — 그 경우 `.txt` 자체가 authoritative source 다.**
- **Subchapter shape**: `.agents/skills/naite/grow-branch.md § Templates § 서브챕터 노트` 그대로. Lecture-natural H-tag, `## Source` trailing provenance (file path only), 본문에 원본 PDF page anchor·이미지 임베드 안 함.
- **Output quality contract**: `docs/CONVENTIONS.md § Output quality contract` 준수. 본문은 self-contained Korean prose 로 작성하고, `roots/`, PDF page, staging, render, backfill, "필기에는", "자료에서는" 같은 source/process voice 를 `## Source` 앞에 남기지 않는다. 손필기·시각 강조·보조자료 관점은 개념 설명으로 흡수한다.
- **Style reference**: `tmp/style-reference/{course-or-domain}/manifest.md` 가 있으면 manifest 의 `Included files` + `Fallback path` 그대로 사용. 없으면 manifest 의 fallback path 의 노트 1-7장을 read-only 로 직접 참고. 어느 경우에도 tree 에 ingest 안 함.
- **자동화 권한 분리**: 본 sub-op 는 tree 페이지 작성·검증, raw staging 까지만 자동 수행. **VCS mutation (`git add` / `git commit` / `git push`) 은 사용자 또는 chapter-finish 의 명시 승인 후에만**. Codex 환경에서 `.git/index.lock` 같은 권한 실패 검출 시 즉시 중단하고 보고.
- **Failure-mode 룰**: 같은 시스템 경계에서 동일 에러가 반복되면 transient 로 보지 말고 architecture 의심으로 전환. 횟수 임계 안 박음 — 사용자·운영자의 판단.
- **Worked example**: 강의자료에 자연스럽게 있을 때만 포함. 강제 아님 — 강의자료에 없는 예시를 만들어서 채우지 않는다.
- **Self-skip on own session resources**: 본 sub-op 가 실행 중인 worktree·branch 자체는 cleanup 대상에서 자동 제외. 자기 자신을 못 지움.
- 그 외 모든 `grow-branch.md § Hard rules` 적용 (slug, frontmatter, naming, trunk 분리, raw 보존, archive).

## Source variants

course 마다 source 구성이 다름. 본 skill 은 다음 variant 를 인식·처리.

### A. 표준 — 강의 PDF + 손필기 통합 (default)
강의자료 PDF 가 사용자 손필기를 포함. 단일 PDF set 을 chapter 단위로 PNG render + image-read.

### B. 별도 손필기 단일 PDF
강의 교재와 별개로 사용자 손필기가 *전체 코스 통합 단일 PDF* 로 존재. 처리:
1. 손필기 PDF 전체를 사전 1회 PNG render → 모든 PNG image-read → chapter/section 매핑 + 강조점·관점을 `tmp/{slug}-notes-extracted.md` 에 working artifact 로 정리 (tmp/ gitignore, ingest 안 함).
2. 교재 PDF 는 chapter 단위 처리. 각 subchapter 작성 시 *해당 section 의 사용자 필기 관점* 을 prose narrative 에 자연스럽게 녹임.

### C. 시험 정리 hwpx (한컴오피스)
사용자가 시험 준비로 정리한 한컴오피스 hwpx 가 chapter framework hint. 처리:
1. hwpx 는 zip + xml 구조. PowerShell `Expand-Archive` 로 unzip → `Contents/section*.xml` 에서 텍스트 추출 → `tmp/{slug}-exam-outlines.md` 에 working artifact.
2. chapter map 결정 시 hwpx outline 을 1차 framework, PDF 내부 헤더로 cross-validate.
3. 본문 작성 시 hwpx 정리 흐름을 *구성 가이드* 로 활용. 단 hwpx 자체는 `## Source` 에 표기 안 함 (page self-contained 룰 — 본문 inline 흡수).

### D. week ≠ chapter
강의 PDF 파일명의 week / 회차 번호가 실 chapter 와 다를 수 있음. 항상 PDF 내부 제목 기준으로 chapter 확정. mid/final review 자료는 정리 대상에서 제외.

### E. 저학년 깊이
저학년 때 들은 코스의 backfill 은 *내용 위주* 정리 — 강의자료에 있는 만큼만 prose 화. 깊이 부족을 tree / rings / temp log 어디에도 메타 코멘트로 기록 금지. worked example 임의 추가 금지.

### F. 과제 / 풀이 자료
강의 외에 사용자 과제 PDF 가 별도 폴더로 존재. 사용자 본인의 *계산 직관·풀이 흐름* 이 다른 코스 손필기와 동등한 인사이트 source. subchapter 작성 시 과제 PNG 도 image-read 하여 풀이 관점을 prose 에 녹임. 단 과제 *문제* 자체를 tree 에 옮기지 않음.

### G. 순수 텍스트 transcript
강의자료가 video transcript / 공식 배포 텍스트 / lecture script 등 **시각 레이어 없는 순수 텍스트** 로 제공됨. 손필기·다이어그램·수식·시각 강조가 source 자체에 부재 (대부분 Anthropic Academy 같은 외부 코스 또는 텍스트 배포 강의). 처리:
1. PNG render 룰은 *적용 대상이 부재* 하므로 자동 무력화. `.txt` (또는 markdown 화된 transcript) 자체가 authoritative source — 텍스트로 시작·텍스트로 끝.
2. Subchapter 작성 시 `.txt` 를 직접 read → lecture 의 자연 sub-division 그대로 H2/H3/H4 매핑. 본문은 source 의 prose substance 를 *보존* (요약·압축 금지 — backfill 의 목적이 .txt 깊이 회복).
3. `## Source` 에 `.txt` path 1개만 (또는 1 subchapter 가 multiple `.txt` 로 매핑되면 모두 나열). 중간 산출물 (`-ko.md` 같은 부분 번역·요약) 은 roots 에 두지 않음 — `roots/` content-immutable, distillation 은 tree 가 담당 (`AGENTS.md § Layers`).
4. 다른 hard rules (subchapter shape, frontmatter 5 facet, naming, trunk 분리) 는 동일 적용.

### H. Obsidian markdown cross-reference
강의자료 PDF 가 canonical source 이고, 사용자의 legacy Obsidian markdown 노트가 verification / gap-fill source 로 존재. 처리:
1. Obsidian markdown 은 raw staging 에 원문 그대로 복사하되, tree 본문으로 그대로 옮기지 않는다. markdown 은 read-only reference 이며 lecture PDF 가 기준 source 다.
2. 사전 1회 mapping pass 로 PDF chapter 와 Obsidian note 의 대응·충돌·gap 을 `tmp/{slug}-obsidian-extracted.md` 에 정리한다. 이 working artifact 는 gitignore, ingest 안 함.
3. chapter loop 에서는 PDF 를 PNG render + image-read 한 뒤, 해당 Obsidian note 를 cross-check 한다. 충돌 시 lecture PDF 기준으로 쓰고, 필요한 경우 본문에 짧은 provenance prose 로 충돌 사실을 남긴다.
4. Obsidian note 는 source path 로 남길 수 있지만, 본문 voice 는 tree 의 lecture-natural prose 로 재구성한다.

### I. Obsidian markdown primary
사용자의 Obsidian markdown 노트가 course 의 primary structure/source 이고, lecture PDF 는 cross-check / missing concept fill-in source. 처리:
1. Obsidian markdown 을 raw staging 에 원문 그대로 복사하고, note 의 H-구조·논리 흐름을 `tmp/{slug}-obsidian-extracted.md` 에 명시화한다.
2. Obsidian coverage 가 충분한 chapter 는 note 의 논리 frame 을 엄격히 따른다. 단, 문장은 tree prose 로 재작성하고 verbatim transfer 를 피한다.
3. Obsidian coverage 가 없는 후반 chapter 는 lecture PDF 를 PNG render + image-read 하되, 앞 chapter 에서 추출한 frame 과 voice 를 계승한다.
4. lecture PDF / 시험 정리 PDF 는 구조 확인과 gap-fill 용도이며, source 간 충돌은 canonical priority 를 명시적으로 판단한다.

### J. Low-res PDF + audio supplement + cheat sheets
강의 PDF 가 저해상도·반복 슬라이드 중심이고, 중후반부 audio recording transcript 와 시험 정리 자료가 보조 source 로 존재. 처리:
1. PDF 는 저해상도라도 PNG render + image-read mandatory. 손필기·흐름·반복 표현을 흡수하되, 반복 슬라이드는 invariant prose 로 압축한다.
2. audio 는 직접 ingest 하지 않는다. 사전 변환 transcript 를 `roots/courses/{slug}/chNN-recording-transcript.md` 로 staging 한 뒤 Variant G 처럼 텍스트 source 로 cross-reference 한다.
3. cheat sheet 는 chapter framework / emphasis hint 로만 사용한다. hwpx 면 unzip + xml 추출, PDF 면 image-read 후 `tmp/{slug}-exam-outlines.md` 에 outline 을 둔다.
4. 수식·모델 구조는 Obsidian 호환 LaTeX (`$...$`, `$$...$$`) 로 정리하고, PDF·audio·cheat sheet 의 중복은 하나의 lecture-natural narrative 로 합친다.

새 variant 가 발견되면 본 skill 에 surface 후 추가.

## State machine — chapter loop

backfill 은 chapter 단위 loop. 각 iteration 의 단일 truth source: `tmp/{slug}-run-log.md` (gitignore 영역, commit 대상 아님).

State transitions:
- `STARTED` — chapter 처리 시작. 같은 chapter 가 이미 STARTED 면 실행 중단 (concurrent run 방지).
- `DONE` — chapter 의 모든 subchapter page 작성 + 검증 완료. 다음 chapter 로 이동 가능.
- `ABORTED` — 실패. 원인 1줄 기록. 다음 iteration 은 ABORTED chapter 부터 재진입.

각 loop iteration 시작 시 `tmp/{slug}-run-log.md` 와 `git status --short` 만 먼저 읽는다. 진행 중인 STARTED 가 있으면 더 무거운 맥락 (PDF, source manifest) 을 읽지 않고 중단한다.

State entry 포맷:
```
## [YYYY-MM-DDTHH:MM] STARTED | {slug} ch{NN}
## [YYYY-MM-DDTHH:MM] DONE    | {slug} ch{NN} — N subchapters
## [YYYY-MM-DDTHH:MM] ABORTED | {slug} ch{NN}
- cause: <one-line>
```

## Workflow

### 0. Pre-flight

1. `grow-branch.md § 0` 의 모든 step (AGENTS.md, trunk.md, rings.md tail).
2. `tmp/{slug}-run-log.md` 존재 여부 확인. 없으면 신규 생성.
3. 사용자 인텐트 확인 — 어느 chapter 부터, 어디까지.

### 1. Chapter 단위 loop iteration

각 iteration = 정확히 한 chapter.

1. `tmp/{slug}-run-log.md` 읽기. 직전 ABORTED 있으면 사용자에게 보고하고 재진입 여부 확인.
2. STARTED 마킹.
3. `grow-branch.md § C chapter-start` 의 step 적용 (PDF 추출, 서브챕터 리스트 확인). 단 사용자 대화는 없음 — 미리 결정된 매핑 또는 PDF 자동 파싱 결과 사용.
4. 각 subchapter 에 대해 다음 a-h 를 정확히 수행:
   - **a. PNG render (mandatory)** — 해당 subchapter PDF page range 를 PyMuPDF 1.5x 로 PNG render. `grow-branch.md § PDF rendering pipeline` 의 python 명령. batch 5-15 페이지 적정. 텍스트 추출 단독 시작 절대 금지.
   - **b. 모든 PNG image-read** — 한 장씩 Read 도구로 image 흡수. 도형·화살표·손글씨·여백 메모·시각 강조·worked example 의 숫자 step 모두.
   - **c. Variant-specific cross-reference** (해당 시) — `§ Source variants` 의 B/C/F/H/I/J 처럼 별도 source (사용자 필기 단일 PDF / hwpx outline / 과제 PDF / Obsidian markdown / audio transcript / cheat sheet) 가 있으면 해당 subchapter 의 매칭 부분을 cross-reference. variant E (1학년 깊이) 는 추가 source 없음, 강의자료만.
   - **d. Subchapter 페이지 작성** — `§ Codex prompt template` 의 골격 + `.agents/skills/naite/grow-branch.md § Templates § 서브챕터 노트`. style anchor 참조. 0-to-1 신규 작성 시 frontmatter 5 facet 신규 생성, deepening pass 시 기존 frontmatter 보존 + 본문 *추가* (축소·삭제 금지).
   - **e. Content guard** — 작성/수정한 page 의 `## Source` 앞 body 를 `/naite care § Content Guard` 기준으로 스캔하고 즉시 수정. 특히 raw path, source-process voice, unnecessary English generic heading, mojibake 는 DONE 전에 남기지 않는다.
   - **f. PNG 즉시 삭제** — 해당 subchapter 작성 끝나면 `Remove-Item` 으로 roots/assets/{slug}_ch{NN}_{SS}_p*.png 즉시 삭제. 누적 금지.
   - **g. lint pass 확인** — `python .naite/scripts/lint-ontology.py` 3a-3g 통과. 3h candidates 는 manual review.
   - **h. Temp log entry append** — `§ Temp run-log schema` 형식 따라 `tmp/{slug}-run-log.md` 에 append.
5. Chapter 메타 페이지 작성 — `grow-branch.md § E chapter-finish` step 3 그대로. 단 commit 은 안 함.
6. DONE 마킹.
7. **VCS mutation 안 함**. commit 은 사용자에게 위임 (또는 사용자가 별도 chapter-finish op 명시 호출 시).

## Temp run-log schema

`tmp/{slug}-run-log.md` 의 entry 형식. 한 subchapter 처리마다 누적, finalizer 가 통합 시 참조하고 흡수 후 삭제.

### Per-subchapter entry (chapter loop step 4h 의 산출)
```
- subchapter: course-{slug}-ch{NN}-{SS}-{title-slug}
- source: roots/courses/{slug}/sessionNN-notes.pdf p.{START}-{END}
- supplementary: (있을 때만) 사용자 필기 single PDF p.{X-Y} | hwpx outline section | 과제 PDF p.{Y-Z}
- handwriting anchors absorbed: 대략 N
- body line count: before {X} → after {Y}  (deepening pass 시 의미 있음, 0-to-1 시 0 → Y)
- summary: 1 줄 — 어떤 깊이 / 강조점 / 사용자 관점이 추가됐는지
```

### Per-course summary (모든 chapter 완료 후)
```
## course summary
- chapters: N
- subchapters: M
- total PNG batches rendered: K
- proposed subject path: <ontology path>
- trunk.md proposed line: ` - [[course-{slug}-00-index]] — {title}`
- 1-line course summary
```

finalizer 가 위 정보를 `tree/rings.md` 의 coarse migration / branch-start entry 로 변환 후 본 run-log 삭제. **페이지별 verdict 절대 tree/rings.md 에 노출 안 함** — rings.md 는 coarse summary 만.

### 2. Branch-finish

backfill loop 종료 후 사용자가 명시 승인 시 `grow-branch.md § F branch-finish` 의 step 그대로 — archive 이동, rings entry, push 까지.

Finalizer 가 worktree 를 제거하기 전에는 teardown safety check 를 반드시 수행한다:
1. `git -C ../naite-{slug} status --ignored --porcelain` 에서 `!!` ignored 항목을 확인한다.
2. ignored 항목이 비어 있으면 worktree remove 진행 가능.
3. ignored 항목이 `tmp/` 같은 working artifact 뿐이면 해당 worktree 내부 경로임을 확인한 뒤 삭제 가능.
4. ignored 항목이 `roots/courses/_archive/{slug}/` 아래 source 파일이면, main repo 의 같은 경로에서 `git ls-files` 로 추적 여부를 확인한다. 추적되지 않았으면 main 에 복사 후 `git add -f` + commit 으로 raw source 를 먼저 보존한다.
5. 고유 source 가 main 에 보존되기 전에는 `git worktree remove` 를 실행하지 않는다.

## Codex prompt template

backfill 의 각 subchapter 작성 시 Codex 에 전달할 prompt 의 골격:

> **목표**: tree 의 course subchapter page 1개 작성.
>
> **Ontology**: `docs/CONVENTIONS.md § Ontology`, `.naite/ontology/subject-tree.md`, `.naite/ontology/topics.md`.
>
> **Page shape**: `.agents/skills/naite/grow-branch.md § Templates § 서브챕터 노트` 그대로 준수.
> - Lecture-natural H-tag (H1=subchapter, H2=sub-division, H3=concept group, H4=concept).
> - `## Source` trailing provenance, 파일 path only.
> - 본문에 원본 PDF page anchor 안 함. 이미지 임베드 default off.
> - `## Core idea / ## Details / ## Also known as / ## Related` 같은 wiki-rubric 헤딩 안 만듦.
> - 본문은 한국어 설명 spine 이 기본. technical term, formula, model name, course-native English heading 은 허용하지만 한국어로 자연스럽게 쓸 수 있는 generic heading/문장은 한국어로 쓴다.
> - `## Source` 앞 본문에 `roots/`, staging, PDF page, page range, render, backfill, "필기에는", "강의 노트에는", "자료에서는", "이 페이지에서는" 같은 source/process voice 를 쓰지 않는다.
>
> **Style anchor**: `tmp/style-reference/{course-or-domain}/manifest.md` (있으면) 또는 manifest 의 fallback path. read-only 참조, ingest 금지. *관찰된 voice 신호* 이지 hard spec 아님.
>
> **Quality**: 공식 나열 금지 (유도·각 항 의미·성립 조건 함께). 앞 subchapter 와의 흐름은 prose 안에 자연스럽게. 학생 필기 강조점은 해당 개념 H4 설명 안에 통합. 슬라이드 예시는 숫자·과정·결과 실제로 작성. 유사·대비 개념 비교 prose 가능. Worked example 은 강의자료에 자연스럽게 있을 때만 — 강제 아님.
>
> **출력**: `tree/course-{slug}-ch{NN}-{SS}-{title-slug}.md`. frontmatter 5 facet, body 는 hard rules 준수.

## Contamination guards

multi-session 운영에서 발견된 실패 패턴 + 회피 룰.

### Mixed-branch contamination
한 work branch 에 *서로 다른 코스의 commit 이 섞이면* (예: `backfill-aa101` 안에 다른 코스의 chapter commit 이 함께 들어간 사고), 통합 시 cherry-pick 결정이 모호해지고 finalizer 가 멈춤.

회피:
- 한 session 은 정확히 *하나의 코스 branch* 에서만 작업.
- 작업 시작 시 `git status` + 현재 branch + 직전 commit log 확인 — 다른 코스 commit 이 보이면 그 branch 는 contaminated 로 판단, 새 clean branch 로 분기 후 그쪽에서만 진행.
- Contamination 발견 시 *clean source* 가 별도 branch 로 격리되어 있는지 확인.

### `*-isolated` branch convention
contamination 발생 후 clean source 만 분리한 branch 는 `{original}-isolated` 명명. 예: `backfill-aa101-isolated` = `backfill-aa101` 의 contamination 제외한 clean 작업. finalizer 는 `*-isolated` 가 있으면 그것을 정식 source 로 우선.

### 메인 repo dirty during multi-worktree work
사용자 메인 repo 가 dirty (codex scratch / Obsidian config / untracked 작업물) 한 채로 worktree 작업이 진행되면, finalizer 통합 시 dirty state 가 main 으로 새지 않도록 격리:
- finalizer 는 *별도 clean worktree* (`{repo}-finalizer-{TODAY}`) 에서 origin/main 으로부터 작업.
- 메인 repo dirt 처리는 finalizer 통합 후 사용자 confirm 받아 별도 단계 (worktree·branch cleanup 도 같은 단계).

### Codex scratch 격리
codex (또는 다른 agent) 가 자체 scratch (`.codex-work/`, `.codex-cache/` 등) 를 메인 repo 안에 만드는 경우가 있음. 이 디렉토리는 tree 와 무관 — `.gitignore` 차단 대상. 발견 시 care --check surface (`/naite care --check § 7` Binary creep 의 비-tree dirt 검사).

## What this command never does

- 사용자 dialogue 없이 active learning 콘텐츠 작성 (이건 `grow-branch.md § A start` 의 책임).
- 자동 `git add` / `git commit` / `git push` — 항상 사용자 승인 후.
- 강의자료에 없는 worked example 을 만들어서 페이지에 추가.
- 본문에 원본 PDF page anchor 인용 (`.agents/skills/naite/grow-branch.md § Templates § 서브챕터 노트` self-contained 룰).
- 텍스트 추출 단독으로 본문 작성 (PNG render + image-read 가 mandatory pre-write step).
- `tmp/style-reference/` 또는 `tmp/{slug}-notes-extracted.md` / `tmp/{slug}-exam-outlines.md` 내용을 tree 로 복사·요약·인용 페이지 생성.
- chapter 한 개를 처리 중 (STARTED 살아있는 동안) 다음 chapter 로 넘어감.
- 자기 자신 (현재 실행 중인 worktree·branch) 을 cleanup 시도.
- 다른 코스 branch 의 commit 을 본 session 의 작업 branch 로 머지 (contamination 회피).
