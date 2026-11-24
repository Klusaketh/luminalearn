function climbStairs(n) {
  let a = 1, b = 1;  // ways to reach step 0 and step 1
  for (let i = 0; i < n - 1; i++) [a, b] = [b, a + b];
  return b;
}
