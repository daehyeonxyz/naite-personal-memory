# ingest — grow 내부 모듈

이 파일은 사용자 노출 명령이 아니다. `/naite grow` 가 위임하는 내부 모듈이다.

ingest 는 raw 소스를 나무로 끌어들인다. 두 모드가 한 워크플로 형태를 공유한다.

## 모드

- 기본 `<path>`: `<path>` 는 `roots/` 아래의 파일이나 디렉터리다 (grow 가 위임한다).
- Legacy `--legacy <path>`: `<path>` 는 Obsidian Vault 노트다 (`roots/legacy/` 나 절대 Vault 경로). 기본 흐름 전에 wikilink 번역이 추가된다.

`<path>` 가 디렉터리면 안의 각 파일을 아래 전체 워크플로로 한 번에 하나씩 처리한다 (조용히 일괄 처리하지 않는다). 파일 사이마다 사용자가 멈출 기회를 준다.

## 컨텍스트 라우팅과 역할 분리

소스를 읽기 전에 `docs/CONTEXT.md` 를 로드하고 그 컨텍스트 허용 순서를 따른다. 페이지 조회의 빠른 경로로 `.naite/ontology/tree-manifest.json` 을 쓰되, 큐레이션된 사람용 진입점을 위해 `tree/trunk.md` 도 함께 읽는다.

긴 소스와 여러 파일 소스와 디렉터리와, 워크플로 계약을 주의 밖으로 밀어낼 가능성이 있는 모든 소스에서는 작업을 세 역할로 분리한다.

1. Reader: raw 소스를 읽고 압축된 추출 덩어리를 만든다. Reader 는 `tree/` 와 `.naite/ontology/` 와 `roots/` 를 편집하지 않는다.
2. Writer: `docs/CONVENTIONS.md` 와 이 워크플로와 생성 지도와 ontology 파일과 Reader 덩어리를 읽는다. Writer 가 tree 페이지를 만들거나 갱신한다.
3. Verifier: 바뀐 페이지를 검사하고 생성 지도를 재생성하고 `.naite/ontology/tree-dependencies.json` 에서 inbound 의미 의존 페이지를 surface 한다.

활성 도구 표면이 서브에이전트를 지원하고 사용자가 위임을 허용했으면 물리적 서브에이전트를 쓴다. 그렇지 않으면 같은 역할을 한 세션의 순차 단계로 유지한다.

## Workflow (모든 파일)

### 1. 사전 점검

- `docs/CONTEXT.md` 를 읽는다.
- `.naite/ontology/tree-manifest.json` 이 없거나 현재 작업 기준으로 낡았으면 `python .naite/scripts/build-tree-manifest.py` 를 실행한다.
- `.naite/ontology/tree-manifest.json` 을 읽고, 전체 페이지 본문을 로드하기 전에 기존 페이지 후보를 좁히는 데 쓴다.
- 기존 페이지를 편집하기 전에, 변경이 의존 페이지에 영향을 줄 수 있으면 `.naite/ontology/tree-dependencies.json` 을 읽는다. 파일이 없으면 `python .naite/scripts/build-tree-dependencies.py` 를 실행한다.
- `tree/trunk.md` 를 전문으로 읽어 어떤 지식 도메인이 있고(`## Knowledge domains` 절) 어떤 가지 메타 페이지가 있는지(`## Branches`) 파악한다. trunk 는 큐레이션이지 전수가 아니다. slug 의 진실은 `tree/*.md` glob 이다.
- `tree/seeds.md` 를 읽는다. 일치하는 stub 이 있으면 기대되는 페이지가 있다는 뜻이고 이 소스가 그것을 채울 수 있다.
- `tree/rings.md` 의 마지막 20줄 정도를 읽어 최근 맥락(무엇이 grow 됐는지, 대기 중인 실마리)을 파악한다.

### 2. 소스 읽기

- 파일을 읽는다. 2,000줄을 넘으면 조각으로 나눠 읽는다.
- 소스가 참조하는 이미지(markdown 이미지 문법)는 추출에 내용이 중요하면 Read 도구로 읽는다.

### 3. (Legacy 모드만) wikilink 번역

