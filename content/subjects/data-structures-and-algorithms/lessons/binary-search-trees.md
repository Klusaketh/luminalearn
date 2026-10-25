---
lesson: binary-search-trees
title: Binary Search Trees (BST)
summary: Keep keys ordered in a binary tree so that search, insertion, deletion, and range queries follow a single root-to-leaf path.
minutes: 60
type: theory
objectives:
  - State the binary search tree invariant and explain why in-order traversal yields the keys in sorted order
  - Implement search, insertion, minimum, successor, and deletion, including the two-child case
  - Analyse BST operations as O(h) and explain how insertion order determines the height h
  - Answer ordered queries such as floor, ceiling, and range search that hash tables cannot support
---

## Introduction

A hash table finds a key in expected constant time, but it knows nothing about order. It cannot tell you the smallest key, the next appointment after 14:30, or every customer whose surname falls between "Patel" and "Singh". A sorted array answers all of these with binary search, but inserting into it shifts up to $n$ elements.

A **binary search tree (BST)** combines the strengths of both. It stores keys in a binary tree arranged so that, at every node, smaller keys lie to the left and larger keys lie to the right. Searching follows one path from the root, discarding a whole subtree at every step, just as binary search discards half an array. Unlike a sorted array, inserting or deleting a key only changes a few pointers. The catch is that the tree's speed depends on its height, which depends on the order in which keys arrive.

**Before you start:** you should know binary tree traversals and binary search.

## Core theory

### The invariant

A binary search tree is a binary tree in which, for every node with key $k$:

- every key in the node's **left subtree** is less than $k$, and
- every key in the node's **right subtree** is greater than $k$.

The rule concerns **entire subtrees**, not just the immediate children. This lesson assumes distinct keys; a structure that must store duplicates can keep a count in each node or consistently send equal keys to one side.

The invariant has an immediate consequence: an **in-order traversal visits the keys in increasing order**. By induction on the tree's size, in-order lists the left subtree in sorted order (all smaller than $k$), then $k$, then the right subtree in sorted order (all larger than $k$).

### Search, minimum, and maximum

To search for $x$, start at the root. If $x$ equals the node's key, stop. If $x$ is smaller, the invariant says it can only be in the left subtree, so move left; otherwise move right. If you fall off the tree, $x$ is absent.

The **minimum** is found by following left pointers until there are none; the **maximum** by following right pointers. Each of these operations follows a single downward path, so it costs $O(h)$, where $h$ is the tree's height.

### Insertion

Insert by searching for the key. The search ends at an empty position exactly where the key would have to be, and the new key becomes a leaf there. No existing node moves, and the invariant still holds. The cost is $O(h)$.

### Successor

The **in-order successor** of a node is the next larger key:

- If the node has a right subtree, the successor is the minimum of that right subtree.
- Otherwise, it is the nearest ancestor whose left subtree contains the node: the last node at which the search path from the root turned left.

### Deletion

Deleting node $z$ has three cases:

1. **$z$ is a leaf:** remove it.
2. **$z$ has one child:** replace $z$ with that child (splice it out). Everything in the child's subtree was already on the correct side of $z$'s parent.
3. **$z$ has two children:** find its successor $s$, the minimum of the right subtree. Copy $s$'s key into $z$, then delete $s$ from the right subtree. Because $s$ is a minimum, it has no left child, so that second deletion is case 1 or case 2.

Using the successor works because it is larger than everything in $z$'s left subtree and smaller than everything else in the right subtree, so it can take $z$'s place without breaking the invariant. The predecessor (maximum of the left subtree) works equally well. Deletion costs $O(h)$.

### Height decides everything

Every operation above is $O(h)$, so the shape of the tree matters:

| Insertion order | Shape | Height for $n$ keys |
| :--- | :--- | :--- |
| Sorted (or reverse sorted) | degenerate chain | $n - 1$ |
| Random | bushy | $O(\log n)$ expected |
| Median first, recursively | perfectly balanced | $\lfloor \log_2 n \rfloor$ |

For keys inserted in random order, a search for a present key makes about $2 \ln n \approx 1.39 \log_2 n$ comparisons on average. But real data is often sorted or nearly sorted (timestamps, IDs from a counter), which produces the worst case. Balanced search trees, covered in the next lesson, restructure themselves to keep $h = O(\log n)$ whatever the input.

### Ordered operations

Because a BST keeps its keys in order, it supports queries that hash tables cannot:

