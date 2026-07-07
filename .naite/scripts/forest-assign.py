#!/usr/bin/env python3
"""forest-assign.py — 개념 계보 기반 페이지→나무 배정 + 걸침 개념 surface.

핵심 원칙: 나무 소속은 '과목 도메인 라벨'이 아니라 '개념 계보(링크 이웃이 실제로
어느 나무에 속하는가)'로 정한다. 예) 한 페이지가 한 과목에서 왔어도, 링크 이웃이
다른 계보에 모이면 그 계보의 나무로 흘러야 한다.

방법: semi-supervised label propagation. 각 페이지를 도메인→나무 map 으로 seed 한 뒤,
가중 링크 그래프 위에서 이웃의 나무 분포로 점수를 번지게 한다(seed 를 alpha 로 앵커).
수렴 후 argmax 가 배정 나무, top1-top2 margin 이 낮으면 '걸침 개념'(genuine bridge).

이 도구는 걸침 개념 메커니즘(#1)의 구현이다:
  - flip(seed != final)  = 과목 라벨이 개념 계보와 어긋난 페이지 (재배정 후보)
  - low-margin           = 두 나무에 정당하게 걸친 페이지 (primary home + inter-tree link)

READ-ONLY. 트리/ontology 미수정.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

NAITE_ROOT = Path(__file__).resolve().parent.parent.parent
DEPS_PATH = NAITE_ROOT / ".naite" / "ontology" / "tree-dependencies.json"
MANIFEST_PATH = NAITE_ROOT / ".naite" / "ontology" / "tree-manifest.json"
FOREST_PATH = NAITE_ROOT / ".naite" / "ontology" / "forest-manifest.json"
CONFIG_PATH = NAITE_ROOT / ".naite" / "forest" / "forest-config.json"

def load_config() -> dict:
    """vault-specific forest-config.json 로드. 없으면 빈 config(identity fallback)."""
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {}

RELATION_WEIGHT = {
    "builds-on": 3.0, "instance-of": 3.0, "extends": 3.0, "applies-to": 2.0, "see-also": 1.0,
}
BASE_WEIGHT = 1.0
SYNAPSE_RELATIONS = {
    "decided-over", "trade-off", "validates", "falsifies", "contradicts", "failed-when",
}

def load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--alpha", type=float, default=0.25, help="seed 앵커 강도(0~1).")
    ap.add_argument("--iters", type=int, default=40, help="propagation 반복 수.")
    ap.add_argument("--margin", type=float, default=0.15, help="걸침 개념 margin 임계.")
    ap.add_argument("--neutral", type=str, default="",
                    help="seed 를 주지 않고 이웃이 정하게 할 도메인(쉼표 구분). "
                         "예: domain-a,domain-b")
    ap.add_argument("--write", action="store_true",
                    help="개념 계보 배정을 .naite/ontology/forest-manifest.json 에 기록.")
    args = ap.parse_args()

    config = load_config()
    config_domain_to_tree = config.get("domain_to_tree", {})
    tree_desc = config.get("tree_descriptions", {})
    tree_labels = config.get("tree_labels", {})  # tree -> 사람용 표시 이름 (naite-app 이 manifest.label 로 읽는다)
    # --neutral 가 주어지면 그것을 쓰고, 아니면 config 의 neutral_domains.
    if args.neutral:
        neutral_domains = {d.strip() for d in args.neutral.split(",") if d.strip()}
    else:
        neutral_domains = set(config.get("neutral_domains", []))

    deps = load_json(DEPS_PATH)
    manifest = load_json(MANIFEST_PATH)
    recs = [r for r in manifest.get("pages", []) if not r.get("special", False)]
    meta = {r["slug"]: r for r in recs}
    existing = set(meta.keys())

    def first_domain(m: dict) -> str:
        for key in ("domains", "subject"):
            v = m.get(key)
            if isinstance(v, list) and v:
                return str(v[0]).split("/")[0]
        return "(none)"

    nodes = sorted(existing)
    idx = {s: i for i, s in enumerate(nodes)}
    n = len(nodes)
    if n == 0:
        print("# forest-assign — 콘텐츠 페이지가 없어 배정할 것이 없습니다 "
              "(Phase 1: 빈/단일 나무).")
        return

    # config 의 domain_to_tree, 없는 도메인은 identity(도메인=나무) fallback.
    # config 자체가 비면 모든 도메인이 자기 이름의 나무가 된다(어떤 vault 에서도 동작).
    domains_seen = {first_domain(meta[s]) for s in nodes}
    domain_to_tree = dict(config_domain_to_tree)
    for d in domains_seen:
        domain_to_tree.setdefault(d, d)

    trees = sorted(set(domain_to_tree.values()))
    tidx = {t: i for i, t in enumerate(trees)}
    T = len(trees)

    seed_tree = {s: domain_to_tree[first_domain(meta[s])] for s in nodes}

    # 가중 인접행렬(시냅스 제외).
    edge_rel = defaultdict(set)
    for src, targets in deps.get("outbound", {}).items():
        if src in existing:
            for t in targets:
                if t in existing and t != src:
                    edge_rel[frozenset((src, t))]
    for src, rel, tgt in deps.get("relation_edges", []):
        if src in existing and tgt in existing and src != tgt:
            edge_rel[frozenset((src, tgt))].add(rel)

    A = np.zeros((n, n), dtype=np.float64)
    for pair, rels in edge_rel.items():
        a, b = tuple(pair)
        cr = [r for r in rels if r not in SYNAPSE_RELATIONS]
        w = max((RELATION_WEIGHT.get(r, BASE_WEIGHT) for r in cr), default=BASE_WEIGHT)
        ia, ib = idx[a], idx[b]
        A[ia, ib] = w
        A[ib, ia] = w

    # row-normalize.
    rowsum = A.sum(axis=1, keepdims=True)
    rowsum[rowsum == 0] = 1.0
    P = A / rowsum

    # seed one-hot. neutral 도메인 페이지는 uniform(이웃이 결정).
    S = np.zeros((n, T), dtype=np.float64)
    for s in nodes:
        if first_domain(meta[s]) in neutral_domains:
            S[idx[s], :] = 1.0 / T
        else:
            S[idx[s], tidx[seed_tree[s]]] = 1.0

    F = S.copy()
    for _ in range(args.iters):
        F = args.alpha * S + (1 - args.alpha) * (P @ F)
        rs = F.sum(axis=1, keepdims=True)
        rs[rs == 0] = 1.0
        F = F / rs

    final_idx = F.argmax(axis=1)
    final_tree = {nodes[i]: trees[final_idx[i]] for i in range(n)}
    sortedF = np.sort(F, axis=1)
    if T < 2:
        # Single-tree vault (the common starting state): no runner-up column
        # exists, every page is unambiguously assigned.
        margin = np.ones(n, dtype=np.float64)
    else:
        margin = sortedF[:, -1] - sortedF[:, -2]

    # 결과 집계.
    final_sizes = Counter(final_tree[s] for s in nodes)
    seed_sizes = Counter(seed_tree[s] for s in nodes)

    print("# forest-assign — 개념 계보 기반 배정 (label propagation)")
    print(f"nodes {n} | trees {T} | alpha {args.alpha} | iters {args.iters}")
    print()
    print(f"{'tree':22} {'seed':>6} {'final':>6} {'Δ':>5}")
    print("-" * 42)
    for t in trees:
        print(f"{t:22} {seed_sizes.get(t,0):>6} {final_sizes.get(t,0):>6} "
              f"{final_sizes.get(t,0)-seed_sizes.get(t,0):>+5}")

    # flips: seed != final.
    flips = [(s, seed_tree[s], final_tree[s]) for s in nodes if seed_tree[s] != final_tree[s]]
    flip_by = Counter((a, b) for _s, a, b in flips)
    print()
    print(f"# 과목 라벨과 개념 계보가 어긋난 페이지(flip): {len(flips)}")
    for (a, b), c in flip_by.most_common(12):
        print(f"  {a:20} → {b:20} {c:>4}")

    # 검증: 과목 라벨과 개념 계보가 어긋나기 쉬운 도메인의 최종 행선.
    # neutral 도메인이 지정됐으면 그것을, 아니면 flip 이 가장 많은 도메인을 본다.
    if neutral_domains:
        check_domains = sorted(neutral_domains)
    else:
        flip_counter = Counter(first_domain(meta[s]) for s in nodes
                               if seed_tree[s] != final_tree[s])
        check_domains = [d for d, _c in flip_counter.most_common(3)]
    if check_domains:
        print()
        print("# 검증: 도메인별 최종 나무 분포 (걸침 개념 메커니즘 확인)")
        for dom in check_domains:
            d_pages = [s for s in nodes if first_domain(meta[s]) == dom]
            if not d_pages:
                continue
            d_dest = Counter(final_tree[s] for s in d_pages)
            print(f"  {dom} {len(d_pages)}p → {dict(d_dest)}")
            for s in sorted(d_pages, key=lambda x: -F[idx[x]].max())[:5]:
                print(f"    {final_tree[s]:14} ← {s}")

    # 걸침 개념: low margin. (T<2 → no secondary tree, no bridges by definition.)
    bridges = sorted(
        [(s, final_tree[s], trees[int(np.argsort(F[idx[s]])[-2])], float(margin[idx[s]]))
         for s in nodes if T >= 2 and margin[idx[s]] < args.margin],
        key=lambda x: x[3],
    )
    print()
    print(f"# 걸침 개념(genuine bridge, margin<{args.margin}): {len(bridges)}")
    print("  primary / secondary 두 나무에 걸친 페이지 → primary 거주 + inter-tree link.")
    for s, t1, t2, m in bridges[:15]:
        print(f"    {m:.3f}  {s:42} {t1} | {t2}")

    if args.write:
        kind_of = {r["slug"]: r.get("kind", "?") for r in recs}
        intra = Counter()
        inter = Counter()
        for src, targets in deps.get("outbound", {}).items():
            if src not in existing:
                continue
            ta = final_tree[src]
            for t in targets:
                if t in existing:
                    tb = final_tree[t]
                    if ta == tb:
                        intra[ta] += 1
                    else:
                        inter[frozenset((ta, tb))] += 1
        forest_trees = []
        for t in trees:
            members = [s for s in nodes if final_tree[s] == t]
            internal = intra.get(t, 0)
            external = sum(c for pair, c in inter.items() if t in pair)
            total = internal + external
            entry = {
                "tree": t,
                "description": tree_desc.get(t, ""),
                "page_count": len(members),
                "self_containment": round(internal / total, 3) if total else 0.0,
                "internal_edges": internal,
                "external_edges": external,
                "by_kind": dict(Counter(kind_of[s] for s in members)),
            }
            # 사람용 표시 이름(약어 확장 등)은 vault 가 정한다 — 앱은 하드코딩하지 않는다.
            if tree_labels.get(t):
                entry["label"] = tree_labels[t]
            forest_trees.append(entry)
        out = {
            "schema_version": 2,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator": ".naite/scripts/forest-assign.py",
            "status": "proposal",
            "method": "concept-lineage label propagation",
            "note": "나무 소속은 과목 도메인이 아니라 링크 이웃(개념 계보)으로 배정. "
                    "마이그레이션 전 사용자 승인 대상.",
            "params": {"alpha": args.alpha, "iters": args.iters,
                       "neutral_domains": sorted(neutral_domains)},
            "page_count": n,
            "tree_count": len(trees),
            "trees": forest_trees,
            "inter_tree_edges": [
                {"trees": sorted(list(pair)), "count": c}
                for pair, c in sorted(inter.items(), key=lambda kv: kv[1], reverse=True)
            ],
            "bridges": [
                {"slug": s, "primary": t1, "secondary": t2, "margin": round(m, 3)}
                for s, t1, t2, m in bridges
            ],
            "page_to_tree": {s: final_tree[s] for s in nodes},
        }
        FOREST_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print()
        print(f"wrote {FOREST_PATH.relative_to(NAITE_ROOT)} (schema_version 2, 개념 계보 배정)")


if __name__ == "__main__":
    import sys
    try:  # keep non-ASCII report output from crashing a cp949/legacy Windows console
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    main()
