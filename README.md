<p align="center">
  <img src="assets/naite-banner.png" alt="naite" width="640" />
</p>

<p align="center"><em>내가 소유하는 개인 지식 시스템. 내 에이전트들이 함께 쓰는 두뇌.</em></p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-7cc15a" alt="MIT" />
  <img src="https://img.shields.io/badge/version-0.8.7-a9621f" alt="v0.8.7" />
  <img src="https://img.shields.io/badge/Claude_Code-ready-a9621f" alt="Claude Code" />
  <img src="https://img.shields.io/badge/Codex-ready-7cc15a" alt="Codex" />
  <img src="https://img.shields.io/badge/Obsidian-compatible-a9621f" alt="Obsidian" />
</p>

naite는 내가 아는 것을 쌓아 두는 개인 지식 시스템입니다. 자료를 넣고 질문을 던지면, 유지 관리자 역할을 맡은 에이전트가 자료를 읽고 서로 연결된 페이지로 정리합니다. 이 페이지들이 모이는 폴더가 여러분의 vault입니다.

넣을 수 있는 자료에 제한은 없습니다. AI와 나눈 대화, 강의 자료, 유튜브 영상, 뉴스, 논문, 프로젝트 기록까지, 내 지식이 될 만한 것이라면 무엇이든 재료가 됩니다.

그중에서도 AI와 나눈 대화는 보통 그 서비스 안에 갇혀 있습니다. naite는 그 기록을 꺼내 와 평문 Markdown으로 여러분의 Git 저장소에 남깁니다. 어떤 서비스에도 묶이지 않은, 온전히 내 소유의 기록입니다.

이렇게 한 번 쌓아 두면, 이 vault를 여는 어떤 에이전트든 나를 아는 채로 대화를 시작합니다. 예를 들어 관심 있는 채용 공고를 하나 던지면, 일반적인 조언 대신 내가 배운 것과 만들어 온 것을 근거로 지금 무엇이 준비되어 있고 무엇이 부족한지 짚어 줍니다. 에이전트를 바꿔도, 세션이 끝나도, 같은 기록 위에서 대화가 이어집니다.

이름은 나무의 나이테에서 왔습니다. 나무가 해마다 안쪽부터 테를 더하며 자라듯, 여러분의 기록도 덮어쓰이지 않고 겹겹이 쌓이며 자랍니다. 이 아이디어는 Andrej Karpathy가 제안한 LLM Wiki 패턴에서 출발했습니다.

<p align="center">
  <img src="assets/app-forest.png" alt="데스크톱 앱의 숲 대시보드" width="820" />
</p>
<p align="center"><em>데스크톱 앱에서 본 숲입니다. 지식이 얼마나 쌓였고 지금 어디가 자라는 중인지 한눈에 보여 줍니다.</em></p>

## 어떻게 동작하나

vault는 Markdown 파일이 담긴 폴더 하나이고, naite는 이 폴더를 나무 한 그루로 봅니다.

| 나무 | 실제로는 |
|---|---|
| 뿌리 | 내가 넣은 원본 자료 (`roots/`) |
| 잎 | 에이전트가 정리한 지식 페이지 (`tree/`) |
| 맥 | 페이지 사이의 링크 (`[[wikilink]]`) |
| 열매 | 결정과 인사이트처럼 다시 꺼내 쓰는 결과물 |
| 나이테 | 시간순으로 남는 성장 기록 |

자료를 넣으면 뿌리에 쌓이고, 에이전트가 그것을 읽어 잎을 만들고, 잎과 잎을 맥으로 잇습니다. 고민 끝에 내린 결정은 열매로 남고, 이 모든 성장은 나이테에 시간순으로 기록됩니다. 여러분이 할 일은 자료를 고르고 질문하는 것뿐입니다.

벡터 DB 같은 무거운 장치는 필요 없습니다. 전부 평문 Markdown이라 가볍고, Git으로 그대로 옮기거나 공유할 수 있으며, Obsidian으로 열면 나무가 그래프로 보입니다.

## 시작하기

Claude Code만 있으면 됩니다. vault로 쓸 폴더를 하나 만들고, 그 폴더에서 Claude Code를 연 다음 아래 한 줄을 붙여넣으세요.

```text
naite 를 설치하고 이 폴더를 내 vault 로 시작해줘. `claude plugin marketplace add daehyeonxyz/naite-personal-memory` 와 `claude plugin install naite@naite` 를 실행한 뒤, 설치된 naite 플러그인의 start 절차를 읽고 그대로 따라줘.
```

이 한 줄로 설치부터 첫 기록까지 이어집니다. 에이전트가 naite 플러그인을 설치하고, 이 폴더를 여러분의 vault로 만든 뒤, 첫 나무 심기를 안내합니다. ChatGPT, Claude, Gemini에서 내보낸 대화 기록을 첨부하면 붙여넣은 정보를 바탕으로 나와 관련된 페이지들이 바로 나이테에 기록됩니다. 이렇게 스스로에 대한 여러 정보를 기록하고, 기록된 정보를 바탕으로 새로운 학습을 해 나갈수록 여러분의 나이테는 더 겹겹이 쌓일 것입니다.

다음부터는 어디서든 `/naite`로 시작하면 됩니다. 명령이 헷갈리면 그냥 "naite 시작하자"라고 말해도 같은 흐름으로 이어집니다.

<details>
<summary>명령을 직접 치고 싶다면</summary>

