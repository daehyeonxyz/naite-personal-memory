# naite

**누가 물려주는 기록이 아니라, 내가 직접 쌓아가는 기록.**

naite is a personal knowledge vault maintained by an LLM. You drop in sources and ask questions; an agent (Claude Code or Codex) reads them, writes linked Markdown pages you own, and keeps the whole thing coherent over time. Everything lives in one Git repository, in plain text, forever yours.

이름은 **나이테**에서 왔습니다. 나무가 한 해 한 해 안쪽에서부터 더해 가는 성장 테를 뜻합니다.

## 왜 naite 인가

우리는 이미 인공지능 위에서 공부하고 일합니다. 강의자료는 AI 챗봇 에 넣고, 과목마다 채팅 프로젝트를 만들고, 과제와 코드는 Claude Code 나 Codex 와 대화하며 만듭니다.

문제는 그 경험이 끝난 뒤입니다. 채팅 기록은 남아 있고 발표자료도 어딘가에 저장되어 있습니다. 그런데 한 학기가 지나고 나면 무엇이 어디에 있는지 모르고, 찾아도 다음 질문과 다음 프로젝트로 이어지지 않습니다.

**저장되어 있다는 것과 쌓였다는 것은 다릅니다.**

naite 가 담는 것은 백과사전이 아니라 "내가 아는 것" 입니다. 그 앎은 두 갈래입니다.

- 스스로 알아낸 것: 결정, 프로젝트, 통찰, 아직 풀지 못한 질문.
- 밖에서 배운 것: 강의 노트, 논문 요약, 아티클, 공식 문서.

두 갈래가 한 그래프 안에서 서로 링크됩니다. 내가 내린 결정이 강의에서 배운 개념을 인용하고, 그 개념이 다음 프로젝트에서 다시 쓰입니다. 분리하면 이 링크가 사라지기 때문에, 한 그래프에 두는 것이 핵심입니다.

그리고 이 기록은 읽기용 노트로 끝나지 않습니다. **naite 폴더에서 에이전트를 켜면, 에이전트는 나를 아는 상태로 시작합니다.** 예를 들어 관심 있는 채용 공고를 하나 던지면, 일반론이 아니라 내가 배운 과목과 했던 프로젝트를 근거로 어디가 준비되어 있고 어디가 비어 있는지 답해 줍니다. 기록이 쌓일수록 모든 대화의 출발점이 높아집니다.

페이지를 쓰고 정리하는 일은 LLM 이 맡습니다. 사용자는 자료를 고르고, 질문하고, 중요한 것을 짚기만 하면 됩니다. 이 구도는 Andrej Karpathy 가 정리한 LLM Wiki 패턴 위에 있습니다.

## 나무 모델

naite 는 저장소 하나를 살아서 자라는 나무 한 그루로 다룹니다. 자료가 뿌리로 들어와, 잎에서 이해가 되고, 열매로 수확되어 다음에 다시 쓰이고, 그 과정 전체가 나이테로 남습니다.

| 나무 | 의미 | 위치 |
|---|---|---|
| 뿌리 root | 원본 자료가 들어오는 곳 | `roots/` |
| 줄기 trunk | 전체 구조를 보여주는 진입점 | `tree/trunk.md` |
| 잎 leaf | 이해가 일어나는 지식 페이지 | `tree/*.md` |
| 열매 fruit | 결정, 통찰처럼 다시 꺼내 쓰는 결과물 | `kind=decision` 페이지 |
| 나이테 rings | 시간순 성장 기록 | `tree/rings.md` |
| 씨앗 seed | 앞으로 만들 페이지 후보 | `tree/seeds.md` |

잎과 잎은 맥 (vein, `[[wikilink]]`) 으로 이어집니다.

## 시작하기

필요한 것은 GitHub 계정과 Claude Code 또는 Codex 하나뿐입니다.

1. GitHub 에서 새 저장소를 만듭니다. 개인 기록이므로 **Private** 을 권장합니다.
2. 그 저장소를 클론한 폴더에서 Claude Code 또는 Codex 를 실행합니다.
3. 아래 프롬프트를 그대로 붙여넣습니다.

```text
https://github.com/daehyeonxyz/naite-personal-memory 를 이 폴더에 설치해줘.

1. 위 저장소를 임시 폴더에 클론한 다음, .git 을 제외한 모든 파일을 이 폴더 루트로 복사해.
2. 복사가 끝나면 임시 폴더를 지우고, CLAUDE.md (Codex 라면 AGENTS.md) 를 읽어.
3. "naite install" 메시지로 첫 커밋을 만들어줘.
4. 끝나면 내가 지금 바로 해볼 수 있는 것을 한두 가지 알려줘.
```

설치가 끝나면 첫 자료를 하나 던져 보세요. 강의 PDF 하나, 인상 깊었던 대화 하나면 충분합니다.

```text
/naite grow
```

처음부터 모든 경험을 정리할 필요는 없습니다. 나무는 자랄수록 더 쓸모 있어집니다.

## 명령어

| 명령 | 언제 쓰나 |
|---|---|
| `/naite grow [path?]` | 공부한 것, 던져둔 자료를 나무에 반영할 때. 대화 마무리, 파일 하나, 과목·책·시리즈 단위 전부 여기로 |
| `/naite ask <질문>` | 쌓인 기록을 바탕으로 질문할 때 |
| `/naite fruit [topic?]` | 결정, trade-off, 실패 분석을 열매로 남길 때 |
| `/naite care [scope?]` | 나무를 다듬을 때. `--check` 를 붙이면 고치지 않고 점검만 합니다 |

명령을 외울 필요는 없습니다. 그냥 자료를 붙여넣고 "반영해줘" 라고 말해도 에이전트가 알아서 맞는 흐름을 탑니다.

## 폴더 구조

사용자가 알아야 할 폴더는 두 개뿐입니다.

```text
naite/
  roots/   # 뿌리. 원본 자료가 들어오는 곳 (PDF, 대화 기록, 아티클)
  tree/    # 나무. 에이전트가 쓰고 서로 연결하는 지식 페이지
  docs/    # 더 깊은 규칙이 궁금할 때 읽는 기술 문서
```

나머지 (`.naite/`, `.claude/`, `.agents/`) 는 에이전트가 쓰는 내부 구현이라 몰라도 됩니다. Obsidian 으로 이 폴더를 열면 나무가 그래프로 보입니다.

## 더 알아보기

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): 왜 이런 구조인지, 스키마 설계 근거.
- [docs/CONVENTIONS.md](docs/CONVENTIONS.md): 페이지가 지키는 규칙들.
- [docs/CONTEXT.md](docs/CONTEXT.md): 에이전트가 무엇을 어떤 순서로 읽는지.

## naite 가 아닌 것

naite 는 AI 챗봇 대체품이 아니고, 더 똑똑한 챗봇을 만드는 프로젝트도 아닙니다. 기존 도구를 쓴 결과를 내가 소유하는 기록으로 가져오고, 그 기록을 다음 질문과 다음 선택에 재사용하게 만드는 하네스, 곧 작업 틀입니다.

## License

MIT