무엇이든 쓰기 전에 링크 pass 를 진행한다.

1. 소스의 모든 `[[target]]` 과 `[[target|display]]` 를 찾는다.
2. 각 target 을 내장된 경로가 아니라 basename 이나 표시 텍스트로 해석한다. 이유: Obsidian Vault 에는 기존 링크 부패가 있다 (예: `K-Means.md` 가 `1_Knowledge/Machine Learning/...` 를 담고 있는데 실제 폴더는 `1_Knowledge/AI-ML/...` 다). 경로를 믿으면 참조가 조용히 사라진다.
3. 각 링크를 분류한다.
   - resolved: target 이 `tree/` 페이지로 존재하거나 kebab-case 로 바꾸면 기존 slug 와 일치한다.
   - ambiguous: 후보 페이지가 여럿이다 (예: `attention` 과 `attention-mechanism` 두 페이지).
   - missing: 어떤 이름으로도 페이지가 없다.
4. 진행 전에 분류된 목록을 번역 보고로 사용자에게 보인다. 형식 예:

   ```
   Translation report for sigmoid.md:
   resolved  : softmax          → tree/softmax.md
   resolved  : activation       → tree/activation-function.md (slug differs)
   ambiguous : attention        → attention | attention-mechanism (which?)
   missing   : universal-approximation-theorem
   ```
5. 사용자가 확인하면 다음처럼 처리한다.
   - resolved 링크는 정본 slug 로 다시 쓴다 (예: `[[activation-function|activation]]`).
   - ambiguous 는 사용자에게 고르게 한다.
   - missing 은 kebab-case target 으로 링크를 유지하고 `tree/seeds.md` 에 항목을 덧붙인다 (`- [[missing-slug]] — first seen in [[new-page-slug]], context: ...`).
6. 소스의 `roots/legacy/` 사본에서(원본 Vault 파일은 절대 아님) 번역 전 wikilink 를 번역된 형태 위의 HTML 주석으로 보존한다. 예: `<!-- original: [[1_Knowledge/Machine Learning/Softmax|Softmax]] -->`.

### 4. takeaway 논의

페이지를 쓰기 전에 추출한 내용을 3~8개의 bullet 로 사용자에게 알린다. 어떤 페이지를 어떤 모양으로 만들거나 갱신할지 묻는다. 이 단계는 생략할 수 없다. 큐레이터는 사용자다.

### 5. 페이지 작성·갱신

영향받는 각 페이지에 대해 다음을 지킨다.

`docs/CONVENTIONS.md` 의 출력 품질 계약과 학습 노트 품질 축과 kind 별 품질 계약을 따른다. 본문은 자립하는 tree 페이지이지 처리 노트가 아니다. 소스의 실질을 산문으로 흡수하고, raw 경로와 소스 출처는 `## Source` 나 source-record 링크에만 둔다. `## Source` 앞의 본문에 원자료·공정 화법(`raw`, staging, extraction, PDF page, "원문에서는", "자료에서는", "이 페이지에서는")과 em dash(`—`)를 남기지 않는다. 원천 메커니즘(무엇이 아니라 어떻게와 왜)을 본문에 보존한다. H 계층은 소스의 논리적 구획을 드러내고, 수식은 조건과 기호와 해석과 함께 쓰고, 예시는 메커니즘을 실제로 재현한다. 선택한 `kind` 의 claim spine 을 지키고, 관찰과 source claim 과 해석과 가설의 혼동이 결론을 바꿀 수 있는 곳에서는 명시적으로 구분한다. "원본 필요" 표시는 ingest 한 소스에 실제로 없는 자료에만 쓰고, 가진 자료를 설명하지 않는 핑계로 쓰지 않는다 (`docs/QUALITY.md` 4절 LEAF-4).

