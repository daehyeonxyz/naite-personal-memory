# /naite grow backfill

이 파일은 `grow-branch.md` H 절의 sub-op 위임 대상이다. 사용자가 이미 충분히 학습한 과목을 dialogue 없이 일괄 정리하는 모드다.

이 모드는 active 학습(`grow-branch.md` A~G 절)과 분리된 운영 모델을 갖는다. Codex 단독 실행이 가능하고, 대량 PDF 추출과 chapter 단위 sweep 과 deferred commit 패턴을 쓴다. 이 파일은 backfill 만의 불변식과 chapter loop 를 담당하고, 공통 단계(slug, frontmatter, raw 폴더 셋업, branch-finish 의 archive 이동, rings 형식)는 `grow-branch.md` 의 해당 절을 그대로 따른다.

## 사용 시점

- 사용자가 이미 학습을 마친 과목(예: 저학년 전공 과목, 외부 강의 archive)을 backfill 할 때 쓴다.
- 강의자료 PDF 와, 가능하면 사용자 손필기가 staging 되어 있어야 한다.
- chapter·subchapter 구조가 충분히 명확하거나 미리 매핑이 가능해야 한다.
- 사용자가 자동화를 명시적으로 승인해야 한다. `/naite grow backfill {slug}` 호출이 그 승인이다.

active 학습과 동시에 사용하지 않는다. 학습 중인 콘텐츠에 backfill 을 쓰면 dialogue takeaway 가 사라져서 페이지의 가치가 떨어진다.

## 강행 규칙

- PNG render 는 시각 레이어가 있을 때 필수다. 텍스트 추출만으로 시작하는 것은 금지된다.
  - PDF 를 PyMuPDF 로 PNG render 하고 image-read 하는 것이 필수 사전 단계다 (`grow-branch.md` D 절의 b 단계).
  - 강의 본체와 사용자 손필기와 도형·도식을 전부 PNG 로 image-read 한 뒤에야 본문을 쓴다. 텍스트 추출은 시각 강조와 손글씨와 다이어그램과 수식 일부를 누락시킨다.
  - 0에서 1로 가는 backfill 이든 깊이 보강 pass 든 동일하게 적용된다. 깊이 보강도 PNG 재로드부터 시작한다.
  - 단 소스가 시각 레이어 없는 순수 텍스트(variant G)면 적용 대상이 없으므로 이 규칙은 자동으로 무력화된다. 그 경우에는 `.txt` 자체가 authoritative source 다.
- subchapter 의 형태는 `.agents/skills/naite/grow-branch.md` Templates 절의 서브챕터 노트를 그대로 따른다.
  - 강의 흐름을 따르는 자연스러운 H-tag 를 쓰고, `## Source` 는 파일 경로만 담는 trailing provenance 로 두고, 본문에 원본 PDF 의 페이지 anchor 와 이미지 임베드를 넣지 않는다.
- 출력 품질 계약을 지킨다 (`docs/CONVENTIONS.md` 의 출력 품질 계약과 학습 노트 품질 축과 kind 별 품질 계약).
  - 본문은 자립하는 한국어 산문으로 쓰고, `roots/` 와 PDF page 와 staging 과 render 와 backfill 과 "필기에는"과 "자료에서는" 같은 소스·공정 화법과 em dash(`—`)를 `## Source` 앞에 남기지 않는다.
  - 손필기와 시각 강조와 worked example 의 판단 순서는 개념 설명으로 흡수한다.
  - H 계층은 강의의 논리적 구획을 보여 주고, 수식은 조건과 기호와 해석과 함께 쓴다.
  - `kind=source-record` 의 질문과 메커니즘과 근거와 조건을 소스가 제공하는 범위 안에서 보존한다.
- 문체 참조: `tmp/style-reference/{course-or-domain}/manifest.md` 가 있으면 manifest 의 `Included files` 와 `Fallback path` 를 그대로 쓴다. 없으면 manifest 의 fallback 경로에 있는 노트 1~7장을 read-only 로 직접 참고한다. 어느 경우에도 tree 에 ingest 하지 않는다.
- 자동화 권한은 분리되어 있다. 이 sub-op 는 tree 페이지의 작성·검증과 raw staging 까지만 자동으로 수행한다.
  - VCS 변경(`git add`·`git commit`·`git push`)은 사용자나 chapter-finish 의 명시적 승인 후에만 한다.
  - Codex 환경에서 `.git/index.lock` 같은 권한 실패가 검출되면 즉시 중단하고 보고한다.
