import heapq

def network_delay_time(times, n, k):
    graph = {u: [] for u in range(1, n + 1)}
    for u, v, w in times:
        graph[u].append((v, w))
    settled = {}
    heap = [(0, k)]
    while heap:                                # Dijkstra: always expand the earliest node
        t, node = heapq.heappop(heap)
        if node in settled:
            continue
        settled[node] = t
        for nxt, w in graph[node]:
            if nxt not in settled:
                heapq.heappush(heap, (t + w, nxt))
    return max(settled.values()) if len(settled) == n else -1
