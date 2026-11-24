def min_cost_connect_points(points):
    n = len(points)
    parent = list(range(n))

    def find(x):                               # union-find root with path halving
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    edges = sorted(
        (abs(points[i][0] - points[j][0]) + abs(points[i][1] - points[j][1]), i, j)
        for i in range(n) for j in range(i + 1, n)
    )
    total = links = 0
    for cost, i, j in edges:                   # Kruskal: cheapest edge that joins two trees
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj
            total += cost
            links += 1
            if links == n - 1:
                break
    return total
