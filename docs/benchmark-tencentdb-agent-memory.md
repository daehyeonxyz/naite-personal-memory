# Benchmark — TencentDB Agent Memory vs naite

**Status**: 스카우트 완료 (2026-07-22, 마당 recruit 파이프라인). 제품 로드맵 참고용 경쟁 레퍼런스 문서.
**Source**: https://github.com/TencentCloud/TencentDB-Agent-Memory @ `45e6e80` (MIT, Tencent 2026). npm `@tencentdb-agent-memory/memory-tencentdb`.
**Scope**: 이 문서는 "무엇을 배울 것인가" 를 다룬다. 코드 이식은 하지 않는다(호스트가 OpenClaw 전용이라 비이식). 근거 등급 표기 — `[코드 확인]` = 스카우트에서 소스를 직접 읽음, `[저자 주장]` = README 벤치마크 수치 인용(재현 안 함).

---

## 1. 그들의 구조 요약

같은 시장(에이전트 개인 기억)의 가장 크게 성장한 오픈소스 구현이다. 두 축으로 되어 있다.

**심볼릭 단기기억 (in-task)** — 무거운 도구 로그를 컨텍스트에서 내리고(offload) 압축 심볼(Mermaid)로 치환해 태스크 안에서의 토큰 폭증을 막는다. `[저자 주장]` WideSearch 토큰 −61.38%, 성공률 상대 +51.52%, SWE-bench 50연속 태스크 세션 기준.

**계층형 장기기억 (cross-session)** — 원본 대화(L0) → 기록 추출(L1) → Scene Block(L2) → Persona(L3) 로 증류한다. "무손실 축적도, 비가역 요약도 거부한다" 는 설계 선언. `[저자 주장]` PersonaMem 48% → 76%.

핵심 파일 형식 `[코드 확인]`:

- **Scene Block** (`src/core/scene/scene-format.ts`): META 구분자로 감싼 Markdown. 메타 4필드 = `created / updated / summary / heat`. heat 는 정수 온도.
- **Scene Navigation** (`scene-navigation.ts`): 장면 인덱스를 heat 내림차순으로 정렬해 에이전트에게 주입하고, heat 구간별 시각 우선순위 표시(🔥 단계)를 붙인다. 인덱스가 곧 recall 우선순위 표면이다.
- **PersonaTrigger** (`src/core/persona/persona-trigger.ts`): 재증류 트리거 5조건, 우선순위 평가 — P1 명시 요청 → P2 콜드스타트(장면 있고 persona 없음) → P2.5 복구(persona.md 본문 소실) → P3 첫 장면 추출 → P4 임계치(`memories_since_last_persona >= interval`).
- **스토리지**: 로컬 sqlite-vec 우선, Tencent 클라우드 VDB(tcvdb)는 선택적 마이그레이션 대상. 형태소(jieba)+벡터 하이브리드. LLM 증류는 `@ai-sdk/openai` 로 자체 호출.

## 2. naite 와의 구조 대응

| 그들 | naite | 판정 |
|---|---|---|
| L0 원본 대화 | 세션 트랜스크립트 (호스트 보관) | 동형 |
| L1 기록 추출 | rings / capture | 동형 |
| L2 Scene Block (META+heat) | tree 노트 (5-facet frontmatter) | naite 가 분류는 깊고(facet 5), **사용 신호는 없음(heat 부재)** |
| L3 Persona 자동 증류 | SOUL.md·개인 프로필 (수동/care 경유) | naite 는 **재증류 트리거가 없음** — 사람이 때를 판단 |
| heat 정렬 내비게이션 | index/MOC (큐레이션 순서) | naite 인덱스는 정적, 그들은 사용 온도 동적 정렬 |
| 심볼릭 단기기억 | (없음 — 호스트의 컨텍스트 관리에 위임) | 제품 범위 판단 필요 |
| 벤치마크 공개 (PersonaMem 등) | 없음 | **가장 아픈 갭** — 효과 주장을 증거로 못 뒷받침 |

## 3. 로드맵 채택 후보 (우선순위순)

1. **heat 메타 + 온도 정렬 내비게이션** — tree 노트 frontmatter 에 사용 온도(`heat`/`last_used`)를 두고, index/ask recall 이 온도를 정렬 신호로 쓴다. care(가지치기·병합)의 판단 근거로도 쓴다. 마당 하네스에는 2026-07-22 `scripts/memory-heat.js` 로 선행 이식됨 — 제품화 시 그 실측 교훈(일반 단어 슬러그 오탐 → 파일명 형태 매칭, 동명 슬러그 프로젝트 귀속)을 그대로 가져올 것.
2. **재증류 트리거** — "증거가 쌓이면 정체성 문서를 다시 증류할 때다" 를 자동 감지. 그들의 5조건 중 임계치·명시요청은 그대로 유효하고, 마당 이식판은 모순(최우선)·반복·시간 트리거를 추가했다(`scripts/persona-trigger.js`). naite 제품에서는 grow/care 사이클에 "재증류 제안" 으로 노출하되 실행은 항상 사용자 게이트.
3. **평가 방법론** — PersonaMem 류 장기기억 벤치마크로 naite 의 효과를 수치화. "연속 장기 세션" 조건(고립 턴 아님)이 핵심 설계다. 최소 버전: 동일 과제를 naite on/off 로 반복해 재설명 비용(토큰·턴)을 재는 자체 벤치.

## 4. 채택하지 않는 것 (이유 포함)

- **런타임 코드 전체**: OpenClaw 플러그인 API 에 결박(peer dependency). naite 는 Claude Code·Codex 양 레인 스킬/플러그인이라 구조가 다르다.
- **자체 LLM 호출 증류**(@ai-sdk/openai): naite 는 호스트 세션 안에서 증류하는 설계(비용·프라이버시 단일 통제)를 유지한다.
- **클라우드 VDB 마이그레이션 경로**: naite 는 로컬-우선·파일-우선. 벡터 검색이 필요해지면 기존 shared-pgvector 계열로.
- **🔥 이모지 내비게이션**: 마당 출력 규칙(이모지 금지)과 충돌. 온도 표기는 숫자/텍스트로.

## 5. Provenance

- 스카우트: 마당 recruit (2026-07-22), 판정 대화 및 승인 = 사용자 (heat 는 기억 수준 채택, 재증류 트리거 심화 후 채택, 제품 벤치마킹 채택).
- 이식 형태: idea-port (개념 증류, 코드 미복사). MIT 라 코드 인용이 필요해지면 가능하나 현재 불필요.
- 마당 측 구현: `~/.claude/scripts/memory-heat.js`, `~/.claude/scripts/persona-trigger.js`, rr SKILL 배선. REGISTRY census 행 참조.
