#!/usr/bin/env python3
"""forest-retrieval-experiment.py — 검증 실험 B (단일 vault vs 숲 retrieval).

질문: 단일 monolithic vault 에서의 retrieval 이 숲(community 제한) retrieval 보다
거짓 연관(spurious association)을 더 많이 만드는가? 그 대가로 잃는 정당한
cross-domain 연결은 얼마인가? 즉 '깨끗한 사상 공간 vs 우연한 연결의 상실'
trade-off (docs/ARCHITECTURE.md § 9) 를 정량화한다.

설계 원칙: retriever 는 링크 그래프와 독립이어야 한다(안 그러면 동어반복).
그래서 TF-IDF(문자 n-gram) 콘텐츠 유사도를 retriever 로 쓴다. 군집은
forest-communities.py 와 동일한 Louvain(resolution 1.0, seed 42).

근사 ground-truth: "curated wikilink(사람이 건 링크) = 관련성 있음". 따라서
  - cross-domain AND curated   = 정당한 우연한 연결 (숲이 잃으면 손실)
  - cross-domain AND uncurated = 거짓 연관 후보 (숲이 줄이면 이득)

정직한 한계: uncurated cross-domain 이 전부 노이즈는 아니다. 일부는 아직 링크 안 된
'가치 있는 발견'(우리가 원하는 serendipity)일 수 있다. 그래서 이 실험은 trade-off 의
'크기'를 재지, validates/falsifies 의 최종 판정을 내리지 않는다. 최종 판정은 사람의
관련성 라벨이 필요하다.

READ-ONLY. 트리/ontology 를 수정하지 않는다.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import networkx as nx
from networkx.algorithms.community import louvain_communities
from sklearn.feature_extraction.text import TfidfVectorizer

NAITE_ROOT = Path(__file__).resolve().parent.parent.parent
DEPS_PATH = NAITE_ROOT / ".naite" / "ontology" / "tree-dependencies.json"
MANIFEST_PATH = NAITE_ROOT / ".naite" / "ontology" / "tree-manifest.json"

RELATION_WEIGHT = {
    "builds-on": 3.0, "instance-of": 3.0, "extends": 3.0, "applies-to": 2.0, "see-also": 1.0,
}
BASE_WEIGHT = 1.0
SYNAPSE_RELATIONS = {
    "decided-over", "trade-off", "validates", "falsifies", "contradicts", "failed-when",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    m = re.match(r"^---\r?\n.*?\r?\n---\r?\n?(.*)$", text, re.DOTALL)
    return m.group(1) if m else text


def domain_of(meta: dict) -> str:
    for key in ("domains", "subject"):
        val = meta.get(key)
        if isinstance(val, list) and val:
            return str(val[0]).split("/")[0]
        if isinstance(val, str) and val:
            return val.split("/")[0]
    return "(none)"


def build_partition(deps: dict, existing: set) -> dict[str, int]:
    edge_rel: dict[frozenset, set[str]] = defaultdict(set)
    for src, targets in deps.get("outbound", {}).items():
        if src in existing:
            for t in targets:
                if t in existing and t != src:
                    edge_rel[frozenset((src, t))]
    for src, rel, tgt in deps.get("relation_edges", []):
        if src in existing and tgt in existing and src != tgt:
            edge_rel[frozenset((src, tgt))].add(rel)
    G = nx.Graph()
    G.add_nodes_from(existing)
    for pair, rels in edge_rel.items():
        a, b = tuple(pair)
        cluster_rels = [r for r in rels if r not in SYNAPSE_RELATIONS]
        w = max((RELATION_WEIGHT.get(r, BASE_WEIGHT) for r in cluster_rels), default=BASE_WEIGHT)
        G.add_edge(a, b, weight=w)
    comms = louvain_communities(G, weight="weight", resolution=1.0, seed=42)
    node_comm = {}
    for cid, c in enumerate(comms):
        for n in c:
            node_comm[n] = cid
    return node_comm


def curated_pairs(deps: dict, existing: set) -> set[frozenset]:
    pairs = set()
    for src, targets in deps.get("outbound", {}).items():
        if src in existing:
            for t in targets:
                if t in existing and t != src:
                    pairs.add(frozenset((src, t)))
    return pairs


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--k", type=int, default=10, help="retrieval top-k (default 10).")
    ap.add_argument("--min-body", type=int, default=200,
                    help="질의로 쓸 페이지 본문 최소 길이(문자).")
    args = ap.parse_args()

    deps = load_json(DEPS_PATH)
    manifest = load_json(MANIFEST_PATH)
    recs = [r for r in manifest.get("pages", []) if not r.get("special", False)]
    meta = {r["slug"]: r for r in recs}
    existing = set(meta.keys())

    # 본문 로드.
    slugs, bodies = [], []
    for r in recs:
        path = NAITE_ROOT / r["file"]
        try:
            text = strip_frontmatter(path.read_text(encoding="utf-8-sig", errors="replace"))
        except OSError:
            continue
        slugs.append(r["slug"])
        bodies.append(text)
    if len(bodies) < 2:
        print("# forest-retrieval-experiment — 본문 페이지가 부족해 실험할 수 없습니다 "
              "(Phase 1: 빈/단일 나무).")
        return
    idx_of = {s: i for i, s in enumerate(slugs)}
    domain = {s: domain_of(meta[s]) for s in slugs}

    node_comm = build_partition(deps, existing)
    cur_pairs = curated_pairs(deps, existing)

    # TF-IDF (문자 n-gram → 언어 견고, 링크와 독립).
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2,
                          sublinear_tf=True, max_features=60000)
    X = vec.fit_transform(bodies)            # L2-normalized rows by default
    S = (X @ X.T).toarray()                  # cosine similarity matrix
    np.fill_diagonal(S, -1.0)

    # clamp k so np.argpartition kth (k) stays < n; small/new vaults have few docs.
    k = min(args.k, len(slugs) - 1)
    # 질의 집합: 본문이 충분히 긴 페이지.
    queries = [i for i, b in enumerate(bodies) if len(b) >= args.min_body]

    # 군집 인덱스 묶음.
    comm_members: dict[int, list[int]] = defaultdict(list)
    for s in slugs:
        comm_members[node_comm.get(s, -1)].append(idx_of[s])

    agg = {
        "A": Counter(), "B": Counter(),
    }
    n_q = 0
    b_short = 0  # 군집이 작아 top-k 를 못 채운 질의 수

    for qi in queries:
        q_slug = slugs[qi]
        q_dom = domain[q_slug]
        q_comm = node_comm.get(q_slug, -1)
        n_q += 1

        # Condition A: 전체 vault top-k.
        order = np.argpartition(-S[qi], k)[:k]
        a_top = order[np.argsort(-S[qi][order])]

        # Condition B: 같은 community 로 후보 제한.
        cand = [j for j in comm_members[q_comm] if j != qi]
        if len(cand) > k:
            cand_arr = np.array(cand)
            sub = S[qi][cand_arr]
            sel = cand_arr[np.argsort(-sub)[:k]]
            b_top = sel
        else:
            b_top = np.array(cand)
            if len(cand) < k:
                b_short += 1

        for label, top in (("A", a_top), ("B", b_top)):
            c = agg[label]
            c["retrieved"] += len(top)
            for j in top:
                hit = slugs[j]
                cross = domain[hit] != q_dom
                curated = frozenset((q_slug, hit)) in cur_pairs
                if curated:
                    c["curated"] += 1
                if cross:
                    c["cross"] += 1
                    if curated:
                        c["cross_curated"] += 1   # 정당한 우연한 연결
                    else:
                        c["cross_uncurated"] += 1  # 거짓 연관 후보

    def per_q(label, key):
        return agg[label][key] / n_q if n_q else 0.0

    def rate(label, key):
        r = agg[label]["retrieved"]
        return agg[label][key] / r if r else 0.0

    print("# forest-retrieval-experiment — 검증 실험 B v1 (TF-IDF retriever)")
    print(f"질의 페이지: {n_q} | top-k = {k} | 문서 {len(slugs)}개")
    print(f"retriever: char n-gram(3-5) TF-IDF cosine (링크 그래프와 독립)")
    print(f"community: Louvain resolution=1.0 seed=42 | "
          f"B 에서 군집이 작아 top-k 미달인 질의: {b_short}")
    print()
    hdr = f"{'metric':36} {'A(vault)':>12} {'B(forest)':>12} {'Δ(B-A)':>12}"
    print(hdr)
    print("-" * len(hdr))
    rows = [
        ("cross-domain / top-k (전체)", "cross"),
        ("  거짓 연관 후보 (uncurated)", "cross_uncurated"),
        ("  정당한 cross 연결 (curated)", "cross_curated"),
        ("curated hit / top-k (정밀도 proxy)", "curated"),
    ]
    for name, key in rows:
        a, b = rate("A", key), rate("B", key)
        print(f"{name:36} {a:>12.3f} {b:>12.3f} {b - a:>+12.3f}")
    print()
    print("질의당 평균 건수 (top-k 안):")
    for name, key in rows:
        print(f"  {name:34} A={per_q('A', key):.2f}  B={per_q('B', key):.2f}")

    # trade-off 판정 보조.
    a_spur = per_q("A", "cross_uncurated")
    b_spur = per_q("B", "cross_uncurated")
    a_legit = per_q("A", "cross_curated")
    b_legit = per_q("B", "cross_curated")
    print()
    print("# trade-off 요약 (질의당)")
    print(f"  거짓 연관 감소: {a_spur:.2f} → {b_spur:.2f}  (줄인 양 {a_spur - b_spur:.2f})")
    print(f"  정당한 cross 손실: {a_legit:.2f} → {b_legit:.2f}  (잃은 양 {a_legit - b_legit:.2f})")
    if (a_legit - b_legit) > 0:
        ratio = (a_spur - b_spur) / (a_legit - b_legit)
        print(f"  교환비 (거짓 1 줄일 때 정당 연결 손실): {1/ratio:.2f}" if ratio else "  교환비: n/a")
        print(f"  → 거짓 연관 {ratio:.1f}건을 줄이는 대가로 정당한 cross 연결 1건을 잃는다.")
    print()
    print("주의: 'curated=관련' 은 근사다. uncurated cross 중 일부는 노이즈가 아니라")
    print("아직 링크 안 된 가치 있는 발견일 수 있다. 이 실험은 trade-off 의 크기를 재며,")
    print("최종 판정에는 사람의 관련성 라벨이 필요하다.")


if __name__ == "__main__":
    main()
