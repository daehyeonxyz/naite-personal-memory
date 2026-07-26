# 내 에이전트에 나무 붙이기 (MCP)

naite 나무는 [`naite-mcp`](https://www.npmjs.com/package/naite-mcp) 커넥터를 통해 **각자 자신의
Claude Code / Claude Desktop / Codex** 에서 읽고 이어붙일 수 있다. 도구는 둘이다.

- **`naite_ask`** (읽기): 나무가 아는 것에서 검색·페이지·이웃을 가져온다.
- **`naite_capture`** (쓰기): 대화에서 건진 주장을 `roots/conversations/` 에 스테이징한다. 잎으로의
  변환은 다음 naite 세션의 `/naite grow` 가 한다. 서버가 저장 전 secrets 를 검사한다.

## 전제

이 커넥터는 *이미 자란 나무*를 가리킬 때만 쓸모가 있다. 빈 폴더는 읽을 게 없다. 아직 시작 전이라면
`/naite start` 로 첫 나무를 짓는다 (플러그인 설치라면 start 가 빈 폴더에 스타터를 스캐폴드하고, 직접 클론했다면 그 폴더에서 바로 start 를 부른다). 이후는 `/naite grow`, `/naite care` 로 이어 간다.

vault 경로는 `NAITE_ROOT` 환경변수 → `--root <경로>` 인자 → 현재 디렉토리 순으로 찾는다.

## Claude Code

이 저장소의 **naite** 플러그인을 설치하면 `naite-mcp` 가 함께 등록된다. vault 는 Claude Code 를
연 프로젝트 디렉토리(`${CLAUDE_PROJECT_DIR}`)로 잡힌다.

```
/plugin marketplace add https://github.com/daehyeonxyz/naite-personal-memory
/plugin install naite
```

직접 추가하려면:

```
claude mcp add naite -e NAITE_ROOT=/절대/경로/내-vault -- npx -y naite-mcp
```

## Claude Desktop

`claude_desktop_config.json` (Windows: `%APPDATA%\Claude\`, macOS:
`~/Library/Application Support/Claude/`) 에 추가하고 재시작한다.

```json
{
  "mcpServers": {
    "naite": {
      "command": "npx",
      "args": ["-y", "naite-mcp"],
      "env": { "NAITE_ROOT": "C:/Users/<you>/projects/your-vault" }
    }
  }
}
```

## Codex

`~/.codex/config.toml` 에 추가한다.

```toml
[mcp_servers.naite]
command = "npx"
args = ["-y", "naite-mcp"]
env = { NAITE_ROOT = "C:/Users/<you>/projects/your-vault" }
```

---

`naite-mcp` 는 npm 공개 패키지다 (`npx -y naite-mcp`). vault 가 비어 있으면 읽을 게 없으니, `/naite`
스킬로 먼저 키운 다음 붙인다.
