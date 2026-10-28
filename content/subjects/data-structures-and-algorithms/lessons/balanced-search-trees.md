---
lesson: balanced-search-trees
title: Balanced Search Trees (AVL & Red-Black)
summary: Keep a binary search tree's height logarithmic with rotations, using the AVL balance rule or the red-black colouring rules.
minutes: 60
type: theory
objectives:
  - Explain why an unbalanced BST degrades and what a balance invariant guarantees
  - Perform left, right, and double rotations and show that they preserve the BST order
  - Insert keys into an AVL tree, identifying the LL, RR, LR, and RL cases and the rotation each needs
  - State the red-black tree properties, explain why they bound the height by 2 log2(n + 1), and compare red-black trees with AVL trees and B-trees
---

## Introduction

A binary search tree answers search, insert, delete, floor, and range queries in time proportional to its height. With luck the height is about $\log_2 n$; with sorted input, which is common in practice (timestamps, auto-incremented IDs, alphabetical imports), the tree degenerates into a chain of height $n - 1$ and every operation becomes linear.

A **balanced search tree** is a BST that enforces an extra structural rule, the balance invariant, and repairs any violation after each update. The repairs are local restructurings called **rotations**, which take constant time and never break the search order. The result is a guaranteed height of $O(\log n)$ for any sequence of insertions and deletions. This lesson covers the two classic designs: the **AVL tree**, introduced by Georgy Adelson-Velsky and Evgenii Landis in 1962, and the **red-black tree**, the structure behind many standard library ordered maps.

**Before you start:** you should know binary search trees, including insertion and deletion.

## Core theory

### Rotations

A **right rotation** at node $y$ with left child $x$ makes $x$ the root of the subtree, with $y$ as its right child. The right subtree of $x$ (call it $B$) becomes the left subtree of $y$. A **left rotation** is the mirror image.

```text
        y                         x
       / \     rotate right      / \
      x   C    ------------>    A   y
     / \       <------------       / \
    A   B       rotate left       B   C
```

In both trees the in-order sequence is $A, x, B, y, C$, so a rotation **preserves the BST invariant**. It changes only three pointers, so it costs $O(1)$. What it does change is the height: rotating right moves subtree $A$ up one level and subtree $C$ down one level. Balanced trees use rotations to shift weight from a tall side to a short side.

### AVL trees

The **balance factor** of a node is $\text{height}(\text{left}) - \text{height}(\text{right})$, with the empty tree having height $-1$. An **AVL tree** is a BST in which every node's balance factor is $-1$, $0$, or $+1$.

**Why the height is logarithmic.** Let $N(h)$ be the minimum number of nodes in an AVL tree of height $h$. The sparsest such tree has a root, one subtree of height $h - 1$, and one of height $h - 2$, both as sparse as possible:

$$N(h) = N(h-1) + N(h-2) + 1, \qquad N(0) = 1, \; N(1) = 2.$$

This gives 1, 2, 4, 7, 12, 20, 33, ..., which equals $F_{h+3} - 1$, where $F_k$ is the $k$-th Fibonacci number. Fibonacci numbers grow like $\varphi^k$ with $\varphi \approx 1.618$, so the height of an AVL tree with $n$ nodes is less than about $1.44 \log_2 n$. In other words, an AVL tree is never more than about 44% taller than a perfectly balanced tree.

**Insertion.** Insert as in an ordinary BST, then walk back up the path to the root, updating each node's height. At the first node $z$ whose balance factor becomes $\pm 2$, one of four cases applies, named after the path from $z$ to the newly inserted key:

| Case | Shape at $z$ | Fix |
| :--- | :--- | :--- |
| LL | new key in the left subtree of $z$'s left child | right rotation at $z$ |
| RR | new key in the right subtree of $z$'s right child | left rotation at $z$ |
| LR | new key in the right subtree of $z$'s left child | left rotation at the left child, then right rotation at $z$ |
| RL | new key in the left subtree of $z$'s right child | right rotation at the right child, then left rotation at $z$ |

The LR and RL cases need a **double rotation**: the first rotation turns the "zig-zag" into a straight line, and the second fixes it. After an insertion, a single fix (one single or one double rotation) restores the subtree to the height it had before the insertion, so no ancestors need repair. Deletion is similar but may need a rotation at every level on the way up, which is still $O(\log n)$.

### Red-black trees

A **red-black tree** is a BST in which every node is coloured red or black and the empty children (written NIL) are treated as black leaves, subject to these rules:

1. The root is black.
2. A red node has no red child (no two reds in a row on any path).
3. Every path from a node down to a NIL leaf passes through the same number of black nodes. This number, counting the NIL leaf but not the starting node itself, is the node's **black-height**.

