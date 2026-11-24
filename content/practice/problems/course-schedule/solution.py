from collections import deque

def can_finish(num_courses, prerequisites):
    unlocks = [[] for _ in range(num_courses)]
    waiting_on = [0] * num_courses          # unmet prerequisites per course
    for course, before in prerequisites:
        unlocks[before].append(course)
        waiting_on[course] += 1
    ready = deque(c for c in range(num_courses) if waiting_on[c] == 0)
    taken = 0
    while ready:
        c = ready.popleft()
        taken += 1
        for nxt in unlocks[c]:
            waiting_on[nxt] -= 1
            if waiting_on[nxt] == 0:
                ready.append(nxt)
    return taken == num_courses