- **floor(x)**: the largest key $\le x$; **ceiling(x)**: the smallest key $\ge x$.
- **range(lo, hi)**: all keys in $[lo, hi]$, in sorted order, in $O(h + k)$ time for $k$ results.
- **min, max, successor, predecessor**, and, with each node storing its subtree size, **rank** (how many keys are smaller) and **select** (the $i$-th smallest key).

| Operation | Sorted array | Hash table | BST (height $h$) |
| :--- | :--- | :--- | :--- |
| Search | $O(\log n)$ | $O(1)$ expected | $O(h)$ |
| Insert or delete | $O(n)$ | $O(1)$ expected | $O(h)$ |
| Min, max, floor, successor | $O(\log n)$ | $O(n)$ | $O(h)$ |
| Sorted listing | $O(n)$ | $O(n \log n)$ (needs a sort) | $O(n)$ |

## Worked examples

### Example 1: Building and searching a BST

Inserting the keys 50, 30, 70, 20, 40, 60, 80, 35, 45, 65 in that order produces this tree:

```text
          50
        /    \
      30      70
     /  \    /  \
   20   40  60   80
       /  \   \
      35  45   65
```

```python
class Node:
    def __init__(self, key):
        self.key, self.left, self.right = key, None, None

def insert(node, key):
    if node is None:
        return Node(key)
    if key < node.key:
        node.left = insert(node.left, key)
    elif key > node.key:
        node.right = insert(node.right, key)
    return node                       # an equal key is ignored: no duplicates

def search(node, key):
    path = []
    while node is not None:
        path.append(node.key)
        if key == node.key:
            return True, path
        node = node.left if key < node.key else node.right
    return False, path

def inorder(node):
    return inorder(node.left) + [node.key] + inorder(node.right) if node else []

root = None
for k in [50, 30, 70, 20, 40, 60, 80, 35, 45, 65]:
    root = insert(root, k)

print(inorder(root))
print(search(root, 45))
print(search(root, 62))
```

Output:

```text
[20, 30, 35, 40, 45, 50, 60, 65, 70, 80]
(True, [50, 30, 40, 45])
(False, [50, 70, 60, 65])
```

The search for 45 goes left at 50 (45 < 50), right at 30, and right at 40. The search for 62 visits four nodes before falling off the tree at the empty left child of 65; if 62 were inserted now, it would become exactly that left child. Note the pattern `node.left = insert(node.left, key)`: the recursive call returns the (possibly new) subtree root, and the parent stores it.

### Example 2: Deleting in all three cases

```python
class Node:
    def __init__(self, key):
        self.key, self.left, self.right = key, None, None

def insert(node, key):
    if node is None:
        return Node(key)
    if key < node.key:
        node.left = insert(node.left, key)
    elif key > node.key:
        node.right = insert(node.right, key)
    return node

def min_node(node):
    while node.left is not None:
        node = node.left
    return node

def delete(node, key):
    if node is None:
        return None                         # key not present
    if key < node.key:
        node.left = delete(node.left, key)
    elif key > node.key:
        node.right = delete(node.right, key)
    else:
        if node.left is None:               # no child or only a right child
            return node.right
        if node.right is None:              # only a left child
            return node.left
        successor = min_node(node.right)    # two children
        node.key = successor.key
        node.right = delete(node.right, successor.key)
    return node

def show(node):
    if node is None:
        return "-"
    if node.left is None and node.right is None:
        return str(node.key)
    return f"{node.key}({show(node.left)}, {show(node.right)})"

root = None
for k in [50, 30, 70, 20, 40, 60, 80, 35, 45, 65]:
    root = insert(root, k)

print("start:", show(root))
for key in (20, 60, 50):
    root = delete(root, key)
    print(f"delete {key}:", show(root))
```

Output:

```text
start: 50(30(20, 40(35, 45)), 70(60(-, 65), 80))
delete 20: 50(30(-, 40(35, 45)), 70(60(-, 65), 80))
delete 60: 50(30(-, 40(35, 45)), 70(65, 80))
delete 50: 65(30(-, 40(35, 45)), 70(-, 80))
```

Deleting 20 removes a leaf. Deleting 60 splices out a node with one child, so 65 moves up to become 70's left child. Deleting the root 50 is the two-child case: its successor is the minimum of the right subtree, 65, which is copied into the root and then removed from its old position.

### Example 3: Floor and range queries

