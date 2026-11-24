function coinChange(coins, amount) {
  const best = [0, ...new Array(amount).fill(Infinity)];  // best[a] = fewest coins making amount a
  for (let a = 1; a <= amount; a++) {
    for (const c of coins) {
      if (c <= a && best[a - c] + 1 < best[a]) best[a] = best[a - c] + 1;
    }
  }
  return best[amount] === Infinity ? -1 : best[amount];
}
