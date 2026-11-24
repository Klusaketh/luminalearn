def coin_change(coins, amount):
    INF = float("inf")
    best = [0] + [INF] * amount            # best[a] = fewest coins making amount a
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and best[a - c] + 1 < best[a]:
                best[a] = best[a - c] + 1
    return best[amount] if best[amount] != INF else -1