- 페이지가 없으면 완전한 ontology frontmatter 로 `tree/<slug>.md` 를 만든다.
  ```yaml
  ---
  kind: concept | entity | source-record | project | decision | insight | comparison | essay | personal
  form: prose | index              # grow 산물은 보통 prose
  topics: []                       # canonical from `.naite/ontology/topics.md`. 0-5개. 빈 배열 OK.
  subject: [<path>]                # SKOS-lite path from `.naite/ontology/subject-tree.md`
  source-types: [course | conversation | paper | article | docs | book | essay | external]   # 8-enum list (single-item OK)
  domains: [<subject-top-level>]   # CACHED — 위 subject path 에서 기계적으로 도출
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
  ---
  ```
  - `kind` 선택 기준:
    - `concept`: 재사용 가능한 일반 개념·방법·이론이다 (permanent note).
    - `entity`: 구체적인 도구·사람·조직·제품이다 (Codex, Karpathy, OpenAI 등).
    - `source-record`: 특정 source unit 을 tree 안에 정리한 기록이다 (course subchapter 노트, chapter index, 논문 노트, 책 노트 등의 literature note).
    - `project`: 본인 프로젝트의 추적이다.
    - `decision`: 결정·선택·실패의 기록이다 (synapse). 파일명은 `decision-YYYY-MM-DD-<slug>.md` 다.
    - `insight`: 작업과 학습에서 압축된 통찰이다.
    - `comparison`: A 대 B 비교가 페이지의 본질이다.
    - `essay`: 사용자 본인이 직접 쓴 글이다 (voice 보존, 보통 `subject: [personal]` 계열). 남의 글 정리는 `source-record` 다.
    - `personal`: 자기 기록 메타 페이지다 (프로필, 이력 등. 예: `personal-profile`).
  - `form` 선택 기준: 본문이 산문 흐름이면 `prose`, 다른 페이지의 링크 목록·내비게이션 hub 면 `index` 다.
  - `subject` 는 `.naite/ontology/subject-tree.md` 의 경로 하나를 쓴다. 진짜 cross-domain 일 때만 복수로 둔다 (`[a/x, b/y]`).
  - `topics` 는 `.naite/ontology/topics.md` 의 정본을 우선한다.
    - 미등록 topic 후보가 입자도 가드(`.naite/ontology/topics.md` 의 Topic granularity guidance 절. 재사용 가능한 개념 수준이고 넓은 도메인도 페이지 특정도 아닐 것)를 통과하면, LLM 이 직접 `.naite/ontology/topics.md` 의 canonical_topics 절에 덧붙이고 페이지에 사용한다 (`docs/CONVENTIONS.md` Schema evolution 의 자율 A).
    - 가드에 실패하면 페이지에서 빼고 grow 요약에 "topic skipped (granularity): X" 로 surface 만 한다.
    - 명백한 별칭(`cot ↔ chain-of-thought` 처럼 형태 변형이나 잘 알려진 약어)도 LLM 이 `.naite/ontology/topics.md` 의 aliases 절에 직접 덧붙인다 (자율 A). 동의어로 의심되지만 모호하면 care --check 의 군집 surface 로 미룬다.
  - `source-types` 는 8-enum 리스트다 (`docs/CONVENTIONS.md` Ontology 절 참조). 한 페이지가 여러 소스에서 강화될 수 있으므로 `source-types: [course, paper]` 처럼 복수가 가능하다. `legacy` 는 source-types 값이 아니다. `--legacy` 모드의 import 출처는 본문이나 기록 항목으로 남기고, source-types 는 콘텐츠의 본질(보통 `[article]` 이나 `[conversation]`)을 따른다.
  - 새 subject narrower 가 자연스러우면 LLM 이 `.naite/ontology/subject-tree.md` 의 narrower: 에 후보를 덧붙이고 grow 요약에 "narrower proposed: X" 로 surface 한다 (자율 B). 사용자가 다음 검토 사이클에서 confirm 하거나 되돌린다.
  - 새 top-level domain 과 새 enum 값(`kind`·`form`·`source-types`)과 새 facet 필드와 subject 폐기는 자율 C 다. LLM 의 추가가 절대 금지되고, grow 요약에 압력으로 surface 만 한다.
  - 본문은 요약을 먼저 적고 세부를 다음에 적는다. 소스는 `[[source-page-slug]]` 로 인용한다 (그 소스가 가치 있으면 `kind=source-record` 페이지를 만든다. 특정 논문·아티클이 그 예다).
