---
lesson: hash-functions-collisions
title: Hash Functions and Collision Handling
summary: How hash tables achieve constant average-time lookup, what makes a good hash function, and how chaining and open addressing resolve collisions.
minutes: 55
type: theory
objectives:
  - Explain how a hash function and an array combine to give average O(1) insert, delete, and lookup
  - Describe the properties of a good hash function and compute simple hash values by hand
  - Resolve collisions with separate chaining and with open addressing (linear probing, quadratic probing, double hashing)
  - Relate the load factor to performance, and explain resizing and the worst case
---

## Introduction

Arrays give constant-time access, but only by integer position. Most real lookups are by **key**: a username, a word, a product code, a file path. Searching a list of keys is $\Theta(n)$, and even a sorted array with binary search is $\Theta(\log n)$.

A **hash table** gets the best of both worlds. A **hash function** converts each key into an array index, so a lookup computes where the key should be and checks that slot directly. On average, insertions, deletions, and lookups all take $\Theta(1)$ time, which is why hash tables power Python's `dict` and `set`, Java's `HashMap`, database hash indexes, caches, and compilers' symbol tables.

The complication is that two different keys can map to the same slot, a **collision**. How a table handles collisions, and how full it is allowed to become, decides how fast it really is.

**Before you start:** you need arrays, linked lists, the modulo operator, and amortized analysis.

## Core theory

### Hash functions

A hash function $h$ maps a key to an integer, which is reduced to an index in a table of $m$ slots, typically with $h(k) \bmod m$. A good hash function:

1. **Is deterministic**: the same key always gives the same hash.
2. **Is fast** to compute.
3. **Spreads keys uniformly** over the slots, so that similar keys do not cluster.
4. **Uses the whole key**: hashing only the first character of a string, for example, sends all words with the same first letter to the same slot.

For integers, the **division method** $h(k) = k \bmod m$ works well when $m$ is a prime not close to a power of two. For strings, a **polynomial rolling hash** treats the characters as digits in some base $B$:

$$h(s) = \left(s_0 B^{n-1} + s_1 B^{n-2} + \dots + s_{n-1}\right) \bmod m,$$

computed efficiently with Horner's rule: start with 0 and, for each character, multiply by $B$ and add the character's code.

Hash values for dictionary keys must never change while the key is stored. That is why Python requires dictionary keys to be **hashable**, which in practice means immutable: strings, numbers, and tuples of immutable values can be keys, but lists cannot.

### Collisions are unavoidable

With more possible keys than slots (there are infinitely many strings), the pigeonhole principle guarantees collisions. Even with few keys, they come quickly: by the **birthday paradox**, a table of 365 slots has a better-than-even chance of a collision once 23 random keys are inserted. So every hash table needs a collision strategy.

### Separate chaining

Each slot holds a list (a **chain**) of all the entries that hashed to it. To insert, append to the chain of slot $h(k)$ (after checking the key is not already there). To look up, scan that one chain.

If $n$ keys are spread over $m$ slots, the **load factor** is $\alpha = n/m$, the average chain length. Assuming uniform hashing, an unsuccessful search examines $\alpha$ entries on average and a successful one about $1 + \alpha/2$. Keeping $\alpha$ bounded by a constant (for example, resizing when $\alpha > 1$) makes every operation $\Theta(1)$ on average. Chaining degrades gracefully: even at $\alpha = 2$ it still works, just more slowly.

### Open addressing

All entries live in the table itself, one per slot. On a collision, the table **probes** a sequence of alternative slots until it finds the key or an empty slot. For probe number $i = 0, 1, 2, \dots$:

| Strategy | Probe sequence | Behaviour |
| :--- | :--- | :--- |
| Linear probing | $(h(k) + i) \bmod m$ | simple and cache friendly, but forms long runs of filled slots (**primary clustering**) |
| Quadratic probing | $(h(k) + c_1 i + c_2 i^2) \bmod m$ | breaks up primary clusters; keys with the same start still follow the same path (**secondary clustering**) |
| Double hashing | $(h_1(k) + i \cdot h_2(k)) \bmod m$ | a second hash sets the step size, so different keys follow different paths; $h_2(k)$ must never be 0 |

Open addressing requires $\alpha < 1$ (the table can never hold more entries than slots), and performance falls sharply as $\alpha$ approaches 1. With linear probing, the expected number of probes for an unsuccessful search is about $\frac{1}{2}\left(1 + \frac{1}{(1 - \alpha)^2}\right)$: about 2.5 probes at $\alpha = 0.5$ but about 50 at $\alpha = 0.9$. Open-addressed tables therefore resize at a load factor around 0.5 to 0.75.

**Deletion** in open addressing needs care. Simply emptying a slot would break probe chains: a later search would stop at the hole and miss keys placed beyond it. Instead the slot is marked with a **tombstone** that searches skip over but insertions may reuse.

### Resizing

