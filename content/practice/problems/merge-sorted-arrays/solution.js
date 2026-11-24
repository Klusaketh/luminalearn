function mergeSorted(a, b) {
  const merged = [];
  let i = 0, j = 0;
  while (i < a.length && j < b.length) merged.push(a[i] <= b[j] ? a[i++] : b[j++]);
  return merged.concat(a.slice(i), b.slice(j));
}
