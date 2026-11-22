def length_of_longest_substring(s):
    last = {}                      # character -> last index seen
    start = best = 0
    for i, ch in enumerate(s):
        if ch in last and last[ch] >= start:
            start = last[ch] + 1   # jump past the earlier copy
        last[ch] = i
        best = max(best, i - start + 1)
    return best
