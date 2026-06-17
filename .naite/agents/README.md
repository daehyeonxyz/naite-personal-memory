# .naite/agents — 나무별 서브에이전트 정의

여기에는 **나무 하나당 하나씩** 서브에이전트 정의(`naite-<tree>.md`)가 들어간다. 각 정의는 그 나무를
전담하는 에이전트의 페르소나 + `--tree <id>` 스코프 + 다른 나무로 잇는 다리(bridge)를 담는다.

목적은 **토대**다. 이후 디스코드 봇이나 다른 헤드리스 클라이언트가 나무별로 이 정의를 로드해, 사용자가
특정 나무에게 바로 말을 걸 수 있게 한다 (봇 연결 자체는 이 저장소 범위 밖).

## 생성

forest-manifest 가 있으면 (`.naite/scripts/forest-assign.py --write` 로 생성):

```
python .naite/scripts/gen-subagents.py            # naite-<tree>.md 기록
python .naite/scripts/gen-subagents.py --dry-run  # 미리보기
```

naite-app 도 같은 형식을 만든다 (`src/vault/forest.ts` 의 `buildSubagentDefs` — 더 풍부한
줄기/허브 토폴로지 포함). 두 생성기는 같은 .md 형식을 따른다.

## 형식

```
---
name: naite-<tree>
description: <표시이름> 나무 전담 ...
tree: <tree>
---

# <표시이름> subagent
...범위 / 다른 나무로 잇는 다리 / 일하는 법...
```

## 재생성 / 커밋

생성물은 vault 내용에서 파생되므로 나무가 자라면 다시 생성한다 (`/naite care` 흐름에 묶어도 된다).
봇이 읽도록 커밋해 둘지, 매번 생성할지는 선택이다. 여기엔 손으로 쓴 내용을 두지 않는다 — 전부 생성물이다.
