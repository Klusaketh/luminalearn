function canFinish(numCourses, prerequisites) {
  const unlocks = Array.from({ length: numCourses }, () => []);
  const waitingOn = new Array(numCourses).fill(0);  // unmet prerequisites per course
  for (const [course, before] of prerequisites) {
    unlocks[before].push(course);
    waitingOn[course] += 1;
  }
  const ready = [];
  for (let c = 0; c < numCourses; c++) if (waitingOn[c] === 0) ready.push(c);
  let taken = 0;
  for (let head = 0; head < ready.length; head++) {
    taken += 1;
    for (const next of unlocks[ready[head]]) {
      if (--waitingOn[next] === 0) ready.push(next);
    }
  }
  return taken === numCourses;
}
