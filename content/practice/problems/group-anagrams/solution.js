function groupAnagrams(words) {
  const groups = new Map();
  for (const w of words) {
    const key = [...w].sort().join("");
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(w);
  }
  const compare = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
  const byList = (x, y) => {
    for (let i = 0; i < Math.min(x.length, y.length); i++) {
      const c = compare(x[i], y[i]);
      if (c !== 0) return c;
    }
    return x.length - y.length;
  };
  return [...groups.values()].map((g) => g.sort(compare)).sort(byList);
}
