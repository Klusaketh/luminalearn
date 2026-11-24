def subsets(nums):
    nums = sorted(nums)
    result = []

    def build(start, chosen):
        result.append(list(chosen))
        for j in range(start, len(nums)):
            chosen.append(nums[j])
            build(j + 1, chosen)
            chosen.pop()                       # backtrack

    build(0, [])
    return result
