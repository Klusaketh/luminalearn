def max_subarray(nums):
    best = current = nums[0]
    for x in nums[1:]:
        current = max(x, current + x)   # extend the run, or start again at x
        best = max(best, current)
    return best