- 페이지가 이미 있으면 편집한다. frontmatter 의 `updated:` 를 갱신한다. 기존 구조를 보존하고 산문을 정밀하게 더하거나 고친다. 모순은 본문에 명시적으로 표시한다 (예: "_2026-04-15 source [[foo]] disagrees: ..._").

각 `form=prose` 잎을 완성하기 직전에 본문을 `docs/QUALITY.md` 4절(LEAF-1~6)과 `docs/CONVENTIONS.md` 의 학습 노트 품질 축과 kind 별 품질 계약으로 자기 점검한다. 미달인데 소스에 필요한 내용이 있으면 그 내용을 먼저 펼쳐 쓴다. 소스가 실제로 부족하면 얇은 잎을 `tree/` 에 내보내지 않고 `tree/seeds.md` 에 깊이 보강 후보 stub 으로 정직하게 강등한다 (stub 형식: `- [[slug]]: LEAF-N 미달 (<사유>), 필요한 것 <부족 자료>`). 강등한 잎은 grow 요약에 surface 한다. 이것은 작성 시점의 관문이다. 관문을 빠져나간 얇음은 care --check 의 3절 lint 가 3k(leaf-depth 경고)로 사후에 surface 한다. `form=index` 페이지는 `docs/CONVENTIONS.md` kind 별 품질 계약의 index 계약으로 별도 자기 점검한다.

영향받는 페이지를 쓰거나 편집한 뒤에는 `## Source` 앞의 본문에 `/naite care` 의 Content Guard 를 실행하고 위반을 즉시 고친다. 이것은 나중의 감사 정리가 아니라 생산의 일부다.

content guard 다음에는 다음을 실행한다.

```powershell
python .naite/scripts/build-tree-manifest.py
python .naite/scripts/build-tree-dependencies.py
```

그 다음 `.naite/ontology/tree-dependencies.json` 에서 바뀐 모든 slug 로 들어오는 inbound 참조를 점검한다. 의미 의존 후보를 grow 요약에 surface 한다. 사용자가 명시적으로 수리를 요청하지 않는 한 의존 페이지를 자동으로 다시 쓰지 않는다.

subject 경로 드리프트와 가드 실패 topic 의 누적은 care --check 의 주된 surface 대상이다. 자율 A 추가물(정본 topic, 별칭, 일반 개념 페이지)의 사후 품질은 care --check 의 garbage collector(`.agents/skills/naite/care-check.md` 14절)가 검증한다.

### 6. `trunk.md` 갱신 (큐레이션이지 전수가 아니다)

`trunk.md` 는 큐레이션된 진입점이라 모든 새 페이지를 등재하지 않는다. 다음 경우에만 갱신한다.

- 새 hub 페이지 (다른 페이지에서 링크를 자주 받을 가능성이 높은 일반 개념 페이지): `## Knowledge domains` 의 해당 도메인 "주요" 줄에 한 줄을 추가한다 (4~7개 한도. 한도에 닿으면 어느 줄을 빼고 넣을지 사용자에게 묻는다).
- hub 역할을 하는 새 source·entity 페이지 (예: 메이저 논문·책·플랫폼 메타): 같은 방식으로 hub 줄에 등재한다.
- 새 도메인의 채택 (사용자 결정 후): `## Knowledge domains` 아래 `### <new-domain>` 절을 신설한다.

다음 경우에는 갱신하지 않는다.

- 일반 개념 페이지가 hub 후보가 아닐 때 (한 페이지에서만 링크를 받을 짧은 개념). care --check 의 고연결 페이지 검사가 나중에 surface 한다.
- course 의 chapter 와 subchapter (course 메타의 Chapters 절이 단일 소스다).

기존 hub 페이지의 콘텐츠가 본질적으로 바뀌면 한 줄 요약을 고친다.

### 7. `rings.md` 에 덧붙이기

항목 하나를 더한다.

```
## [YYYY-MM-DD] grow | <source title or slug>
- pages created: [[...]]
- pages updated: [[...]]
- subject: <path>  (cross-domain 일 때만 복수, .naite/ontology/subject-tree.md 참조)
- stubs added: N
```

### 8. grow 이후 처리 (소스 종류별)

