function maxSubarray(nums) {
  let best = nums[0], current = nums[0];
  for (let i = 1; i < nums.length; i++) {
    current = Math.max(nums[i], current + nums[i]);  // extend the run, or start again here
    best = Math.max(best, current);
  }
  return best;
}
