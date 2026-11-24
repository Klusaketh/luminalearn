function moveZeroes(nums) {
  let w = 0;  // next position for a non-zero value
  for (const x of nums) {
    if (x !== 0) nums[w++] = x;
  }
  for (let i = w; i < nums.length; i++) nums[i] = 0;
  return nums;
}
