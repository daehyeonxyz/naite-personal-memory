# naite

**누가 물려주는 기록이 아니라, 내가 직접 쌓아가는 기록.**

naite is a personal knowledge system maintained by an LLM. You add sources and ask questions; an agent (Claude Code or Codex) reads them and writes connected Markdown pages you own. The conventions and structure are reusable.

naite는 LLM이 관리하는 개인 지식 시스템입니다. 사용자가 자료를 넣고 질문하면, 에이전트(Claude Code 또는 Codex)가 자료를 읽고 사용자가 소유하는 Markdown 페이지를 쓰고 서로 연결합니다. 구조와 규칙은 재사용 가능합니다.

이름은 **나이테**에서 왔습니다. 나무가 해마다 안에서부터 더하는 성장 테를 뜻합니다.

## Why naite

요즘 우리는 이미 인공지능 위에서 공부하고 일합니다. 강의자료는 AI 챗봇에 넣고, 과목별로 ChatGPT Projects나 Claude Projects를 만들고, 프로젝트를 하면서는 Codex, Claude Code, Cursor 같은 도구와 계속 대화합니다.

문제는 그 경험이 끝난 뒤입니다. 채팅 기록은 남아 있고, 발표자료도 저장되어 있고, 코드는 GitHub에 있습니다. 겉으로 보면 전부 저장되어 있습니다. 하지만 나중에 다시 쓰려고 하면 무엇이 어디에 있는지 모르고, 알아도 다음 질문과 다음 프로젝트의 맥락으로 바로 이어지지 않습니다.

**저장되어 있다는 것과 쌓였다는 것은 다릅니다.**

naite가 담는 것은 일반 백과사전이 아니라 **사용자가 아는 것**입니다. 그 앎은 두 갈래입니다.

- 스스로 알아낸 것: 결정, 프로젝트, 통찰, 아직 풀지 못한 질문.
- 밖에서 배운 것: 강의 노트, 논문 요약, 아티클, 공식 문서.

두 갈래는 같은 그래프에 함께 있으며 서로 링크됩니다. 결정 페이지가 강의에서 배운 개념을 인용하고, 그 개념이 다른 페이지에서 다시 쓰입니다. 두 레이어를 한 그래프에 두는 것이 핵심입니다. 분리하면 둘 사이의 링크가 사라집니다.

페이지를 쓰는 일은 LLM이 맡습니다. 사용자는 자료를 고르고 질문하고 중요한 것을 짚습니다. 위키는 쌓일수록 더 쓸모 있어집니다.

## 나무 모델

naite는 살아서 자라는 나무로 이해합니다. 자료가 뿌리로 들어와, 줄기로 구조화되고, 잎에서 이해가 되고, 열매로 수확해 다음에 다시 쓰며, 그 과정이 나이테로 누적됩니다.

| 나무 | 의미 | 레이어 / kind |
|---|---|---|
| 씨앗 seed | 앞으로 만들 페이지 후보 | `wiki/_stubs.md` |
| 뿌리 root | 자료 유입 | `raw/` + `kind=source-record` |
| 줄기 trunk | 구조 | `wiki/index.md` |
| 잎 leaf | 이해가 일어나는 지식 페이지 | `kind=concept`, `source-record`, `insight` |
| 열매 fruit | 다시 쓰는 결과물 | `kind=decision` (+`insight`) |
| 나이테 rings | 시간 성장 기록 | `wiki/log.md` |

## Quick Start

1. 이 저장소를 클론하거나 템플릿으로 새 저장소를 만듭니다.
2. Claude Code (또는 Codex CLI) 로 저장소 루트를 엽니다.
3. 첫 자료를 넣고 말합니다.

```text
/wiki study <path>     # 방금 공부한 자료(PDF, 아티클, 대화)를 위키에 반영
/wiki course           # 과목 단위 학습 (다챕터, 학기 단위)
/wiki query <질문>      # 쌓인 위키에 질문
/wiki lint             # 건강 점검 (고아 페이지, 스키마 drift, secrets)
```

처음부터 모든 경험을 정리할 필요는 없습니다. 강의자료 하나, 대화 하나, 프로젝트 회고 하나만 있어도 시작할 수 있습니다.

### Commands

| Command | When to use |
|---|---|
| `/wiki study [path?]` | 한 번의 공부, 대화, 자료 묶음을 기록으로 정리할 때 |
| `/wiki course [args?]` | 과목, 챕터, 강의 시리즈처럼 이어지는 학습을 관리할 때 |
| `/wiki query <question>` | 이미 쌓인 기록을 바탕으로 질문할 때 |
| `/wiki ingest <path>` | `raw/` 의 원본 파일 하나를 위키 페이지로 변환할 때 |
| `/wiki capture [topic?]` | 지금 대화의 핵심 주장을 `raw/conversations/` 에 스냅샷할 때 |
| `/wiki synapse [topic?]` | 결정·trade-off·실패 분석을 의사결정 페이지로 박을 때 |
| `/wiki lint` | 결정적 건강 점검 (report-only) |
| `/wiki curate [scope?]` | 정성적 검토, 수선, 대규모 정리 |

## Repository structure

```text
naite/
  README.md              # 시작 문서
  CLAUDE.md              # Claude Code bootloader
  AGENTS.md              # Codex bootloader (auto-mirrored)
  CONTEXT.md             # context loading rules
  CONVENTIONS.md         # operating invariants
  ARCHITECTURE.md        # schema rationale

  raw/                   # source of truth (content-immutable)
    articles/            # 논문·아티클 원본
    conversations/       # 대화 claim summary (+ _transcripts/)
    courses/             # 과목별 강의자료 staging
    assets/              # 이미지 등

  wiki/                  # LLM-owned knowledge pages (flat)
    index.md             # curated 진입점
    log.md               # append-only audit trail
    _stubs.md            # 앞으로 만들 페이지 후보

  ontology/              # canonical vocabularies + generated agent maps
    subject-tree.md      # SKOS-lite subject taxonomy
    topics.md            # folksonomy topic governance

  .claude/skills/wiki/   # Claude Code workflow contracts
  .agents/skills/wiki/   # Codex mirror (scripts/sync-agents.ps1 로 재생성)
  scripts/               # lint, map build, mirror sync
```

## Dual surface

naite 는 두 에이전트 표면을 동기화합니다. `.claude/` + `CLAUDE.md` 가 canonical 편집 대상이고, `.agents/` + `AGENTS.md` 는 `scripts/sync-agents.ps1` 로 재생성하는 Codex 미러입니다. `CONTEXT.md`, `CONVENTIONS.md`, `ARCHITECTURE.md`, `ontology/` 는 양쪽이 공유합니다.

## Positioning

naite는 AI 챗봇 대체품이 아닙니다. ChatGPT나 Claude보다 더 똑똑한 답변 도구가 되려는 프로젝트도 아닙니다. Obsidian을 직접 잘 쓰는 사람만을 위한 템플릿도 아닙니다.

naite는 기존 도구를 쓴 결과를 내가 소유하는 기록으로 다시 가져오고, 그 기록을 다음 질문과 다음 선택에 재사용하게 만드는 하네스입니다.

계보: Karpathy 의 LLM Wiki 패턴, second-brain 계열의 개인 지식 관리 위에 있습니다.

## License

MIT