- 실패 유형 규칙: 같은 시스템 경계에서 동일한 에러가 반복되면 일시 장애로 보지 말고 구조 문제로 의심을 전환한다. 횟수 임계는 두지 않는다. 판단은 사용자와 운영자의 몫이다.
- worked example 은 강의자료에 자연스럽게 있을 때만 포함한다. 강제가 아니고, 강의자료에 없는 예시를 만들어 채우지 않는다.
- 자기 세션 자원의 자동 제외: 이 sub-op 가 실행 중인 worktree 와 branch 자체는 cleanup 대상에서 자동으로 제외된다. 자기 자신을 지울 수 없다.
- 그 밖의 모든 `grow-branch.md` 강행 규칙(slug, frontmatter, 이름 규칙, trunk 분리, raw 보존, archive)이 적용된다.

## Source variants

과목마다 소스 구성이 다르다. 이 스킬은 다음 variant 를 인식하고 처리한다.

### A. 표준 — 강의 PDF 와 손필기 통합 (기본)

강의자료 PDF 가 사용자 손필기를 포함한다. 단일 PDF 묶음을 chapter 단위로 PNG render 하고 image-read 한다.

### B. 별도 손필기 단일 PDF

강의 교재와 별개로 사용자 손필기가 전체 과목 통합의 단일 PDF 로 존재한다. 처리는 다음과 같다.

1. 손필기 PDF 전체를 사전에 1회 PNG render 하고 모든 PNG 를 image-read 한 뒤, chapter·section 매핑과 강조점과 관점을 `tmp/{slug}-notes-extracted.md` 에 작업 산출물로 정리한다 (tmp/ 는 gitignore 대상이고 ingest 하지 않는다).
2. 교재 PDF 는 chapter 단위로 처리한다. 각 subchapter 를 쓸 때 해당 section 의 사용자 필기 관점을 산문 서사에 자연스럽게 녹인다.

### C. 시험 정리 hwpx (한컴오피스)

사용자가 시험 준비로 정리한 한컴오피스 hwpx 가 chapter framework 의 힌트다. 처리는 다음과 같다.

1. hwpx 는 zip 과 xml 구조다. PowerShell `Expand-Archive` 로 풀고 `Contents/section*.xml` 에서 텍스트를 추출해서 `tmp/{slug}-exam-outlines.md` 에 작업 산출물로 둔다.
2. chapter 지도를 정할 때 hwpx outline 을 1차 framework 로 쓰고 PDF 내부 header 로 교차 검증한다.
3. 본문을 쓸 때 hwpx 의 정리 흐름을 구성 가이드로 활용한다. 단 hwpx 자체는 `## Source` 에 표기하지 않는다 (페이지 자립 규칙에 따라 본문에 인라인으로 흡수한다).

### D. week 와 chapter 의 불일치

강의 PDF 파일명의 week·회차 번호가 실제 chapter 와 다를 수 있다. 항상 PDF 내부 제목을 기준으로 chapter 를 확정한다. 중간·기말 review 자료는 정리 대상에서 제외한다.

### E. 저학년 깊이

저학년 때 들은 과목의 backfill 은 내용 위주로 정리한다. 강의자료에 있는 만큼만 산문으로 만든다. 깊이 부족을 tree 와 rings 와 임시 로그 어디에도 메타 코멘트로 기록하지 않는다. worked example 의 임의 추가도 금지된다.

### F. 과제·풀이 자료

강의 외에 사용자의 과제 PDF 가 별도 폴더로 존재한다. 사용자 본인의 계산 직관과 풀이 흐름은 다른 과목의 손필기와 동등한 인사이트 소스다. subchapter 를 쓸 때 과제 PNG 도 image-read 해서 풀이 관점을 산문에 녹인다. 단 과제의 문제 자체는 tree 로 옮기지 않는다.

### G. 순수 텍스트 transcript