```text
/plugin marketplace add daehyeonxyz/naite-personal-memory
/plugin install naite
```

설치한 뒤 vault 폴더에서 `/naite start`를 실행하세요.

</details>

### 이미 vault가 있다면

`~/.naite/root` 파일에 vault 경로를 한 줄 적어 두세요. 그다음부터는 어느 폴더에서 열어도 `/naite`가 여러분의 vault로 연결됩니다.

### Codex를 쓰거나 직접 설치하려면

플러그인 없이 저장소를 직접 복사해 시작할 수도 있습니다. 개인 기록이 담기므로 Private 저장소를 권장합니다. 새 저장소를 만들어 클론한 폴더에서 에이전트를 열고, 아래를 붙여넣으세요.

```text
https://github.com/daehyeonxyz/naite-personal-memory 를 이 폴더에 설치해줘.

1. 위 저장소를 임시 폴더에 클론한 다음, .git 을 제외한 모든 파일을 이 폴더 루트로 복사해.
2. 복사가 끝나면 임시 폴더를 지우고, `.naite/PUBLIC_STARTER` 파일이 있으면 지워. 그다음 CLAUDE.md (Codex 라면 AGENTS.md) 를 읽어.
3. `git config core.hooksPath .naite/hooks` 로 가드 훅을 켜.
4. "naite install" 메시지로 첫 커밋을 만들어줘.
5. 끝나면 내가 지금 바로 해볼 수 있는 것을 한두 가지 알려줘.
```

가드 훅은 비밀키나 개인정보가 실수로 커밋되는 것을 막아 주는 안전장치입니다.

## 데스크톱 앱

쌓인 나무를 눈으로 보고 싶을 때는 데스크톱 앱을 엽니다. 나무를 보고, 찾고, 에이전트에게 일을 맡길 수 있습니다.

<p align="center">
  <img src="assets/app-tree.png" alt="나무 그래프 화면" width="820" />
</p>
<p align="center"><em>여러 페이지가 어떤 관계로 이어져 있는지를 그래프뷰로 볼 수 있습니다.</em></p>

<p align="center">
  <img src="assets/app-home.png" alt="홈 화면" width="820" />
</p>
<p align="center"><em>쌓인 지식을 아는 에이전트에게 무엇이든 맡길 수 있습니다.</em></p>

[최신 릴리스](https://github.com/daehyeonxyz/naite-app-releases/releases/latest)에서 내려받으세요. 설치만 하면, 새 버전은 자동으로 업데이트됩니다.

- Windows: `naite_*_x64-setup.exe`
- macOS: `naite_*_universal.dmg`
- Linux: `naite_*_amd64.AppImage`

## 명령어

자주 쓰는 명령은 이 정도입니다.

| 명령 | 언제 쓰나 |
|---|---|
| `/naite start` | 처음 시작할 때 |
| `/naite grow` | 공부한 내용과 보관해 놓은 자료를 나무에 반영할 때 |
| `/naite grow backfill` | 예전에 공부했던 자료들을 한번에 노트로 정리하고 싶을 때 |
| `/naite ask` | 쌓인 기록을 바탕으로 질문할 때 |
| `/naite fruit` | 결정이나 고민의 결론을 남기고 싶을 때 |
| `/naite care --check` | 나무 상태를 점검하고 싶을 때 |
| `/naite care` | 나무를 다듬고 정리할 때 |
| `/naite upgrade` | 새 버전이 업데이트됐을 때 |

외울 필요는 없습니다. 자료를 붙여넣고 "반영해줘"라고만 해도 에이전트가 알맞은 흐름을 찾아갑니다.

## 에이전트를 나에게 맞추기

세 파일이 나를 기억합니다. 모두 평범한 Markdown이라 직접 고칠 수 있습니다.

- `SOUL.md`: 에이전트의 말투. 톤을 바꾸고 싶으면 이 파일을 고칩니다.
- `USER.md`: 내가 선호하는 답변 방식. 비워 두고 시작해도 됩니다.
- `MEMORY.md`: 진행 중인 작업 메모.

`USER.md`와 `MEMORY.md`는 개인 정보라 Git에 올라가지 않습니다.

### vault를 다른 컴퓨터로 옮길 때

vault는 Git 저장소라 clone 하면 그대로 옮겨집니다. 새 컴퓨터에서 두 가지만 챙기세요.

1. 새 폴더에서 `git config core.hooksPath .naite/hooks`를 한 번 실행해 가드 훅을 다시 켭니다.
2. `USER.md`와 `MEMORY.md`는 Git에 없으니 예전 폴더에서 직접 복사합니다.

## 더 알아보기

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): 왜 이런 구조인지
- [docs/CONVENTIONS.md](docs/CONVENTIONS.md): 페이지가 지키는 규칙
- [docs/CONTEXT.md](docs/CONTEXT.md): 에이전트가 무엇을 읽는지
- [docs/connect-mcp.md](docs/connect-mcp.md): Claude Desktop과 Codex에 MCP로 붙이기

## 기여

naite 하네스는 공개되어 있고 기여를 환영합니다. fork 해서 고친 뒤 PR을 보내 주세요. `tree/`와 `roots/`는 각자의 개인 기록이라 기여 대상이 아닙니다. 자세한 내용은 [CONTRIBUTING.md](CONTRIBUTING.md)에 있습니다.

## License

MIT
