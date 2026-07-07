#!/usr/bin/env python3
"""forest-dashboard.py — 나이테 forest 대시보드 생성 (그림자 단계 #2).

파일을 옮기지 않고 forest-manifest.json 만으로 '숲처럼' 운영하기 위한 표면. 평평한
tree/ 위에 forest 스코프를 투영해, 숲 메타 대시보드 + 나무별 진입 정보를 markdown 으로
생성한다. 사용자가 '나이테'라 부르기로 한 대시보드의 그림자 단계 구현이다.

입력: forest-manifest.json(개념 계보 배정), tree-manifest.json(제목·kind),
      tree-dependencies.json(inbound). 출력: .naite/forest/dashboard.md.

READ-ONLY w.r.t. tree/. forest 산출물(.naite/forest/)만 생성한다.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

NAITE_ROOT = Path(__file__).resolve().parent.parent.parent
FOREST_PATH = NAITE_ROOT / ".naite" / "ontology" / "forest-manifest.json"
MANIFEST_PATH = NAITE_ROOT / ".naite" / "ontology" / "tree-manifest.json"
DEPS_PATH = NAITE_ROOT / ".naite" / "ontology" / "tree-dependencies.json"
OUT_PATH = NAITE_ROOT / ".naite" / "forest" / "dashboard.md"


def load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> None:
    if not FOREST_PATH.exists():
        print(f"# forest-dashboard — {FOREST_PATH.name} 이 없습니다. "
              "먼저 forest-assign.py --write 를 실행하세요.")
        return
    forest = load_json(FOREST_PATH)
    manifest = load_json(MANIFEST_PATH)
    deps = load_json(DEPS_PATH)

    title = {r["slug"]: r.get("title", r["slug"]) for r in manifest.get("pages", [])}
    kind = {r["slug"]: r.get("kind", "?") for r in manifest.get("pages", [])}
    inbound = deps.get("inbound_counts", {})
    page_to_tree = forest.get("page_to_tree", {})
    desc = {t["tree"]: t.get("description", "") for t in forest.get("trees", [])}

    members: dict[str, list[str]] = defaultdict(list)
    for slug, tree in page_to_tree.items():
        members[tree].append(slug)

    # inter-tree 인접(나무별 연결 상대).
    nbr: dict[str, Counter] = defaultdict(Counter)
    for e in forest.get("inter_tree_edges", []):
        a, b = e["trees"]
        nbr[a][b] += e["count"]
        nbr[b][a] += e["count"]

    trees_sorted = sorted(forest.get("trees", []), key=lambda t: t["page_count"], reverse=True)
    bridges = forest.get("bridges", [])

    lines: list[str] = []
    w = lines.append
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    w("# 나이테 — Forest Dashboard")
    w("")
    w(f"생성 {now} · `forest-dashboard.py` · status **{forest.get('status','?')}** "
      f"(그림자 단계: 파일 미이동, forest-manifest 투영)")
    w("")
    w(f"숲: **{len(trees_sorted)} 그루**, 총 **{forest.get('page_count','?')} 페이지**. "
      f"배정 방식: {forest.get('method','?')}. 걸침 개념(bridge) {len(bridges)} 건.")
    w("")
    w("## 나무 한눈에")
    w("")
    w("| 나무 | 페이지 | 자족도 | 사상 공간 |")
    w("|---|---|---|---|")
    for t in trees_sorted:
        w(f"| {t['tree']} | {t['page_count']} | {t.get('self_containment',0):.0%} | "
          f"{t.get('description','')} |")
    w("")
    w("## 느슨한 inter-tree 결합 (라우팅 표면)")
    w("")
    top_edges = sorted(forest.get("inter_tree_edges", []), key=lambda e: e["count"], reverse=True)[:10]
    for e in top_edges:
        a, b = e["trees"]
        w(f"- {a} ↔ {b} · {e['count']}")
    w("")

    # 나무별 진입 카드.
    for t in trees_sorted:
        tree = t["tree"]
        w(f"## 🌳 {tree}")
        w("")
        w(f"{desc.get(tree,'')}  ")
        w(f"페이지 {t['page_count']} · 자족도 {t.get('self_containment',0):.0%} · "
          f"내부링크 {t.get('internal_edges',0)} · 외부링크 {t.get('external_edges',0)}")
        w("")
        # 진입 hub: 이 나무 안에서 inbound 상위.
        hubs = sorted(members[tree], key=lambda s: inbound.get(s, 0), reverse=True)[:8]
        w("진입 hub: " + ", ".join(f"[[{h}]]({inbound.get(h,0)})" for h in hubs))
        w("")
        # kind 분포.
        kinds = Counter(kind.get(s, "?") for s in members[tree])
        w("구성: " + ", ".join(f"{k} {c}" for k, c in kinds.most_common()))
        w("")
        # 연결 상대.
        if nbr[tree]:
            rel = ", ".join(f"{o}({c})" for o, c in nbr[tree].most_common(5))
            w(f"연결 나무: {rel}")
            w("")
        # 이 나무를 primary 로 하는 bridge.
        my_bridges = [b for b in bridges if b["primary"] == tree][:6]
        if my_bridges:
            w("걸침 개념(이 나무 거주, secondary 로 링크): "
              + ", ".join(f"[[{b['slug']}]]→{b['secondary']}" for b in my_bridges))
            w("")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_PATH.relative_to(NAITE_ROOT)} ({len(trees_sorted)} trees)")


if __name__ == "__main__":
    import sys
    try:  # keep non-ASCII report output from crashing a cp949/legacy Windows console
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    main()
