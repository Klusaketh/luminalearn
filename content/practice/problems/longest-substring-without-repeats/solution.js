function lengthOfLongestSubstring(s) {
  const last = new Map();  // character -> last index seen
  let start = 0, best = 0;
  for (let i = 0; i < s.length; i++) {
    const ch = s[i];
    if (last.has(ch) && last.get(ch) >= start) start = last.get(ch) + 1;  // jump past the earlier copy
    last.set(ch, i);
    best = Math.max(best, i - start + 1);
  }
  return best;
}
