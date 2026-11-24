function findKthLargest(nums, k) {
  // A min-heap holding the k largest values seen so far.
  const heap = [];
  const swap = (i, j) => ([heap[i], heap[j]] = [heap[j], heap[i]]);
  const push = (x) => {
    heap.push(x);
    for (let i = heap.length - 1; i > 0 && heap[(i - 1) >> 1] > heap[i]; i = (i - 1) >> 1) swap(i, (i - 1) >> 1);
  };
  const pop = () => {
    heap[0] = heap.pop();
    for (let i = 0; ; ) {
      const l = 2 * i + 1, r = l + 1;
      let m = i;
      if (l < heap.length && heap[l] < heap[m]) m = l;
      if (r < heap.length && heap[r] < heap[m]) m = r;
      if (m === i) break;
      swap(i, m);
      i = m;
    }
  };
  for (const x of nums) {
    push(x);
    if (heap.length > k) pop();
  }
  return heap[0];
}
