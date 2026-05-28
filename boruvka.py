class DSU:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def unite(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True

    def count_components(self, n: int) -> int:
        return len({self.find(i) for i in range(n)})


def boruvka(n: int, edges: list) -> dict:
    dsu = DSU(n)
    mst_edges = []
    total_weight = 0
    phases = []
    num_components = n

    phase_num = 0

    while num_components > 1:
        phase_num += 1
        cheapest = {}

        candidates_log = []

        for idx, (u, v, w) in enumerate(edges):
            cu = dsu.find(u)
            cv = dsu.find(v)
            if cu == cv:
                candidates_log.append({
                    "edge_idx": idx,
                    "u": u, "v": v, "w": w,
                    "comp_u": cu, "comp_v": cv,
                    "action": "skip_same_component"
                })
                continue

            candidates_log.append({
                "edge_idx": idx,
                "u": u, "v": v, "w": w,
                "comp_u": cu, "comp_v": cv,
                "action": "consider"
            })

            if cu not in cheapest or w < cheapest[cu][0]:
                cheapest[cu] = (w, u, v, idx)

            if cv not in cheapest or w < cheapest[cv][0]:
                cheapest[cv] = (w, u, v, idx)

        added_in_phase = []
        skipped_duplicates = []
        seen_edge_indices = set()

        for comp_root, (w, u, v, idx) in cheapest.items():
            if idx in seen_edge_indices:
                skipped_duplicates.append({"u": u, "v": v, "w": w})
                continue
            seen_edge_indices.add(idx)

            if dsu.unite(u, v):
                mst_edges.append({"u": u, "v": v, "w": w})
                total_weight += w
                num_components -= 1
                added_in_phase.append({
                    "u": u, "v": v, "w": w,
                    "comp_u": dsu.find(u),
                    "edge_idx": idx
                })

        comp_map = {}
        for i in range(n):
            root = dsu.find(i)
            if root not in comp_map:
                comp_map[root] = []
            comp_map[root].append(i)
        components_snapshot = list(comp_map.values())

        phases.append({
            "phase": phase_num,
            "cheapest_edges": [
                {"comp": c, "u": val[1], "v": val[2], "w": val[0], "edge_idx": val[3]}
                for c, val in cheapest.items()
            ],
            "added_edges": added_in_phase,
            "skipped_duplicates": skipped_duplicates,
            "components_after": components_snapshot,
            "num_components_after": num_components,
            "candidates_log": candidates_log
        })

        if not added_in_phase:
            break

    connected = (num_components == 1)

    return {
        "mst_edges": mst_edges,
        "total_weight": total_weight,
        "phases": phases,
        "connected": connected,
        "num_phases": phase_num
    }