**Why the height is logarithmic.** By induction, a subtree whose root has black-height $b$ contains at least $2^b - 1$ internal nodes. Rule 2 means that at least half the nodes on any root-to-leaf path are black, so a tree of height $h$ has black-height at least $h/2$ and therefore $n \ge 2^{h/2} - 1$ nodes. Rearranging gives

$$h \le 2 \log_2 (n + 1).$$

**Insertion.** Insert the key as in a BST and colour it red. That cannot break rule 3, but it breaks rule 2 if the parent is red. Repair moves upward:

- **Red uncle** (the parent's sibling is red): recolour the parent and uncle black and the grandparent red, then continue checking from the grandparent.
- **Black uncle:** rotate. If the new node is an inner grandchild (zig-zag), first rotate at the parent to make it an outer grandchild. Then rotate at the grandparent and swap the colours of the parent and grandparent.

Finally colour the root black. An insertion performs at most two rotations, and a deletion at most three; the remaining work is recolouring.

### Comparing the designs

| | AVL tree | Red-black tree | B-tree |
| :--- | :--- | :--- | :--- |
| Height bound | about $1.44 \log_2 n$ | $2 \log_2 (n + 1)$ | $O(\log_m n)$ for fan-out $m$ |
| Rotations per insert | at most one single or double | at most two | none; nodes split instead |
| Rotations per delete | up to $O(\log n)$ | at most three | none; nodes merge or borrow |
| Best suited to | lookup-heavy workloads in memory | mixed workloads in memory | data on disk or SSD |

AVL trees are more strictly balanced, so lookups visit slightly fewer nodes. Red-black trees do less restructuring per update, which is why they are the usual choice for general-purpose library maps. B-trees keep hundreds of keys per node so that each disk read narrows the search as much as possible.

## Worked examples

### Example 1: An AVL tree under sorted insertions

```python
class Node:
    def __init__(self, key):
        self.key, self.left, self.right, self.height = key, None, None, 0

def h(node):
    return node.height if node else -1

def update(node):
    node.height = 1 + max(h(node.left), h(node.right))

def balance(node):
    return h(node.left) - h(node.right)

def rotate_right(y):
    x = y.left
    y.left, x.right = x.right, y
    update(y)                                 # y is now below x, so update it first
    update(x)
    return x

def rotate_left(x):
    y = x.right
    x.right, y.left = y.left, x
    update(x)
    update(y)
    return y

def insert(node, key):
    if node is None:
        return Node(key)
    if key < node.key:
        node.left = insert(node.left, key)
    else:
        node.right = insert(node.right, key)
    update(node)
    b = balance(node)
    if b > 1:                                 # left-heavy
        if balance(node.left) < 0:            # LR: straighten the zig-zag first
            node.left = rotate_left(node.left)
        return rotate_right(node)             # LL
    if b < -1:                                # right-heavy
        if balance(node.right) > 0:           # RL
            node.right = rotate_right(node.right)
        return rotate_left(node)              # RR
    return node

def show(node):
    if node is None:
        return "-"
    if node.left is None and node.right is None:
        return str(node.key)
    return f"{node.key}({show(node.left)}, {show(node.right)})"

root = None
for k in range(1, 8):
    root = insert(root, k)
    print(f"insert {k}: {show(root)}")

for keys in ([30, 10, 20], [10, 30, 20]):
    root = None
    for k in keys:
        root = insert(root, k)
    print(keys, "->", show(root))
```

Output:

```text
insert 1: 1
insert 2: 1(-, 2)
insert 3: 2(1, 3)
insert 4: 2(1, 3(-, 4))
insert 5: 2(1, 4(3, 5))
insert 6: 4(2(1, 3), 5(-, 6))
insert 7: 4(2(1, 3), 6(5, 7))
[30, 10, 20] -> 20(10, 30)
[10, 30, 20] -> 20(10, 30)
```

A plain BST would turn the keys 1 to 7 into a chain of height 6. The AVL tree performs an RR rotation after inserting 3, 5, 6, and 7 and ends as a perfect tree of height 2. Inserting 3 makes node 1 right-heavy with balance factor $-2$; a left rotation at 1 lifts 2 to the root. Inserting 6 unbalances the root itself: a left rotation at 2 makes 4 the new root, and 4's old left child, 3, becomes 2's right child.

The last two lines are the double-rotation cases. In `[30, 10, 20]`, the key 20 lands in the right subtree of 30's left child (LR): a left rotation at 10 followed by a right rotation at 30 makes 20 the root. `[10, 30, 20]` is the mirror-image RL case.

### Example 2: Tracing an LR insertion by hand

Insert 20, 4, 26, 3, 9, 15 into an empty AVL tree.

| Step | Tree after the step | Note |
| :--- | :--- | :--- |
| 20, 4, 26 | 20(4, 26) | balanced |
| 3 | 20(4(3, -), 26) | root balance $+1$ |
| 9 | 20(4(3, 9), 26) | root balance $+1$ |
| 15 | before fixing: 20(4(3, 9(-, 15)), 26) | root balance $+2$ |

The key 15 went left at 20 and then right at 4, so this is the LR case at $z = 20$. First rotate left at 4, which lifts 9: the left subtree becomes 9(4(3, -), 15). Then rotate right at 20, which lifts 9 to the root and hands 9's right subtree (15) to 20 as its new left child:

```text
before: 20(4(3, 9(-, 15)), 26)
after:  9(4(3, -), 20(15, 26))
```

Every node now has balance factor $0$ or $+1$ (node 4 has a left child only). The height is 2, the same as before 15 was inserted, which is why no ancestor of the repaired subtree would ever need attention.

### Example 3: Checking the red-black rules

Full red-black insertion code is long, but checking the rules is short and shows exactly what they mean. `black_count` returns the number of black nodes on every path from a node down to a NIL leaf, counting both ends, or reports the first rule it finds broken.

```python
class Node:
    def __init__(self, key, color, left=None, right=None):
        self.key, self.color, self.left, self.right = key, color, left, right

def black_count(node):
    if node is None:
        return 1                                   # NIL leaves are black
    if node.color == "R":
        for child in (node.left, node.right):
            if child is not None and child.color == "R":
                raise ValueError(f"red node {node.key} has a red child")
    left, right = black_count(node.left), black_count(node.right)
    if left != right:
        raise ValueError(f"black-heights differ below {node.key}")
    return left + (1 if node.color == "B" else 0)

def check(root):
    try:
        if root is not None and root.color != "B":
            raise ValueError("the root is red")
        return f"valid, black-height {black_count(root) - 1}"   # the root itself is not counted
    except ValueError as error:
        return f"invalid: {error}"

B, R = "B", "R"
valid = Node(13, B, Node(8, R, Node(1, B), Node(11, B)), Node(17, R, Node(15, B), Node(25, B)))
red_red = Node(10, B, Node(5, R, Node(3, R)), Node(15, B))
unequal = Node(10, B, Node(5, B))

print(check(valid))
print(check(red_red))
print(check(unequal))
```

Output:

```text
valid, black-height 2
invalid: red node 5 has a red child
invalid: black-heights differ below 10
```

Below the root of the valid tree, every path meets exactly one black node (one of 1, 11, 15, 25) and then a black NIL leaf, so the root's black-height is 2. In the second tree, red 5 has red child 3. The third tree shows why a black node cannot have just one black child: the left side of 10 passes through black 5 and then a NIL leaf, two black nodes, while the right side reaches a NIL leaf immediately, one black node.

## Applications

- **Standard library ordered containers:** Java's `TreeMap` and `TreeSet` are documented as red-black trees, and the major C++ standard library implementations build `std::map` and `std::set` on red-black trees.
- **Operating system kernels:** the Linux kernel provides a red-black tree library used in many subsystems; for example, the Completely Fair Scheduler kept runnable tasks in a red-black tree ordered by their virtual runtime.
- **Databases and file systems** use B-trees and B+ trees for indexes because one node fits one disk page; a B-tree with hundreds of keys per node needs only three or four node reads to search millions of keys.
- **Lookup-heavy in-memory indexes** can favour AVL trees, whose stricter balance gives slightly shorter search paths.
- **Interval and order-statistic trees** are typically built on a balanced tree, with extra fields kept correct during rotations.

## Common mistakes

- **Updating heights in the wrong order after a rotation.** The node that moved down must be updated before the node that moved up, because the new parent's height depends on its children.
- **Choosing a single rotation for a zig-zag case.** A single rotation applied to an LR or RL shape just produces the mirror-image imbalance; a double rotation is required.
- **Forgetting that NIL leaves count as black** when computing black-heights, or counting the starting node inconsistently.
- **Assuming a red-black tree is as tightly balanced as an AVL tree.** Its height can approach $2 \log_2 n$, while an AVL tree stays below about $1.44 \log_2 n$.
- **Forgetting to reattach the rotated subtree** to its parent; a rotation returns a new subtree root, which the parent must store.

## Revision notes

- Rotations preserve in-order order, take $O(1)$ time, and move one subtree up and another down.
- AVL: every balance factor is in $\{-1, 0, +1\}$. Minimum nodes satisfy $N(h) = N(h-1) + N(h-2) + 1$, so the height is at most about $1.44 \log_2 n$.
- AVL insertion cases: LL (rotate right), RR (rotate left), LR (left then right), RL (right then left). One fix per insertion suffices.
- Red-black: black root, no red node with a red child, equal black-heights on all paths. Height $\le 2 \log_2(n+1)$.
- Red-black insertion: insert red; red uncle means recolour and move up; black uncle means one or two rotations.
- AVL for lookup-heavy workloads, red-black for general-purpose maps, B-trees for disk-based indexes.

## Practice questions

:::question basic
What two properties of a rotation make it suitable for rebalancing a binary search tree?
:::answer
It preserves the in-order sequence of the keys, so the tree remains a valid BST, and it changes only a constant number of pointers, so it takes $O(1)$ time. It also changes the heights of subtrees: one side moves up a level and the other moves down, which is what rebalancing needs.
:::

:::question basic
Compute every balance factor in the tree 10(5(2, -), 20) and state whether it is an AVL tree.
:::answer
Node 2 is a leaf: balance $(-1) - (-1) = 0$. Node 5 has a left child of height 0 and no right child: $0 - (-1) = +1$. Node 20 is a leaf: 0. The root has a left subtree of height 1 and a right subtree of height 0: $1 - 0 = +1$. Every balance factor is in $\{-1, 0, +1\}$, so it is an AVL tree.
:::

:::question intermediate
Insert 50, 40, 30 into an empty AVL tree. Which case occurs, and what is the final tree?
:::answer
After 50 and 40, the tree is 50(40, -). Inserting 30 puts it in the left subtree of 50's left child, so node 50 has balance factor $+2$ in the LL case. A right rotation at 50 makes 40 the root, giving 40(30, 50), with every balance factor 0.
:::

:::question intermediate
What is the minimum number of nodes in an AVL tree of height 4? Show the calculation.
:::answer
Use $N(h) = N(h-1) + N(h-2) + 1$ with $N(0) = 1$ and $N(1) = 2$: $N(2) = 2 + 1 + 1 = 4$, $N(3) = 4 + 2 + 1 = 7$, $N(4) = 7 + 4 + 1 = 12$. So an AVL tree of height 4 has at least 12 nodes. A perfect tree of height 4 has 31, so AVL trees allow a good deal of imbalance while still keeping the height logarithmic.
:::

:::question intermediate
A red node in a red-black tree has exactly one non-NIL child. Explain why this situation is impossible.
:::answer
The child must be black, because a red node cannot have a red child. Paths from the red node through that black child meet at least one black node before reaching NIL, while the path through the NIL side meets none. The black-heights of the two sides would differ, breaking the equal black-height rule. So a red node has either two NIL children or two non-NIL black children.
:::

:::question advanced
Prove that a red-black tree with $n$ internal nodes has height at most $2 \log_2(n + 1)$.
:::answer
First show by induction on height that a subtree rooted at $x$ contains at least $2^{bh(x)} - 1$ internal nodes, where $bh(x)$ is the black-height of $x$. For a NIL leaf, $bh = 0$ and $2^0 - 1 = 0$. Otherwise each child has black-height at least $bh(x) - 1$, so the subtree has at least $2(2^{bh(x)-1} - 1) + 1 = 2^{bh(x)} - 1$ nodes. Next, on any path from the root to a leaf, no two red nodes are adjacent, so at least half the nodes are black, giving $bh(\text{root}) \ge h/2$. Therefore $n \ge 2^{h/2} - 1$, so $h/2 \le \log_2(n + 1)$ and $h \le 2 \log_2(n + 1)$.
:::

:::question advanced
A database must index 100 million keys stored on disk. Explain why it would use a B-tree rather than a red-black tree.
:::answer
On disk, the cost that matters is the number of page reads, not the number of comparisons. A red-black tree with $10^8$ keys has height at least $\log_2 10^8 \approx 27$, and its nodes are small and scattered, so a search could need about 27 or more separate page reads. A B-tree node fills a whole page and holds hundreds of keys; with a fan-out of a few hundred, three or four levels cover $10^8$ keys, so a search needs only a handful of reads, and the top levels usually stay cached in memory. B-trees also keep keys in large sorted blocks, which makes range scans sequential.
:::

## Further learning

- **Next:** *Tries & Prefix Search* organises strings by their characters instead of by comparing whole keys.
- **Related:** *Binary Search Trees (BST)* covers the search, insertion, and deletion algorithms that balanced trees extend.
- **Related:** *Amortized Analysis* explains how to reason about the cost of a sequence of updates.
