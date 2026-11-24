function subsets(nums) {
  const sorted = [...nums].sort((a, b) => a - b);
  const result = [];
  const chosen = [];
  const build = (start) => {
    result.push([...chosen]);
    for (let j = start; j < sorted.length; j++) {
      chosen.push(sorted[j]);
      build(j + 1);
      chosen.pop();  // backtrack
    }
  };
  build(0);
  return result;
}