강의자료가 영상 전사본이나 공식 배포 텍스트나 강의 script 처럼 시각 레이어 없는 순수 텍스트로 제공된다. 손필기와 다이어그램과 수식과 시각 강조가 소스 자체에 없다 (Anthropic Academy 같은 외부 과목이나 텍스트 배포 강의가 대부분이다). 처리는 다음과 같다.

1. PNG render 규칙은 적용 대상이 없으므로 자동으로 무력화된다. `.txt`(또는 markdown 으로 바뀐 전사본) 자체가 authoritative source 다. 텍스트로 시작해서 텍스트로 끝낸다.
2. subchapter 를 쓸 때 `.txt` 를 직접 읽고 강의의 자연스러운 구획을 그대로 H2·H3·H4 로 매핑한다. 본문은 소스의 산문 실질을 보존한다 (요약과 압축은 금지된다. backfill 의 목적이 `.txt` 깊이의 회복이다).
3. `## Source` 에는 `.txt` 경로 하나만 적는다 (한 subchapter 가 여러 `.txt` 로 매핑되면 전부 나열한다). 중간 산출물(`-ko.md` 같은 부분 번역·요약)은 roots 에 두지 않는다. `roots/` 는 content-immutable 이고 증류는 tree 가 담당한다 (`AGENTS.md` 계층 구조 절).
4. 다른 강행 규칙(subchapter 형태, frontmatter 5 facet, 이름 규칙, trunk 분리)은 동일하게 적용된다.

### H. Obsidian markdown 교차 참조

강의 PDF 가 canonical source 이고, 사용자의 legacy Obsidian markdown 노트가 검증과 공백 메우기의 소스로 존재한다. 처리는 다음과 같다.

1. Obsidian markdown 은 raw staging 에 원문 그대로 복사하되 tree 본문으로 그대로 옮기지 않는다. markdown 은 read-only 참조이고 강의 PDF 가 기준 소스다.
2. 사전 1회의 매핑 pass 로 PDF chapter 와 Obsidian 노트의 대응과 충돌과 공백을 `tmp/{slug}-obsidian-extracted.md` 에 정리한다. 이 작업 산출물은 gitignore 대상이고 ingest 하지 않는다.
3. chapter loop 에서는 PDF 를 PNG render 하고 image-read 한 뒤 해당 Obsidian 노트를 교차 확인한다. 충돌하면 강의 PDF 기준으로 쓰고, 필요하면 본문에 짧은 출처 산문으로 충돌 사실을 남긴다.
4. Obsidian 노트는 source 경로로 남길 수 있지만, 본문의 voice 는 tree 의 강의 원어에 가까운 산문으로 재구성한다.

### I. Obsidian markdown 이 주 소스

사용자의 Obsidian markdown 노트가 과목의 주 구조·소스이고, 강의 PDF 는 교차 확인과 누락 개념 채우기의 소스다. 처리는 다음과 같다.

1. Obsidian markdown 을 raw staging 에 원문 그대로 복사하고, 노트의 H 구조와 논리 흐름을 `tmp/{slug}-obsidian-extracted.md` 에 명시한다.
2. Obsidian 의 커버리지가 충분한 chapter 는 노트의 논리 frame 을 엄격히 따른다. 단 문장은 tree 산문으로 다시 쓰고 문장 그대로의 이식을 피한다.
3. Obsidian 커버리지가 없는 후반 chapter 는 강의 PDF 를 PNG render 하고 image-read 하되, 앞 chapter 에서 추출한 frame 과 voice 를 계승한다.
4. 강의 PDF 와 시험 정리 PDF 는 구조 확인과 공백 메우기 용도로 쓰고, 소스 간 충돌은 canonical 우선순위를 명시적으로 판단한다.

### J. 저해상도 PDF 와 녹음 보조와 cheat sheet

강의 PDF 가 저해상도이고 반복 슬라이드 중심이며, 중후반부의 녹음 전사본과 시험 정리 자료가 보조 소스로 존재한다. 처리는 다음과 같다.

