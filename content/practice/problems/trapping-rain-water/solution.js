function trap(heights) {
  let left = 0, right = heights.length - 1;
  let leftMax = 0, rightMax = 0, water = 0;
  while (left < right) {
    if (heights[left] < heights[right]) {  // the left side is the lower wall
      leftMax = Math.max(leftMax, heights[left]);
      water += leftMax - heights[left++];
    } else {
      rightMax = Math.max(rightMax, heights[right]);
      water += rightMax - heights[right--];
    }
  }
  return water;
}