When the load factor passes a threshold, the table allocates a larger array (typically double the size) and **rehashes** every entry, because each key's index depends on $m$. A single resize costs $\Theta(n)$, but with geometric growth the cost is amortized $\Theta(1)$ per insertion, the same argument as for dynamic arrays.

### Worst case and adversaries

If every key hashes to the same slot, the table degenerates into a single list and every operation becomes $\Theta(n)$. This can happen with a poor hash function, or deliberately, when an attacker who knows the hash function submits many colliding keys (a **hash-flooding** denial-of-service attack). Modern languages defend against this: Python randomises string hashing per process (unless `PYTHONHASHSEED` is fixed), and Java's `HashMap` turns long chains into balanced trees.

### Summary of costs

| Operation | Average (bounded load factor) | Worst case |
| :--- | :--- | :--- |
| Insert | $\Theta(1)$ amortized | $\Theta(n)$ |
| Lookup | $\Theta(1)$ | $\Theta(n)$ |
| Delete | $\Theta(1)$ | $\Theta(n)$ |
| Iterate in key order | not supported efficiently | sort the keys: $\Theta(n \log n)$ |

Hash tables do not keep keys in sorted order. If you need ordered traversal, range queries, or the smallest key, use a balanced search tree instead.

## Worked examples

### Example 1: Polynomial string hashing

```python
def poly_hash(text, base=31, m=1_000_003):
    h = 0
    for ch in text:
        h = (h * base + ord(ch)) % m      # Horner's rule
    return h

for word in ("cat", "act", "tac", "dog"):
    print(word, poly_hash(word), poly_hash(word) % 11)
```

Output:

```text
cat 98262 10
act 96402 9
tac 114582 6
dog 99644 6
```

Anagrams such as `cat`, `act`, and `tac` get different hashes because each character's position changes its weight. A hash that simply added the character codes would give all three the same value, a classic weak hash function. The last column shows the slot in a table of size 11, and it shows a collision: `tac` and `dog` have different hash values but both land in slot 6. Reducing a large hash to a small table always causes collisions like this, which is why the table needs a strategy for them.

### Example 2: Linear probing by hand

Insert the keys 18, 41, 22, 44, 59, 32, 31, 73 into a table of size $m = 13$ with $h(k) = k \bmod 13$ and linear probing.

| Key | $h(k)$ | Probes | Final slot |
| :---: | :---: | :--- | :---: |
| 18 | 5 | 5 | 5 |
| 41 | 2 | 2 | 2 |
| 22 | 9 | 9 | 9 |
| 44 | 5 | 5 taken, 6 | 6 |
| 59 | 7 | 7 | 7 |
| 32 | 6 | 6 taken, 7 taken, 8 | 8 |
| 31 | 5 | 5, 6, 7, 8, 9 taken, 10 | 10 |
| 73 | 8 | 8, 9, 10 taken, 11 | 11 |

Final table: slot 2 = 41, 5 = 18, 6 = 44, 7 = 59, 8 = 32, 9 = 22, 10 = 31, 11 = 73. Slots 5 to 11 now form one long run. Any new key hashing anywhere into that run must walk to its end: this is primary clustering.

### Example 3: A hash map with separate chaining

```python
class ChainedHashMap:
    def __init__(self, capacity=8):
        self.buckets = [[] for _ in range(capacity)]
        self.size = 0

    def _bucket(self, key):
        return self.buckets[hash(key) % len(self.buckets)]

    def put(self, key, value):
        bucket = self._bucket(key)
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)       # overwrite existing key
                return
        bucket.append((key, value))
        self.size += 1
        if self.size / len(self.buckets) > 1.0:
            self._resize(2 * len(self.buckets))

    def get(self, key, default=None):
        for k, v in self._bucket(key):
            if k == key:
                return v
        return default

    def _resize(self, capacity):
        old = [pair for bucket in self.buckets for pair in bucket]
        self.buckets = [[] for _ in range(capacity)]
        for k, v in old:
            self._bucket(k).append((k, v))     # every key gets a new index

m = ChainedHashMap()
for i in range(20):
    m.put(f"user{i}", i * i)
m.put("user3", -1)
print(m.size, len(m.buckets), m.get("user7"), m.get("user3"), m.get("nobody", "missing"))
```

Output:

```text
20 32 49 -1 missing
```

The table started with 8 buckets and doubled to 16 when the ninth key arrived (load factor above 1), then to 32 after the seventeenth. Updating `"user3"` replaced its value rather than adding a duplicate, so the size stayed 20. Each resize rehashes every key because the bucket index depends on the number of buckets.

## Applications

- **Language runtimes**: Python's `dict` and `set` are open-addressed hash tables; object attributes and module namespaces are dictionaries too.
- **Databases**: hash indexes and hash joins match rows on equality in near-constant time per row.
- **Caching**: web caches, memoisation, and CDN lookups map keys to stored results.
- **Compilers and interpreters** keep symbol tables that map identifiers to their declarations.
- **Deduplication and counting**: counting word frequencies, finding duplicates, and checking membership in large sets all use hashing.