1. PDF 는 저해상도라도 PNG render 와 image-read 가 필수다. 손필기와 흐름과 반복 표현을 흡수하되, 반복 슬라이드는 불변 내용의 산문으로 압축한다.
2. 녹음은 직접 ingest 하지 않는다. 사전에 변환한 전사본을 `roots/courses/{slug}/chNN-recording-transcript.md` 로 staging 한 뒤 variant G 처럼 텍스트 소스로 교차 참조한다.
3. cheat sheet 는 chapter framework 와 강조 힌트로만 쓴다. hwpx 면 unzip 과 xml 추출로, PDF 면 image-read 후 `tmp/{slug}-exam-outlines.md` 에 outline 을 둔다.
4. 수식과 모델 구조는 Obsidian 호환 LaTeX(`$...$`, `$$...$$`)로 정리하고, PDF 와 녹음과 cheat sheet 의 중복은 하나의 강의 서사로 합친다.

새 variant 가 발견되면 이 스킬에 surface 한 뒤 추가한다.

## State machine — chapter loop

backfill 은 chapter 단위의 loop 로 돈다. 각 iteration 의 단일 진실 소스는 `tmp/{slug}-run-log.md` 다 (gitignore 영역이고 커밋 대상이 아니다).

상태 전이:

- `STARTED`: chapter 처리를 시작했다. 같은 chapter 가 이미 STARTED 면 동시 실행을 막기 위해 일단 멈춘다 (아래의 crash-recovery 참조).
- `DONE`: chapter 의 모든 subchapter 페이지 작성과 검증이 끝났다. 다음 chapter 로 이동할 수 있다.
- `ABORTED`: 실패했다. 원인을 한 줄로 기록한다. 다음 iteration 은 ABORTED chapter 부터 재진입한다.

각 loop iteration 을 시작할 때는 `tmp/{slug}-run-log.md` 와 `git status --short` 만 먼저 읽는다. 진행 중인 STARTED 가 있으면 더 무거운 맥락(PDF, source manifest)을 읽지 않고 멈춘다.

STARTED 의 crash-recovery: 3·4단계 도중의 프로세스 kill 이나 PNG render OOM 이나 Codex 연결 끊김이 일어나면 `DONE` 이나 `ABORTED` 로 전이하지 못한 `STARTED` 가 남는다. 이때 무한정 멈추면 backfill 이 데드락에 빠진다. 그래서 STARTED 를 만나면 live 인지 stale 인지 판별한다. 같은 세션에서 방금 찍은 것이 아니고(직전 iteration 이 남긴 것이 아니고) 그 chapter 의 산출 페이지가 완결되지 않았으면 stale 로 간주한다. stale STARTED 는 사용자에게 "직전 ch{NN} 작업이 중간에 끊긴 것 같습니다. ABORTED 로 표시하고 그 chapter 부터 다시 진행할까요?"라고 한 줄로 확인한 뒤, 동의하면 그 STARTED 줄 다음에 `ABORTED | ... — stale STARTED recovered` 를 덧붙이고 그 chapter 부터 재진입한다. 진짜 동시 실행이 의심될 때만(다른 세션이 돌고 있을 근거가 있을 때만) 멈춘 채 사용자에게 보고한다.

상태 항목의 형식:

```
## [YYYY-MM-DDTHH:MM] STARTED | {slug} ch{NN}
## [YYYY-MM-DDTHH:MM] DONE    | {slug} ch{NN} — N subchapters
## [YYYY-MM-DDTHH:MM] ABORTED | {slug} ch{NN}
- cause: <one-line>
```

## Workflow

### 0. 사전 점검

1. `grow-branch.md` 0절의 모든 단계를 수행한다 (AGENTS.md 와 trunk.md 와 rings.md 꼬리 읽기).
2. `tmp/{slug}-run-log.md` 의 존재를 확인한다. 없으면 새로 만든다.
3. 사용자 의도를 확인한다. 어느 chapter 부터 어디까지인지다.

### 1. Chapter 단위 loop iteration

각 iteration 은 정확히 chapter 하나다.

