---
lesson: modular-arithmetic-gcd
title: Modular Arithmetic, GCD & Primes
summary: Divisibility and the division algorithm, congruences and modular arithmetic, the Euclidean and extended Euclidean algorithms, modular inverses, primes and the fundamental theorem of arithmetic, fast modular exponentiation, and an outline of RSA.
minutes: 50
type: theory
objectives:
  - Compute remainders and work with congruences, using the rules of modular addition and multiplication
  - Compute gcds with the Euclidean algorithm and modular inverses with the extended Euclidean algorithm
  - Explain prime factorisation, fast modular exponentiation, and how RSA uses them to encrypt and decrypt
review: ai-draft
---
## Introduction

Number theory, once considered the purest and least practical branch of mathematics, now secures almost every online transaction. Hash functions, checksums, random number generators, and public-key cryptography all rely on **modular arithmetic**, arithmetic that "wraps around" like the hours on a clock. This lesson builds the tools step by step, from remainders to the RSA cryptosystem.

**Before you start:** you should know divisibility, proof techniques, and equivalence relations.

## Core theory

### Divisibility and the division algorithm

$a \mid b$ ("a divides b") means $b = ak$ for some integer $k$. The **division algorithm** states that for any integer $a$ and positive integer $d$ there are unique integers $q$ (quotient) and $r$ (remainder) with

$$a = dq + r, \qquad 0 \le r < d$$

We write $r = a \bmod d$. Note that for negative $a$ the remainder is still non-negative in mathematics: $-7 \bmod 3 = 2$ because $-7 = 3(-3) + 2$. (Python's `%` agrees; C and Java's `%` give $-1$.)

### Congruences

$a \equiv b \pmod m$ means $m \mid (a - b)$, equivalently that $a$ and $b$ leave the same remainder modulo $m$. Congruence modulo $m$ is an equivalence relation whose classes are the residues $0, 1, \dots, m - 1$. It respects addition and multiplication: if $a \equiv b$ and $c \equiv d \pmod m$, then

$$a + c \equiv b + d, \qquad ac \equiv bd \pmod m$$

so you may reduce intermediate results at any time, which keeps numbers small. Division is not automatically allowed: $2 \cdot 3 \equiv 2 \cdot 0 \pmod 6$, yet $3 \not\equiv 0$.

### GCD and the Euclidean algorithm

The **greatest common divisor** $\gcd(a, b)$ is the largest integer dividing both. The **Euclidean algorithm** rests on $\gcd(a, b) = \gcd(b, a \bmod b)$ and $\gcd(a, 0) = a$; it takes $O(\log \min(a, b))$ steps. The **extended** Euclidean algorithm also finds integers $s, t$ with

