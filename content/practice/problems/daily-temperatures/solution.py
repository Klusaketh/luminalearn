def daily_temperatures(temperatures):
    answer = [0] * len(temperatures)
    waiting = []                           # indices still waiting for a warmer day
    for i, t in enumerate(temperatures):
        while waiting and temperatures[waiting[-1]] < t:
            j = waiting.pop()
            answer[j] = i - j
        waiting.append(i)
    return answer