1. `tmp/{slug}-run-log.md` 를 읽는다. 직전에 ABORTED 가 있으면 사용자에게 보고하고 재진입 여부를 확인한다.
2. STARTED 를 표시한다.
3. `grow-branch.md` C 절 chapter-start 의 단계를 적용한다 (PDF 추출, 서브챕터 목록 확인). 단 사용자 대화는 없다. 미리 결정된 매핑이나 PDF 자동 파싱 결과를 쓴다.
4. 각 subchapter 에 대해 다음 a~h 를 정확히 수행한다.
   - a. PNG render (필수): 해당 subchapter 의 PDF 페이지 범위를 PyMuPDF 1.5x 로 PNG render 한다. 명령은 `grow-branch.md` 의 PDF rendering pipeline 절에 있다. batch 는 5~15 페이지가 적정하다. 텍스트 추출만으로 시작하는 것은 절대 금지된다.
   - b. 모든 PNG 의 image-read: 한 장씩 Read 도구로 이미지를 흡수한다. 도형과 화살표와 손글씨와 여백 메모와 시각 강조와 worked example 의 숫자 단계 전부다.
   - c. variant 별 교차 참조 (해당할 때): Source variants 절의 B·C·F·H·I·J 처럼 별도 소스(사용자 필기 단일 PDF, hwpx outline, 과제 PDF, Obsidian markdown, 녹음 전사본, cheat sheet)가 있으면 해당 subchapter 의 대응 부분을 교차 참조한다. variant E(저학년 깊이)는 추가 소스가 없고 강의자료만 쓴다.
   - d. subchapter 페이지 작성: Codex prompt template 절의 골격과 `.agents/skills/naite/grow-branch.md` Templates 절의 서브챕터 노트를 따른다. 문체 anchor 를 참조한다. 0에서 1로 새로 쓸 때는 frontmatter 5 facet 을 새로 만들고, 깊이 보강 pass 에서는 기존 frontmatter 를 보존하고 본문을 추가만 한다 (축소와 삭제는 금지된다).
   - e. content guard: 작성·수정한 페이지의 `## Source` 앞 본문을 `/naite care` 의 Content Guard 기준으로 스캔하고 즉시 고친다. 특히 em dash 와 raw 경로와 소스·공정 화법과 불필요한 영어 범용 heading 과 mojibake 는 DONE 전에 남기지 않는다.
   - f. PNG 의 즉시 삭제: 해당 subchapter 작성이 끝나면 `grow-branch.md` PDF rendering pipeline 절의 삭제 스니펫으로 `tmp/render/ch{NN}_p*.png` 를 즉시 삭제한다. 누적은 금지된다 (render 경로와 파일명은 그 파이프라인과 동일하다).
   - g. lint 통과 확인: `python .naite/scripts/lint-ontology.py` 의 3a~3k 와 7절을 통과해야 한다 (blocking 은 3a·3b·3d·3g 와 3j 의 em dash 다). 3c topic 정본과 3h 언어 형태와 3j 의 나머지 출력 품질 패턴과 3k 잎 깊이는 warn-only 라 수동 리뷰로 넘긴다. backfill 산출물은 모든 3j 출력 품질 위반을 완료 전에 0으로 만든다.
   - h. 임시 로그 항목 덧붙이기: Temp run-log schema 절의 형식대로 `tmp/{slug}-run-log.md` 에 덧붙인다.
5. chapter 메타 페이지를 작성한다. `grow-branch.md` E 절 chapter-finish 의 3단계를 그대로 따르되 commit 은 하지 않는다.
6. DONE 을 표시한다.
7. VCS 변경은 하지 않는다. commit 은 사용자에게 위임한다 (또는 사용자가 별도로 chapter-finish op 를 명시 호출할 때 한다).

## Temp run-log schema

`tmp/{slug}-run-log.md` 의 항목 형식이다. subchapter 하나를 처리할 때마다 누적되고, finalizer 가 통합할 때 참조한 뒤 흡수하고 삭제한다.

### subchapter 별 항목 (chapter loop 4h 의 산출)

```
- subchapter: course-{slug}-ch{NN}-{SS}-{title-slug}
- source: roots/courses/{slug}/sessionNN-notes.pdf p.{START}-{END}
- supplementary: (있을 때만) 사용자 필기 single PDF p.{X-Y} | hwpx outline section | 과제 PDF p.{Y-Z}
- handwriting anchors absorbed: 대략 N
- body line count: before {X} → after {Y}  (deepening pass 시 의미 있음, 0-to-1 시 0 → Y)
- summary: 1 줄 — 어떤 깊이 / 강조점 / 사용자 관점이 추가됐는지
```

