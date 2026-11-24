function topKFrequent(nums, k) {
  const counts = new Map();
  for (const x of nums) counts.set(x, (counts.get(x) || 0) + 1);
  // most frequent first; ties go to the smaller value
  return [...counts.keys()].sort((a, b) => counts.get(b) - counts.get(a) || a - b).slice(0, k);
}
