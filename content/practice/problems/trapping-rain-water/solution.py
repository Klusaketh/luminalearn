def trap(heights):
    left, right = 0, len(heights) - 1
    left_max = right_max = water = 0
    while left < right:
        if heights[left] < heights[right]:     # the left side is the lower wall
            left_max = max(left_max, heights[left])
            water += left_max - heights[left]
            left += 1
        else:
            right_max = max(right_max, heights[right])
            water += right_max - heights[right]
            right -= 1
    return water