### 과목 요약 (모든 chapter 완료 후)

```
## course summary
- chapters: N
- subchapters: M
- total PNG batches rendered: K
- proposed subject path: <ontology path>
- trunk.md proposed line: ` - [[course-{slug}-00-index]] — {title}`
- 1-line course summary
```

finalizer 가 위 정보를 `tree/rings.md` 의 굵은 `branch-chapter`(chapter 단위)나 `branch-finish`(과목 종료 시) 항목으로 변환한 뒤 이 run-log 를 삭제한다. rings op 는 `docs/CONVENTIONS.md` 의 rings.md 규율 절의 어휘를 따른다. `migration` 은 스키마·구조 변경 전용이라 backfill 의 콘텐츠 작업에는 쓰지 않는다. 페이지별 평가는 절대 `tree/rings.md` 에 노출하지 않는다. rings.md 는 굵은 요약만 담는다.

### 2. Branch-finish

backfill loop 가 끝난 뒤 사용자가 명시적으로 승인하면 `grow-branch.md` F 절 branch-finish 의 단계를 그대로 수행한다. archive 이동과 rings 항목과 push 까지다.

finalizer 가 worktree 를 제거하기 전에는 teardown 안전 검사를 반드시 수행한다.

1. `git -C ../naite-{slug} status --ignored --porcelain` 에서 `!!` ignored 항목을 확인한다.
2. ignored 항목이 비어 있으면 worktree remove 를 진행할 수 있다.
3. ignored 항목이 `tmp/` 같은 작업 산출물뿐이면 그 항목이 worktree 내부 경로인 것을 확인한 뒤 삭제할 수 있다.
4. ignored 항목이 `roots/courses/_archive/{slug}/` 아래의 소스 파일이면, main repo 의 같은 경로에서 `git ls-files` 로 추적 여부를 확인한다. 추적되지 않았으면 main 에 복사한 뒤 `git add -f` 와 commit 으로 raw 소스를 먼저 보존한다.
5. 고유한 소스가 main 에 보존되기 전에는 `git worktree remove` 를 실행하지 않는다.

## Codex prompt template

backfill 의 각 subchapter 를 쓸 때 Codex 에 전달할 prompt 의 골격이다.