## Common mistakes

- **Using mutable objects as keys.** If a key's hash changed after insertion, the entry could never be found again; Python forbids lists as keys for this reason.
- **Writing a hash function that ignores part of the key,** such as only the first few characters, which causes heavy clustering.
- **Letting an open-addressed table fill up.** Probe counts explode as the load factor approaches 1.
- **Emptying slots on deletion in open addressing,** which breaks later searches; use tombstones.
- **Expecting sorted iteration or range queries.** Hash tables give fast exact lookups only.
- **Forgetting the worst case.** Average $O(1)$ assumes good hashing; adversarial inputs can force $O(n)$.

## Revision notes

- Hash table = hash function + array. Index = $h(k) \bmod m$.
- Good hash: deterministic, fast, uniform, uses the whole key. Keys must be immutable.
- Load factor $\alpha = n/m$. Keep it bounded and operations are $\Theta(1)$ on average.
- Chaining: lists per slot; tolerates $\alpha > 1$; average chain length $\alpha$.
- Open addressing: probe for a free slot. Linear (primary clustering), quadratic (secondary clustering), double hashing (best spread). Needs $\alpha < 1$; deletion uses tombstones.
- Resize by doubling and rehashing: amortized $\Theta(1)$ insertion. Worst case $\Theta(n)$ if keys collide.

## Practice questions

:::question basic
What is the load factor of a hash table with 600 keys and 800 slots, and what does it mean for separate chaining?
:::answer
$\alpha = 600/800 = 0.75$. With separate chaining it is the average chain length: each slot holds 0.75 entries on average, so an unsuccessful search scans about 0.75 entries and a successful one about $1 + 0.75/2 \approx 1.4$ entries (assuming uniform hashing).
:::

:::question basic
Why can a Python tuple of integers be a dictionary key but a list cannot?
:::answer
A dictionary finds a key by its hash, so the hash must stay the same for as long as the key is stored. A tuple of integers is immutable, so its hash never changes. A list can be modified after insertion, which would change its contents and therefore its hash, leaving the entry stranded in the wrong slot. Python prevents this by making lists unhashable.
:::

:::question intermediate
Insert 10, 22, 31, 4, 15, 28 into a table of size 11 using $h(k) = k \bmod 11$ and linear probing. Give the final slot of each key.
:::answer
10 goes to slot 10. 22 goes to slot 0 ($22 \bmod 11 = 0$). 31 goes to slot 9. 4 goes to slot 4. 15 hashes to 4, which is taken, so it probes slot 5. 28 hashes to 6, which is free, so slot 6. Final: 22 at 0, 4 at 4, 15 at 5, 28 at 6, 31 at 9, 10 at 10.
:::

:::question intermediate
In an open-addressed table, key A was inserted at slot 3, and key B, which also hashed to 3, was placed at slot 4. If A is deleted by simply emptying slot 3, what goes wrong when searching for B? How do tombstones fix it?
:::answer
A search for B starts at slot 3, finds it empty, and concludes that B is not in the table, because an empty slot normally means the probe sequence has ended. B is still at slot 4 but can no longer be found. A tombstone marks slot 3 as "deleted but occupied for searching purposes": searches continue past it to slot 4, while insertions may reuse it.
:::

:::question intermediate
Why does double hashing require that $h_2(k)$ is never 0, and why is it often chosen relatively prime to the table size?
:::answer
The probe sequence is $h_1(k) + i \cdot h_2(k)$. If $h_2(k) = 0$, every probe lands on the same slot and the search can never move on. If $h_2(k)$ shares a factor with $m$, the sequence visits only a fraction of the slots and might cycle without finding a free slot even though one exists. Making $m$ prime (or $h_2(k)$ odd with $m$ a power of two) guarantees the sequence can reach every slot.
:::

:::question advanced
A hash table using separate chaining doubles its capacity whenever the load factor exceeds 1. Explain why insertion is amortized $O(1)$ even though a resize rehashes all $n$ keys, and what assumption the $O(1)$ average lookup relies on.
:::answer
Resizes happen when the number of keys passes $m, 2m, 4m, \dots$, and each one rehashes the current keys, so the total rehashing work over $n$ insertions is at most $n + n/2 + n/4 + \dots < 2n$. Spread over $n$ insertions that is a constant per insertion, so insertion is amortized $O(1)$. The constant average lookup time relies on the hash function distributing keys roughly uniformly and independently over the buckets; if many keys collide, chains grow long and lookups degrade toward $O(n)$.
:::

## Further learning

- **Next:** *Binary Tree Traversals* begins the tree structures that, unlike hash tables, keep keys in order.
- **Related:** *Pattern Matching Basics* mentions Rabin-Karp, which applies rolling hashes to string search.
- **Related:** *Binary Search Trees (BST)* and *Balanced Search Trees* offer ordered alternatives with $O(\log n)$ operations.
