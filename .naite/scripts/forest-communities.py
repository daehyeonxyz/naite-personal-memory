#!/usr/bin/env python3
"""forest-communities.py — read-only 분화 신호 진단 (S1: 구조 신호).

tree-dependencies.json 의 wikilink + soft-relation 그래프 위에서 커뮤니티를 찾고,
각 커뮤니티의 conductance(군집 밖으로 새는 비율), 크기, 지배 도메인, 내부 hub 를
리포트한다. 나무 분화 임계의 구조 신호(S1)를 눈으로 보기 위한 프로토타입.

설계 근거: docs/CONVENTIONS.md § Forest layer, docs/ARCHITECTURE.md § 9.

READ-ONLY. 트리·ontology 파일을 수정하지 않는다. 출력은 stdout 리포트뿐이다.

가중치 정책:
  - builds-on / instance-of / extends : 강한 의미 결합 (높은 가중)
  - applies-to                        : 중간
  - see-also / 평문 wikilink          : 약한 결합 (강제 링크가 여기 숨는다)
  - 시냅스 idiom (decided-over / trade-off / validates / falsifies /
    contradicts / failed-when)        : intra-tree 클러스터링에서 제외.
    이들은 본래 군집을 가로지르는 inter-tree 연결 조직이므로, 클러스터링
    가중에서 빼고 cross-community 비율을 따로 보고한다.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx
from networkx.algorithms.community import louvain_communities

NAITE_ROOT = Path(__file__).resolve().parent.parent.parent
DEPS_PATH = NAITE_ROOT / ".naite" / "ontology" / "tree-dependencies.json"
MANIFEST_PATH = NAITE_ROOT / ".naite" / "ontology" / "tree-manifest.json"

# 클러스터링에 쓰는 결합 가중. 평문 wikilink 는 BASE_WEIGHT.
RELATION_WEIGHT = {
    "builds-on": 3.0,
    "instance-of": 3.0,
    "extends": 3.0,
    "applies-to": 2.0,
    "see-also": 1.0,
}
BASE_WEIGHT = 1.0
# 군집을 가로지르도록 설계된 시냅스 layer. 클러스터링 가중에서 제외하고 따로 측정한다.
SYNAPSE_RELATIONS = {
    "decided-over",
    "trade-off",
    "validates",
    "falsifies",
    "contradicts",
    "failed-when",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def page_domain(meta: dict) -> str:
    """페이지의 대표 도메인을 한 개 문자열로. 없으면 '(none)'."""
    for key in ("domains", "subject"):
        val = meta.get(key)
        if isinstance(val, list) and val:
            top = str(val[0]).split("/")[0]
            return top
        if isinstance(val, str) and val:
            return val.split("/")[0]
    return "(none)"


def build_graph(deps: dict, pages: dict):
    """기존 페이지 사이의 무방향 가중 그래프를 만든다. 클러스터링 가중에는
    시냅스 idiom 을 넣지 않는다. 시냅스 edge 는 별도 리스트로 반환한다."""
    existing = set(pages.keys())

    # (a,b) 무순 -> 이 edge 에 붙은 관계 집합
    edge_relations: dict[frozenset, set[str]] = defaultdict(set)

    # 평문 wikilink (outbound) — 존재하는 페이지 사이만.
    for src, targets in deps.get("outbound", {}).items():
        if src not in existing:
            continue
        for tgt in targets:
            if tgt in existing and tgt != src:
                edge_relations[frozenset((src, tgt))]  # touch -> 평문 edge 등록

    # 타입별 soft relation.
    for src, rel, tgt in deps.get("relation_edges", []):
        if src in existing and tgt in existing and src != tgt:
            edge_relations[frozenset((src, tgt))].add(rel)

    G = nx.Graph()
    G.add_nodes_from(existing)
    synapse_edges: list[tuple[str, str, str]] = []

    for pair, rels in edge_relations.items():
        a, b = tuple(pair) if len(pair) == 2 else (next(iter(pair)), next(iter(pair)))
        if a == b:
            continue
        # 시냅스 관계는 따로 기록.
        for rel in rels:
            if rel in SYNAPSE_RELATIONS:
                synapse_edges.append((a, rel, b))
        # 클러스터링 가중: 시냅스 제외 관계의 최대 가중, 없으면 BASE.
        cluster_rels = [r for r in rels if r not in SYNAPSE_RELATIONS]
        if cluster_rels:
            w = max(RELATION_WEIGHT.get(r, BASE_WEIGHT) for r in cluster_rels)
        else:
            w = BASE_WEIGHT
        G.add_edge(a, b, weight=w)

    return G, synapse_edges


def conductance(G: nx.Graph, community: set) -> float:
    """가중 conductance: 군집 밖으로 나가는 가중 / min(vol(S), vol(V\\S))."""
    cut = 0.0
    vol_s = 0.0
    total_vol = 0.0
    for n in G:
        deg = G.degree(n, weight="weight")
        total_vol += deg
    for n in community:
        vol_s += G.degree(n, weight="weight")
        for nbr in G[n]:
            w = G[n][nbr]["weight"]
            if nbr not in community:
                cut += w
    vol_rest = total_vol - vol_s
    denom = min(vol_s, vol_rest)
    return cut / denom if denom > 0 else 0.0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--resolution", type=float, default=1.0,
                    help="Louvain resolution. 높을수록 더 잘게 쪼갬 (default 1.0).")
    ap.add_argument("--seed", type=int, default=42, help="결정성 seed.")
    ap.add_argument("--min-size", type=int, default=15,
                    help="분화 후보로 surface 할 최소 군집 크기 (size floor).")
    ap.add_argument("--max-conductance", type=float, default=0.15,
                    help="분화 후보 conductance 상한. 이보다 낮으면 잘 분리된 군집.")
    ap.add_argument("--top-hubs", type=int, default=4, help="군집별 표시할 hub 수.")
    args = ap.parse_args()

    deps = load_json(DEPS_PATH)
    manifest = load_json(MANIFEST_PATH)
    # manifest['pages'] 는 레코드 리스트. slug -> meta 로 변환하고 special 파일 제외.
    pages = {
        rec["slug"]: rec
        for rec in manifest.get("pages", [])
        if not rec.get("special", False)
    }
    inbound_counts = deps.get("inbound_counts", {})

    G, synapse_edges = build_graph(deps, pages)
    if G.number_of_nodes() == 0:
        print("# forest-communities — 콘텐츠 페이지가 없어 군집을 만들 수 없습니다 "
              "(Phase 1: 빈/단일 나무).")
        return
    largest_cc = max(nx.connected_components(G), key=len) if G.number_of_nodes() else set()

    communities = louvain_communities(
        G, weight="weight", resolution=args.resolution, seed=args.seed
    )
    communities = sorted(communities, key=len, reverse=True)
    Q = nx.algorithms.community.modularity(G, communities, weight="weight")

    # community id 매핑.
    node_comm: dict[str, int] = {}
    for cid, comm in enumerate(communities):
        for n in comm:
            node_comm[n] = cid

    print(f"# forest-communities — S1 구조 신호 진단")
    print(f"nodes: {G.number_of_nodes()} | edges: {G.number_of_edges()} "
          f"| largest connected component: {len(largest_cc)}")
    print(f"louvain communities: {len(communities)} | modularity Q = {Q:.4f} "
          f"(resolution={args.resolution}, seed={args.seed})")
    print(f"분화 후보 기준: size >= {args.min_size} AND conductance <= {args.max_conductance}")
    print()

    candidates = []
    for cid, comm in enumerate(communities):
        if len(comm) < 3:
            continue
        cond = conductance(G, comm)
        dom_counter = Counter(page_domain(pages.get(n, {})) for n in comm)
        top_domains = dom_counter.most_common(3)
        dom_purity = top_domains[0][1] / len(comm) if top_domains else 0.0
        hubs = sorted(comm, key=lambda n: inbound_counts.get(n, 0), reverse=True)
        hub_str = ", ".join(
            f"{h}({inbound_counts.get(h, 0)})" for h in hubs[: args.top_hubs]
        )
        dom_str = ", ".join(f"{d}:{c}" for d, c in top_domains)
        flag = ""
        if len(comm) >= args.min_size and cond <= args.max_conductance:
            flag = "  <== 분화 후보 (잘 분리된 큰 군집)"
            candidates.append((cid, len(comm), cond, top_domains[0][0]))
        print(f"[C{cid:02d}] size={len(comm):4d}  conductance={cond:.3f}  "
              f"purity={dom_purity:.2f}{flag}")
        print(f"      domains: {dom_str}")
        print(f"      hubs:    {hub_str}")

    # 시냅스 layer: cross-community 비율.
    cross = same = 0
    for a, _rel, b in synapse_edges:
        ca, cb = node_comm.get(a), node_comm.get(b)
        if ca is None or cb is None:
            continue
        if ca == cb:
            same += 1
        else:
            cross += 1
    total = cross + same
    print()
    print("# 시냅스 layer (decided-over / trade-off / validates / falsifies / "
          "contradicts / failed-when)")
    if total:
        print(f"시냅스 edge {total}개 중 cross-community {cross} "
              f"({cross / total:.0%}), within-community {same} ({same / total:.0%})")
        print("→ cross 비율이 높을수록 시냅스가 군집을 가로지르는 inter-tree 연결 조직이라는 가설을 지지한다.")
    else:
        print("시냅스 edge 없음.")

    print()
    print(f"# 요약: 분화 후보 군집 {len(candidates)}개")
    for cid, size, cond, dom in candidates:
        print(f"  - C{cid:02d}: {size} pages, conductance {cond:.3f}, 지배 도메인 '{dom}'")


if __name__ == "__main__":
    import sys
    try:  # keep non-ASCII report output from crashing a cp949/legacy Windows console
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    main()
