function dailyTemperatures(temperatures) {
  const answer = new Array(temperatures.length).fill(0);
  const waiting = [];  // indices still waiting for a warmer day
  temperatures.forEach((t, i) => {
    while (waiting.length && temperatures[waiting[waiting.length - 1]] < t) {
      const j = waiting.pop();
      answer[j] = i - j;
    }
    waiting.push(i);
  });
  return answer;
}
