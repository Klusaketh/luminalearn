function maxProfit(prices) {
  let lowest = Infinity, best = 0;
  for (const price of prices) {
    lowest = Math.min(lowest, price);       // cheapest day to have bought on
    best = Math.max(best, price - lowest);  // sell today?
  }
  return best;
}