```python
class Node:
    def __init__(self, key):
        self.key, self.left, self.right = key, None, None

def insert(node, key):
    if node is None:
        return Node(key)
    if key < node.key:
        node.left = insert(node.left, key)
    elif key > node.key:
        node.right = insert(node.right, key)
    return node

def floor(node, x):
    best = None
    while node is not None:
        if x == node.key:
            return x
        if x < node.key:
            node = node.left
        else:
            best = node.key            # node.key <= x: a candidate, look for a larger one
            node = node.right
    return best

def range_query(node, lo, hi, out):
    if node is None:
        return out
    if lo < node.key:                  # the left subtree may hold keys >= lo
        range_query(node.left, lo, hi, out)
    if lo <= node.key <= hi:
        out.append(node.key)
    if node.key < hi:                  # the right subtree may hold keys <= hi
        range_query(node.right, lo, hi, out)
    return out

root = None
for k in [50, 30, 70, 20, 40, 60, 80, 35, 45, 65]:
    root = insert(root, k)

print(floor(root, 62), floor(root, 45), floor(root, 19))
print(range_query(root, 33, 62, []))
```

Output:

```text
60 45 None
[35, 40, 45, 50, 60]
```

For `floor(62)`, every time the search moves right it records the current key as the best candidate so far (50, then 60), and it stops at the empty left child of 65. No key is at most 19, so that floor is `None`. The range query never enters the subtree of 20 or 80: at node 30 it skips the left side because nothing there can be at least 33, and at 70 it skips the right side.

### Example 4: Insertion order and height

```python
class Node:
    def __init__(self, key):
        self.key, self.left, self.right = key, None, None

def insert(root, key):                  # iterative, so a deep tree cannot overflow the call stack
    new = Node(key)
    if root is None:
        return new
    node = root
    while True:
        side = "left" if key < node.key else "right"
        child = getattr(node, side)
        if child is None:
            setattr(node, side, new)
            return root
        node = child

def height(root):                       # number of levels minus one, computed level by level
    h, level = -1, [root] if root else []
    while level:
        h += 1
        level = [c for n in level for c in (n.left, n.right) if c]
    return h

def build(keys):
    root = None
    for k in keys:
        root = insert(root, k)
    return root

def median_first(lo, hi):
    if lo > hi:
        return []
    mid = (lo + hi) // 2
    return [mid] + median_first(lo, mid - 1) + median_first(mid + 1, hi)

def scrambled(n, seed=12345):           # a Fisher-Yates shuffle driven by a fixed generator
    keys, state = list(range(1, n + 1)), seed
    for i in range(n - 1, 0, -1):
        state = (1103515245 * state + 12345) % 2**31
        j = state % (i + 1)
        keys[i], keys[j] = keys[j], keys[i]
    return keys

n = 1023
print("sorted order:      ", height(build(range(1, n + 1))))
print("scrambled order:   ", height(build(scrambled(n))))
print("median-first order:", height(build(median_first(1, n))))
```

Output:

```text
sorted order:       1022
scrambled order:    20
median-first order: 9
```

The same 1023 keys produce heights from 9 to 1022. Inserting in sorted order makes every key the right child of the previous one, so searching for the largest key takes 1023 comparisons, no better than a linked list. A scrambled order gives a height of 20, about twice the minimum, and the median-first order builds a perfect tree of height $\log_2 1024 - 1 = 9$.

## Applications

- **Ordered maps and sets** in standard libraries, such as Java's `TreeMap` and `TreeSet` and C++'s `std::map` and `std::set`, are balanced binary search trees, chosen when keys must be kept in order.
- **Database and file-system indexes** use B-trees and B+ trees, multiway generalisations of the BST designed so that each node fills a disk page.
- **Scheduling and time-series lookups** use floor and ceiling queries: "the next event after time $t$" or "the most recent reading before $t$".
- **Range reporting**, for example every order with a price between two values, in time proportional to the height plus the number of results.
- **Augmented trees** such as order-statistic trees and interval trees store extra information in each node to answer rank, selection, and overlap queries.

## Common mistakes

- **Checking only parent-child pairs.** A tree with root 10, left child 5, and 12 as the right child of 5 satisfies every parent-child comparison, but 12 lies in 10's left subtree, so it is not a BST. Validation must carry lower and upper bounds down the tree.
- **Forgetting to store the result of the recursive call,** as in `insert(node.left, key)` instead of `node.left = insert(node.left, key)`, so a newly created node is never attached.
- **Copying the successor's key in the two-child case but not deleting the successor,** which leaves the key in the tree twice.
- **Assuming $O(\log n)$ performance.** Without balancing, sorted input produces a chain and every operation becomes $O(n)$.
- **Handling duplicates inconsistently,** for example sending equal keys left on insertion but right on search, so stored keys cannot be found.

