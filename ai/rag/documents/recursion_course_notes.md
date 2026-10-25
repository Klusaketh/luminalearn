---
topic: Recursion
subject: Computer Science
source: LuminaLearn Course Notes: Recursion
---

## What recursion is
A recursive function solves a problem by calling itself on a smaller version of the same problem. Every correct recursive function has two parts. The base case answers the smallest inputs directly, without another call. The recursive case shrinks the input, calls the function on the smaller input, and combines that result into the answer for the current input. If any call can skip past the base case, the recursion never stops.

## The call stack
Each call that has not finished waits on the call stack. Calling factorial(4) pushes frames for factorial(4), factorial(3), factorial(2) and factorial(1). The base case returns 1, and the stack unwinds: factorial(2) returns 2 times 1, factorial(3) returns 3 times 2, and factorial(4) returns 4 times 6, which is 24. The stack holds one frame per level, so a recursion n levels deep uses O(n) stack space, and very deep recursion can overflow the stack.

## Designing a recursive solution
Start from the smallest input and decide what it should return. Then assume the recursive call already works for a smaller input, and ask how to build the current answer from it. This "leap of faith" is what makes recursion manageable: you never trace every level in your head. Finally, check that every call moves strictly closer to the base case, for example by decreasing n or by slicing a list.

## Common mistakes
Forgetting the base case, or writing one that is never reached, causes infinite recursion and a stack overflow. Calling the function with the same argument it received makes no progress. Branching into two or more calls on overlapping inputs, as a naive Fibonacci does, recomputes the same values exponentially many times; caching results with memoization reduces it to linear time.

## Recursion versus iteration
Any recursion can be rewritten as a loop with an explicit stack, and simple tail-shaped recursions become plain loops. Recursion is the clearer choice when the data is itself recursive, such as trees, nested lists, or divide-and-conquer algorithms like merge sort. A loop is usually better for long linear sequences, where recursion would use stack space for no benefit.