> 목표: tree 의 course subchapter 페이지 1개를 작성한다.
>
> Ontology: `docs/CONVENTIONS.md` Ontology 절, `.naite/ontology/subject-tree.md`, `.naite/ontology/topics.md`.
>
> 페이지 형태: `.agents/skills/naite/grow-branch.md` Templates 절의 서브챕터 노트를 그대로 지킨다.
> - 강의 흐름의 자연스러운 H-tag 를 쓴다 (H1 은 subchapter, H2 는 구획, H3 는 개념 묶음, H4 는 개념).
> - `## Source` 는 trailing provenance 이고 파일 경로만 적는다.
> - 본문에 원본 PDF 의 페이지 anchor 를 넣지 않는다. 이미지 임베드는 기본 off 다.
> - `## Core idea / ## Details / ## Also known as / ## Related` 같은 위키 rubric heading 을 만들지 않는다.
> - 본문은 한국어 설명이 기본 골격이다. 기술 용어와 수식과 모델 이름과 강의 고유의 영어 heading 은 허용하지만, 한국어로 자연스럽게 쓸 수 있는 범용 heading 과 문장은 한국어로 쓴다.
> - `## Source` 앞의 본문에 `roots/` 와 staging 과 PDF page 와 page range 와 render 와 backfill 과 "필기에는"과 "강의 노트에는"과 "자료에서는"과 "이 페이지에서는" 같은 소스·공정 화법을 쓰지 않는다.
>
> 문체 anchor: `tmp/style-reference/{course-or-domain}/manifest.md 가 있으면 그것을, 없으면 manifest 의 fallback 경로를 read-only 로 참조한다. ingest 는 금지된다. 이것은 관찰된 voice 신호이지 hard spec 이 아니다.
>
> 품질: 공식의 나열은 금지된다 (유도와 각 항의 의미와 성립 조건을 함께 쓴다). 앞 subchapter 와의 흐름은 산문 안에 자연스럽게 잇는다. 학생 필기의 강조점은 해당 개념의 H4 설명 안에 통합한다. 슬라이드의 예시는 숫자와 과정과 결과를 실제로 쓴다. 유사·대비 개념의 비교 산문은 가능하다. worked example 은 강의자료에 자연스럽게 있을 때만 쓴다. 강제가 아니다.
>
> 출력: `tree/course-{slug}-ch{NN}-{SS}-{title-slug}.md`. frontmatter 는 5 facet 이고 본문은 강행 규칙을 지킨다.

## Contamination guards

다중 세션 운영에서 발견된 실패 패턴과 회피 규칙이다.

### 가지 섞임 오염

한 작업 branch 에 서로 다른 과목의 커밋이 섞이면(예: `backfill-aa101` 안에 다른 과목의 chapter 커밋이 함께 들어간 사고) 통합 시 cherry-pick 결정이 모호해지고 finalizer 가 멈춘다.

회피 규칙은 다음과 같다.

- 한 세션은 정확히 하나의 과목 branch 에서만 작업한다.
- 작업 시작 시 `git status` 와 현재 branch 와 직전 커밋 로그를 확인한다. 다른 과목의 커밋이 보이면 그 branch 를 오염된 것으로 판단하고, 새 clean branch 로 분기한 뒤 그쪽에서만 진행한다.
- 오염이 발견되면 clean 소스가 별도 branch 로 격리되어 있는지 확인한다.

### `*-isolated` branch 관례

오염 발생 후 clean 소스만 분리한 branch 는 `{original}-isolated` 로 이름 짓는다. 예를 들어 `backfill-aa101-isolated` 는 `backfill-aa101` 에서 오염을 제외한 clean 작업이다. finalizer 는 `*-isolated` 가 있으면 그것을 정식 소스로 우선한다.

### 다중 worktree 작업 중의 dirty 메인 repo

사용자의 메인 repo 가 dirty 한 채로(codex scratch, Obsidian 설정, 미추적 작업물) worktree 작업이 진행되면, finalizer 통합 시 dirty 상태가 main 으로 새지 않게 격리한다.

- finalizer 는 별도의 clean worktree(`{repo}-finalizer-{TODAY}`)에서 origin/main 을 기준으로 작업한다.
- 메인 repo 의 dirty 처리는 finalizer 통합 후 사용자 confirm 을 받아 별도 단계로 한다 (worktree 와 branch 의 cleanup 도 같은 단계다).

### Codex scratch 격리

codex 나 다른 에이전트가 자체 scratch(`.codex-work/`, `.codex-cache/` 등)를 메인 repo 안에 만드는 경우가 있다. 이 디렉터리는 tree 와 무관하고 `.gitignore` 차단 대상이다. 발견되면 care --check 가 surface 한다 (`/naite care --check` 7절 Binary creep 의 비 tree 오염 검사).

## 이 명령이 절대 하지 않는 것

- 사용자 dialogue 없이 active 학습 콘텐츠를 쓰지 않는다 (그것은 `grow-branch.md` A 절 start 의 책임이다).
- 자동으로 `git add` 와 `git commit` 과 `git push` 를 하지 않는다. 항상 사용자 승인 후에 한다.
- 강의자료에 없는 worked example 을 만들어 페이지에 추가하지 않는다.
- 본문에 원본 PDF 의 페이지 anchor 를 인용하지 않는다 (`.agents/skills/naite/grow-branch.md` Templates 절 서브챕터 노트의 자립 규칙).
- 텍스트 추출만으로 본문을 쓰지 않는다 (PNG render 와 image-read 가 필수 사전 단계다).
- `tmp/style-reference/` 나 `tmp/{slug}-notes-extracted.md` 나 `tmp/{slug}-exam-outlines.md` 의 내용을 tree 로 복사하거나 요약하거나 인용 페이지로 만들지 않는다.
- chapter 하나를 처리 중일 때(STARTED 가 살아 있는 동안) 다음 chapter 로 넘어가지 않는다.
- 자기 자신(현재 실행 중인 worktree 와 branch)의 cleanup 을 시도하지 않는다.
- 다른 과목 branch 의 커밋을 이 세션의 작업 branch 로 머지하지 않는다 (오염 회피).