## Revision notes

- Invariant: left subtree < node < right subtree, for every node and its entire subtrees.
- In-order traversal of a BST gives sorted order.
- Search, insert, delete, min, max, successor, floor, and ceiling all follow one path: $O(h)$.
- Successor: minimum of the right subtree, or else the last ancestor where the path turned left.
- Delete: leaf (remove), one child (splice), two children (copy the successor, then delete the successor).
- Height ranges from $\lfloor \log_2 n \rfloor$ to $n - 1$; sorted insertion gives the worst case.
- BSTs support ordered queries (floor, ceiling, range, rank) that hash tables do not.

## Practice questions

:::question basic
Insert 8, 3, 10, 1, 6, 14, 4, 7, 13 in that order into an empty BST. Describe the tree, give its in-order traversal, and state its height.
:::answer
The root is 8. Its left child is 3, with children 1 and 6; 6 has children 4 and 7. The right child of 8 is 10, which has only a right child, 14, whose left child is 13. In-order: 1 3 4 6 7 8 10 13 14. The longest root-to-leaf paths (8, 3, 6, 4 and 8, 10, 14, 13) have 3 edges, so the height is 3.
:::

:::question basic
Explain why an in-order traversal of a BST lists the keys in increasing order.
:::answer
Argue by induction on the size of the tree. An empty tree is trivially listed in order. For a tree with root key $k$, in-order first lists the left subtree, which by the induction hypothesis is in increasing order and contains only keys less than $k$. Then it lists $k$, and then the right subtree, which is in increasing order and contains only keys greater than $k$. Joining the three parts gives an increasing sequence.
:::

:::question intermediate
Delete 3 from the tree built in the first question. Which case applies, and what does the tree look like afterwards?
:::answer
Node 3 has two children (1 and 6), so its key is replaced by its successor, the minimum of its right subtree: follow left pointers from 6 to reach 4. Copy 4 into the node that held 3, then delete the original 4, which is a leaf. The result: root 8; left child 4 with children 1 and 6; 6 now has only the right child 7; the right side (10, 14, 13) is unchanged.
:::

:::question intermediate
Is the tree with root 10, left child 5 (whose children are 2 and 12), and right child 15 a valid BST? Describe an algorithm that checks validity correctly.
:::answer
No. Every parent-child pair looks correct, but 12 is in the left subtree of 10 and is larger than 10. A correct check passes an allowed interval down the tree: the root may hold any key; when moving to a left child, the upper bound becomes the parent's key; when moving to a right child, the lower bound becomes the parent's key. A node is invalid if its key is outside its interval. Here, node 12 must lie in $(5, 10)$ and fails. The check visits each node once, so it is $O(n)$. Equivalently, check that the in-order traversal is strictly increasing.
:::

:::question intermediate
What is the worst-case time to search a BST with $n$ keys, and what insertion order produces that case?
:::answer
$\Theta(n)$. Inserting the keys in sorted (or reverse sorted) order makes each new key a child of the previous one, so the tree is a chain of height $n - 1$, and searching for the deepest key compares against all $n$ keys.
:::

:::question advanced
In the tree from Example 1, find the in-order successor of 45 and of 65 without using parent pointers, and explain the rule you used.
:::answer
Neither node has a right subtree, so the successor is the last ancestor at which the search path from the root turned left. The path to 45 is 50 (left), 30 (right), 40 (right), 45, and the last left turn was at 50, so the successor of 45 is 50. The path to 65 is 50 (right), 70 (left), 60 (right), 65, so the successor of 65 is 70. Both agree with the sorted list 20, 30, 35, 40, 45, 50, 60, 65, 70, 80.
:::

:::question advanced
How can a BST answer "how many keys are smaller than $x$?" in $O(h)$ time, and what extra work do insertions and deletions need?
:::answer
Store in every node the size of its subtree. Search for $x$ from the root with a running count: when moving right from a node, add the size of that node's left subtree plus one (the node itself), because all of them are smaller than $x$; when moving left, add nothing; if $x$ is found, add the size of its left subtree. The answer is the final count, after one root-to-leaf path. Insertions and deletions must update the size of every node on the path they follow, which keeps them $O(h)$.
:::

## Further learning

- **Next:** *Balanced Search Trees (AVL & Red-Black)* shows how rotations keep the height logarithmic for any insertion order.
- **Related:** *Binary Search & Invariants* applies the same halving idea to sorted arrays.
- **Related:** *Hash Functions & Collision Handling* covers the unordered alternative with expected constant-time lookups.
