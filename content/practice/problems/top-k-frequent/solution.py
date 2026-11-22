from collections import Counter
import heapq

def top_k_frequent(nums, k):
    counts = Counter(nums)
    return heapq.nsmallest(k, counts, key=lambda v: (-counts[v], v))