이 나무에는 범용 `_archive/` 층이 없다. raw 파일이 source of truth 이고 tree 페이지가 증류물이라, raw 를 보관용으로 복제하는 층은 중복으로 판정되어 제거됐다 (`docs/CONVENTIONS.md` 의 grow 이후 처리 절 참조).

소스 위치에 따라 다음 중 정확히 하나를 실행한다.

- `roots/articles/` 아래의 소스: 조치 없음. 파일은 제자리에 남고 `rings.md` 가 grow 를 기록한다.
- `roots/legacy/` 아래의 소스: 조치 없음. articles 와 같이 파일이 남는다.
- `roots/conversations/` 아래의 소스 (capture 단계가 만든 `YYYY-MM-DD-<slug>.md` claim 요약): claim 요약을 삭제한다. 일시적 staging 이었다. `roots/conversations/_transcripts/<same-slug>.md` 의 원문 전사본은 건드리지 않는다. 그것이 영구 보험 사본이다.
- `roots/courses/{slug}/` 아래의 소스: subchapter grow 시점에는 조치가 없다. grow branch 모드의 `branch-finish` op 가 통째 보관 이동(`roots/courses/{slug}/` 에서 `roots/courses/_archive/{slug}/` 로)을 담당한다. 파일 단위 이동을 시도하지 않는다.
- 그 밖의 위치 (예: 사용자가 `roots/` 밖의 파일을 직접 가리킨 경우): 표시하고, 먼저 위의 위치 중 하나로 staging 할지 묻는다. `roots/` 밖의 위치에서 grow 하지 않는다.

필요한 파일 작업이 실패하면(예: 도구 환경이 conversations claim 요약의 삭제를 막으면) 완료를 주장하지 않는다. `rings.md` 에 같은 prefix 로 `- aborted: could not clean up <path> after grow` 본문의 항목을 덧붙이고, 잔류 상태를 사용자에게 surface 한다. `/naite care --check` 도 이 상태를 표시한다.

`roots/legacy/` 밖의 절대 Vault 경로를 받은 `--legacy` 모드에서는, 먼저 `roots/legacy/<slug>.md` 로 복사한다 (3절 6항의 번역 주석 포함). 그 다음 위의 `roots/legacy/` 규칙을 적용한다. 파일은 남는다. 원본 Vault 파일 자체는 수정하지 않는다.

### 9. 사용자와 checkpoint

무엇이 반영됐는지 요약한다. 고칠 것이 있는지 묻는다. 확인을 받은 뒤에만 다음 파일로 넘어간다 (디렉터리를 처리 중일 때).

## 이 모듈이 절대 하지 않는 것

- `roots/` 아래 파일의 내용을 변경하지 않는다. 종류별 정리(conversations 의 claim 요약 삭제, legacy 사본 생성)가 유일하게 허용되는 이동이다.
- `roots/articles/` 나 `roots/conversations/` 나 `roots/legacy/` 아래에 `_archive/` 디렉터리를 만들지 않는다. 프로젝트의 유일한 archive 경로는 `roots/courses/_archive/` 이고, 그것은 grow branch 모드 `branch-finish` 의 소관이지 이 모듈의 소관이 아니다.
- 자율 A 밖의 스키마 변경을 하지 않는다.
  - 정본 topic 과 별칭과 일반 개념 페이지는 입자도 가드를 통과하면 자율 추가한다 (자율 A).
  - subject narrower 는 후보 덧붙이기와 요약 surface 까지다 (자율 B).
  - 새 top-level domain 과 새 enum 값(`kind`·`form`·`source-types`)과 새 facet 필드와 subject 폐기는 LLM 이 절대 추가하지 않는다 (자율 C, 사용자 결정).
  - 새 페이지의 `domains` cache 는 선택한 `subject` 경로의 top-level 에서 기계적으로 도출해 함께 작성한다. `care --check` 는 낡은 cache 를 보고만 한다.
- chapter 와 subchapter 페이지를 `trunk.md` 에 등재하지 않는다. course 메타의 Chapters 절이 단일 소스다.
- git 커밋을 하지 않는다. 커밋은 사용자가 자기 리듬으로 한다.
- 파일별 사용자 확인 없이 디렉터리를 일괄 grow 하지 않는다.
