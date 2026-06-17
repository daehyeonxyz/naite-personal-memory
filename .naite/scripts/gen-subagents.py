#!/usr/bin/env python3
"""gen-subagents — 나무별 서브에이전트 정의(.md)를 생성한다.

`.naite/ontology/forest-manifest.json` 의 per-tree 정보(label/description/by_kind/
self_containment + bridges)를 읽어 `.naite/agents/naite-<tree>.md` 를 쓴다. 각 정의는 그 나무를
전담하는 에이전트 페르소나 + `--tree <id>` 스코프 + 다른 나무로 잇는 다리를 담는다.
이후 디스코드 봇 등 헤드리스 클라이언트가 나무별로 로드한다 (토대만 — 봇 연결은 범위 외).

naite-app 의 `src/vault/forest.ts` buildSubagentDefs 와 같은 형식을 따른다.
형식·의도는 `.naite/agents/README.md` 참조.

사용:
  python .naite/scripts/gen-subagents.py            # .naite/agents/ 에 기록
  python .naite/scripts/gen-subagents.py --dry-run  # 쓰지 않고 미리보기
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

NAITE_ROOT = Path(__file__).resolve().parent.parent.parent
FOREST_PATH = NAITE_ROOT / ".naite" / "ontology" / "forest-manifest.json"
AGENTS_DIR = NAITE_ROOT / ".naite" / "agents"


def prettify(domain: str) -> str:
    return " ".join(w[:1].upper() + w[1:] for w in re.split(r"[-/]", domain) if w)


def build_md(tree: dict, vault: str, bridges: list[dict]) -> str:
    tid = tree["tree"]
    name = tree.get("label") or prettify(tid)
    desc = tree.get("description", "")
    pages = tree.get("page_count", 0)
    sc = round((tree.get("self_containment") or 0) * 100)
    kinds = ", ".join(f"{k} {n}" for k, n in (tree.get("by_kind") or {}).items())
    out = [
        "---",
        f"name: naite-{tid}",
        f"description: {name} 나무 전담. 이 나무의 개념·결정·작업 이력을 근거로 답하고, 범위를 벗어나면 해당 나무로 넘긴다.",
        f"tree: {tid}",
        "---",
        "",
        f"# {name} subagent",
        "",
        f"{vault} 지식 나무의 **{name}** (`{tid}`) 나무를 전담하는 에이전트입니다."
        + (f" {desc}" if desc else ""),
        "",
        "## 범위",
        f"- 이 나무(`{tid}`)의 잎을 근거로 답합니다. naite 명령은 `--tree {tid}` 로 스코프합니다.",
        f"- 페이지 {pages}개, 자족도 {sc}%." + (f" 구성: {kinds}." if kinds else ""),
        "",
    ]
    mine = [b for b in bridges if b.get("primary") == tid]
    if mine:
        out.append("## 다른 나무로 잇는 다리")
        for b in mine[:12]:
            out.append(f"- [[{b['slug']}]] → {b.get('secondary', '')}")
        out.append("")
    out += [
        "## 일하는 법",
        "- 읽기: `naite_ask` (mode=search|page|neighbors) 로 이 나무를 근거로 답합니다.",
        "- 남기기: 대화에서 건진 것은 `naite_capture` 로 스테이징하고, 잎 작성은 `/naite grow` 에 맡깁니다.",
        "- 나무에 없는 것은 지어내지 말고 없다고 말합니다.",
        "",
    ]
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="쓰지 않고 생성될 내용만 출력.")
    args = ap.parse_args()

    if not FOREST_PATH.exists():
        print(f"forest-manifest.json 이 없습니다 ({FOREST_PATH}).")
        print("먼저 `.naite/scripts/forest-assign.py --write` 로 manifest 를 생성하세요.")
        return
    data = json.loads(FOREST_PATH.read_text(encoding="utf-8"))
    trees = data.get("trees", [])
    bridges = data.get("bridges", [])
    vault = NAITE_ROOT.name
    if not trees:
        print("manifest 에 나무가 없습니다 — 자란 vault 가 필요합니다.")
        return
    if not args.dry_run:
        AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    for t in trees:
        md = build_md(t, vault, bridges)
        path = AGENTS_DIR / f"naite-{t['tree']}.md"
        if args.dry_run:
            print(f"# would write {path} ({len(md)} chars)")
        else:
            path.write_text(md, encoding="utf-8")
            print(f"wrote {path}")
    print(f"{len(trees)} subagent(s).")


if __name__ == "__main__":
    main()
