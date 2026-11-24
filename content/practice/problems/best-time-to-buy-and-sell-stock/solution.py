def max_profit(prices):
    lowest = float("inf")
    best = 0
    for price in prices:
        lowest = min(lowest, price)          # cheapest day to have bought on
        best = max(best, price - lowest)     # sell today?
    return best