$$\gcd(a, b) = sa + tb \qquad \text{(Bézout's identity)}$$

### Modular inverses

An **inverse** of $a$ modulo $m$ is an $x$ with $ax \equiv 1 \pmod m$. It exists **if and only if** $\gcd(a, m) = 1$. When it does, Bézout gives $sa + tm = 1$, so $sa \equiv 1 \pmod m$ and $s \bmod m$ is the inverse. Inverses let us "divide" and solve linear congruences $ax \equiv b \pmod m$.

### Primes

A **prime** is an integer $p > 1$ whose only positive divisors are 1 and $p$. The **fundamental theorem of arithmetic** says every integer $n > 1$ factors into primes uniquely, apart from order. Trial division up to $\sqrt{n}$ tests small numbers; there are infinitely many primes. **Fermat's little theorem:** if $p$ is prime and $p \nmid a$, then $a^{p-1} \equiv 1 \pmod p$. More generally, **Euler's theorem** says $a^{\varphi(m)} \equiv 1 \pmod m$ when $\gcd(a, m) = 1$, where $\varphi(m)$ counts the integers in $1..m$ coprime to $m$; for $m = pq$ with distinct primes, $\varphi(m) = (p - 1)(q - 1)$.

### Fast modular exponentiation

Computing $a^e \bmod m$ by multiplying $e$ times is hopeless for 2048-bit exponents. **Square-and-multiply** processes the bits of $e$: square the running power for each bit and multiply it into the result when the bit is 1, reducing modulo $m$ every time. It needs only $O(\log e)$ multiplications. Python's built-in `pow(a, e, m)` does this.

### RSA in outline

1. Choose large primes $p, q$ and set $n = pq$, $\varphi = (p - 1)(q - 1)$.
2. Choose $e$ with $\gcd(e, \varphi) = 1$ (often 65537) and compute $d = e^{-1} \bmod \varphi$.
3. Publish $(n, e)$; keep $d$ secret.
4. Encrypt a message $M < n$ as $C = M^e \bmod n$; decrypt as $M = C^d \bmod n$.

Decryption works because $ed \equiv 1 \pmod{\varphi}$ and Euler's theorem gives $M^{ed} \equiv M \pmod n$. Security rests on the belief that factoring $n$ to recover $p$ and $q$ is infeasible for large primes. Real RSA also uses randomised padding; never use "textbook" RSA directly.

## Worked examples

### Example 1: gcd, Bézout coefficients, and an inverse

Find $\gcd(240, 46)$, Bézout coefficients, and the inverse of 7 modulo 40.

Euclid: $240 = 5 \cdot 46 + 10$; $46 = 4 \cdot 10 + 6$; $10 = 1 \cdot 6 + 4$; $6 = 1 \cdot 4 + 2$; $4 = 2 \cdot 2 + 0$, so the gcd is 2. Working backwards gives $2 = -9 \cdot 240 + 47 \cdot 46$.

```python
def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, s, t = extended_gcd(b, a % b)
    return g, t, s - (a // b) * t

g, s, t = extended_gcd(240, 46)
print(g, s, t, s * 240 + t * 46)
g, s, _ = extended_gcd(7, 40)
inverse = s % 40
print("inverse of 7 mod 40:", inverse, "check:", 7 * inverse % 40, pow(7, -1, 40))
print("solve 7x = 3 (mod 40): x =", 3 * inverse % 40)
print(-7 % 3, (17 * 23) % 5, (17 % 5) * (23 % 5) % 5)
```

Output:

```text
2 -9 47 2
inverse of 7 mod 40: 23 check: 1 23
solve 7x = 3 (mod 40): x = 29
2 1 1
```

The extended algorithm returns the Bézout coefficients $-9$ and $47$. Since $\gcd(7, 40) = 1$, 7 has an inverse modulo 40, namely 23 (Python's `pow(7, -1, 40)` agrees), and multiplying both sides of $7x \equiv 3$ by 23 solves the congruence. The last line shows that Python's `%` returns the mathematical remainder 2 for $-7 \bmod 3$, and that reducing before multiplying gives the same result: $17 \cdot 23 = 391 \equiv 1 \pmod 5$ and $2 \cdot 3 = 6 \equiv 1 \pmod 5$.

### Example 2: A toy RSA round trip

With tiny primes $p = 61$, $q = 53$ (far too small for real security):

```python
from math import gcd

p, q = 61, 53
n, phi = p * q, (p - 1) * (q - 1)
e = 17
assert gcd(e, phi) == 1
d = pow(e, -1, phi)
message = 1234
cipher = pow(message, e, n)
decrypted = pow(cipher, d, n)
print(f"n={n} phi={phi} e={e} d={d}")
print(f"encrypt {message} -> {cipher}, decrypt -> {decrypted}")
print("e*d mod phi =", e * d % phi)
```

Output:

```text
n=3233 phi=3120 e=17 d=2753
encrypt 1234 -> 2183, decrypt -> 1234
e*d mod phi = 1
```

Anyone may encrypt with the public pair $(3233, 17)$, but decrypting requires $d = 2753$, which is easy to compute only if you know $\varphi = 3120$, that is, the factors 61 and 53.

## Applications

- **Cryptography:** RSA, Diffie-Hellman, and elliptic-curve schemes rely on modular arithmetic.
- **Hashing:** hash functions reduce values modulo the table size.
- **Checksums:** ISBN and credit-card (Luhn) check digits use modular arithmetic.
- **Random numbers:** linear congruential generators compute $x_{n+1} = (ax_n + c) \bmod m$.

## Common mistakes

- **Dividing congruences directly.** Multiply by an inverse instead, and only when it exists.
- **Negative remainders.** Mathematical $a \bmod m$ is in $0..m-1$; some languages return negatives.
- **Computing huge powers before reducing.** Use square-and-multiply with reduction at every step.
- **Assuming every number has an inverse mod m.** Only those coprime to $m$ do.
- **Using textbook RSA in practice.** Real systems need large keys and padding.

## Revision notes

- $a = dq + r$, $0 \le r < d$; $a \equiv b \pmod m \iff m \mid (a - b)$.
- Congruence respects $+$ and $\times$; reduce at any time; no direct division.
- Euclid: $\gcd(a, b) = \gcd(b, a \bmod b)$; extended Euclid gives $sa + tb = \gcd(a, b)$.
- Inverse of $a$ mod $m$ exists iff $\gcd(a, m) = 1$.
- Fermat: $a^{p-1} \equiv 1 \pmod p$; Euler: $a^{\varphi(m)} \equiv 1$; $\varphi(pq) = (p-1)(q-1)$.
- RSA: $n = pq$, $ed \equiv 1 \pmod{\varphi}$, $C = M^e \bmod n$, $M = C^d \bmod n$.

## Practice questions

:::question basic
Compute $47 \bmod 6$ and $-47 \bmod 6$.
:::answer
$47 = 6 \cdot 7 + 5$, so $47 \bmod 6 = 5$. $-47 = 6 \cdot (-8) + 1$, so $-47 \bmod 6 = 1$, taking the remainder in the range 0 to 5.
:::

:::question basic
Use the Euclidean algorithm to find $\gcd(84, 36)$.
:::answer
$84 = 2 \cdot 36 + 12$ and $36 = 3 \cdot 12 + 0$, so $\gcd(84, 36) = 12$.
:::

:::question intermediate
Find the inverse of 5 modulo 17, and use it to solve $5x \equiv 3 \pmod{17}$.
:::answer
$5 \cdot 7 = 35 = 2 \cdot 17 + 1$, so the inverse is 7. Multiplying both sides by 7 gives $x \equiv 21 \equiv 4 \pmod{17}$; check: $5 \cdot 4 = 20 \equiv 3$.
:::

:::question intermediate
What is the last digit of $7^{2026}$?
:::answer
Work modulo 10. Powers of 7 cycle through 7, 9, 3, 1 with period 4. Since $2026 = 4 \cdot 506 + 2$, $7^{2026} \equiv 7^2 = 49 \equiv 9 \pmod{10}$, so the last digit is 9.
:::

:::question advanced
In RSA with $p = 11$, $q = 13$, and $e = 7$, find the private key $d$ and encrypt $M = 9$.
:::answer
$n = 143$ and $\varphi = 10 \cdot 12 = 120$. We need $7d \equiv 1 \pmod{120}$: $7 \cdot 103 = 721 = 6 \cdot 120 + 1$, so $d = 103$. Encrypt: $C = 9^7 \bmod 143$. $9^2 = 81$, $9^4 = 81^2 = 6561 \equiv 6561 - 45 \cdot 143 = 126$, $9^6 = 126 \cdot 81 = 10206 \equiv 10206 - 71 \cdot 143 = 53$, $9^7 = 53 \cdot 9 = 477 \equiv 477 - 3 \cdot 143 = 48$. So $C = 48$, and $48^{103} \bmod 143$ returns 9.
:::

## Further learning

- **Next:** return to *Propositional & Predicate Logic* to formalise number-theoretic statements, or continue to Probability.
- **Related:** *Hash Functions & Collision Handling* uses modular reduction to choose buckets.
