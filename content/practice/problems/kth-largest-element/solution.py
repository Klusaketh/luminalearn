import heapq

def find_kth_largest(nums, k):
    heap = []                              # the k largest values seen so far
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)
    return heap[0]
