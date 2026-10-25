---
lesson: binary-tree-traversals
title: Binary Tree Traversals
summary: Visit every node of a binary tree in pre-order, in-order, post-order, and level order, recursively and iteratively, and choose the right order for each task.
minutes: 60
type: theory
objectives:
  - Use binary tree terminology precisely, including depth, height, and full, complete, and perfect trees
  - Perform pre-order, in-order, and post-order traversals by hand and in code, both recursively and with an explicit stack
  - Perform a level-order traversal with a queue and group the nodes by level
  - Choose the traversal order that suits a task such as evaluating, copying, freeing, or printing a tree
---

## Introduction

Arrays and linked lists are linear: each element has one successor, so there is only one natural way to walk through them. Many kinds of data are hierarchical instead. A file system has folders inside folders, a web page is a tree of nested HTML elements, an organisation chart has managers and reports, and a compiler turns the expression `(3 + 4) * (5 - 2)` into a tree of operators and operands.

A **binary tree** is the simplest hierarchical structure: every node has at most two children, called the left child and the right child. To do anything with every node (print it, sum it, copy it, free it) we need a **traversal**, a systematic way of visiting each node exactly once. Because a node has two subtrees, there are several sensible orders, and each one suits different tasks. This lesson covers the four standard orders, how to implement them recursively and iteratively, what they cost, and how to pick the right one.

**Before you start:** you should know recursion, stacks, and queues.

## Core theory

### Terminology

- The **root** is the top node; it has no parent. Every other node has exactly one **parent**.
- A **leaf** has no children; an **internal node** has at least one.
- The **depth** of a node is the number of edges on the path from the root to it. The root has depth 0.
- The **height** of a tree is the number of edges on the longest path from the root to a leaf. A single node has height 0; by convention the empty tree has height $-1$.
- The **subtree** rooted at a node consists of that node and all its descendants.

Some shapes have names:

| Shape | Definition |
| :--- | :--- |
| Full | every node has 0 or 2 children |
| Complete | every level is full except possibly the last, which is filled from the left |
| Perfect | every internal node has 2 children and all leaves have the same depth |
| Degenerate | every internal node has exactly one child, so the tree is effectively a linked list |

A perfect tree of height $h$ has $2^{h+1} - 1$ nodes, of which $2^h$ are leaves. Turning this around, a binary tree with $n$ nodes has height at least $\lfloor \log_2 n \rfloor$ and at most $n - 1$ (the degenerate case). That range matters because many tree operations cost time proportional to the height.

### Depth-first orders

A depth-first traversal finishes one whole subtree before starting the other. The three classic orders differ only in **when the node itself is visited** relative to its two subtrees:

| Order | Sequence | Typical use |
| :--- | :--- | :--- |
| Pre-order | node, left subtree, right subtree | copying or serialising a tree, printing a hierarchy |
| In-order | left subtree, node, right subtree | listing a binary search tree in sorted order, infix expressions |
| Post-order | left subtree, right subtree, node | evaluating expressions, computing sizes and heights, freeing memory |

Each definition is recursive: "visit the left subtree" means traverse it in the same order. For example, consider this tree:

```text
        F
      /   \
     B     G
    / \     \
   A   D     I
      / \   /
     C   E H
```

Pre-order visits F first, then all of F's left subtree (B, A, D, C, E), then all of the right subtree (G, I, H). In-order visits everything left of F, then F, then everything to its right, which gives A B C D E F G H I. Post-order visits F last.

### Level order

A **level-order** (breadth-first) traversal visits nodes by increasing depth, and left to right within a level: F, B, G, A, D, I, C, E, H. It uses a **queue**: dequeue a node, visit it, enqueue its children. Because children join the back of the queue, all nodes of depth $d$ are dequeued before any node of depth $d + 1$.

### Cost

Every traversal visits each node once and does constant work per node, so all four take $\Theta(n)$ time. Their memory use differs:

- A depth-first traversal keeps one stack frame (or explicit stack entry) per node on the current root-to-node path, so it needs $O(h)$ extra space. That is $O(\log n)$ for a balanced tree but $O(n)$ for a degenerate one.
- A level-order traversal holds up to one whole level in its queue, so it needs $O(w)$ space, where $w$ is the maximum width. The last level of a perfect tree holds about half of all nodes, so $w$ can be $\Theta(n)$.

### Iterative versions

Recursion uses the call stack implicitly. An explicit stack does the same job without risking a stack overflow on deep trees:

- **Pre-order:** push the root; repeatedly pop a node, visit it, and push its right child and then its left child. The left child is pushed last, so it is popped (visited) first.
- **In-order:** walk left from the current node, pushing every node passed; when you can go no further, pop a node, visit it, and move to its right child.
- **Post-order:** a pre-order that visits node, right, left produces exactly the reverse of post-order, so collect that sequence and reverse it.

### Reconstructing a tree

If all keys are distinct, the pre-order and in-order sequences together determine the tree uniquely: the first pre-order key is the root, and its position in the in-order sequence splits the remaining keys into the left and right subtrees. Pre-order and post-order together are not enough in general, because a node with a single child produces the same sequences whether the child is on the left or the right.

## Worked examples

### Example 1: The four traversals

```python
from collections import deque

class Node:
    def __init__(self, key, left=None, right=None):
        self.key, self.left, self.right = key, left, right

def preorder(node, out):
    if node:
        out.append(node.key)
        preorder(node.left, out)
        preorder(node.right, out)
    return out

def inorder(node, out):
    if node:
        inorder(node.left, out)
        out.append(node.key)
        inorder(node.right, out)
    return out

def postorder(node, out):
    if node:
        postorder(node.left, out)
        postorder(node.right, out)
        out.append(node.key)
    return out

def level_order(root):
    out, queue = [], deque([root] if root else [])
    while queue:
        node = queue.popleft()
        out.append(node.key)
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    return out

root = Node("F",
            Node("B", Node("A"), Node("D", Node("C"), Node("E"))),
            Node("G", None, Node("I", Node("H"))))

print("pre:  ", " ".join(preorder(root, [])))
print("in:   ", " ".join(inorder(root, [])))
print("post: ", " ".join(postorder(root, [])))
print("level:", " ".join(level_order(root)))
```

Output:

```text
pre:   F B A D C E G I H
in:    A B C D E F G H I
post:  A C E D B H I G F
level: F B G A D I C E H
```

The three recursive functions are identical except for the position of the `append` line. The in-order result is alphabetical because this particular tree is a binary search tree: every key in a node's left subtree is smaller than the node and every key on the right is larger.

### Example 2: Iterative traversals with an explicit stack

```python
class Node:
    def __init__(self, key, left=None, right=None):
        self.key, self.left, self.right = key, left, right

def preorder_iterative(root):
    out, stack = [], [root] if root else []
    while stack:
        node = stack.pop()
        out.append(node.key)
        if node.right:
            stack.append(node.right)   # pushed first, so popped after the left subtree
        if node.left:
            stack.append(node.left)
    return out

def inorder_iterative(root):
    out, stack, node = [], [], root
    while stack or node:
        while node:                    # go as far left as possible
            stack.append(node)
            node = node.left
        node = stack.pop()
        out.append(node.key)
        node = node.right
    return out

def postorder_iterative(root):
    out, stack = [], [root] if root else []
    while stack:                       # visit node, right, left ...
        node = stack.pop()
        out.append(node.key)
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)
    return out[::-1]                   # ... and reverse to get left, right, node

root = Node("F",
            Node("B", Node("A"), Node("D", Node("C"), Node("E"))),
            Node("G", None, Node("I", Node("H"))))

print(" ".join(preorder_iterative(root)))
print(" ".join(inorder_iterative(root)))
print(" ".join(postorder_iterative(root)))

chain = None
for key in range(100_000):             # a degenerate tree 100,000 levels deep
    chain = Node(key, chain)
print(len(inorder_iterative(chain)))
```

Output:

```text
F B A D C E G I H
A B C D E F G H I
A C E D B H I G F
100000
```

The results match Example 1. The last test builds a degenerate tree whose height is 99,999. The recursive `inorder` from Example 1 would exceed CPython's default recursion limit of 1000 and raise `RecursionError`, while the iterative version handles it, because its stack is an ordinary list on the heap.

### Example 3: Choosing the order for the job

An expression tree stores operators in internal nodes and numbers in leaves. Evaluating a node requires the values of both children first, which is exactly post-order.

```python
import operator

OPS = {"+": operator.add, "-": operator.sub, "*": operator.mul}

class Node:
    def __init__(self, key, left=None, right=None):
        self.key, self.left, self.right = key, left, right

def evaluate(node):
    if node.left is None:              # leaves hold numbers
        return node.key
    left, right = evaluate(node.left), evaluate(node.right)   # children first: post-order
    return OPS[node.key](left, right)

def infix(node):                       # in-order, with parentheses to keep the structure
    if node.left is None:
        return str(node.key)
    return f"({infix(node.left)} {node.key} {infix(node.right)})"

def postfix(node):                     # post-order
    if node.left is None:
        return str(node.key)
    return f"{postfix(node.left)} {postfix(node.right)} {node.key}"

def height(node):                      # post-order: a node's height needs its children's
    if node is None:
        return -1
    return 1 + max(height(node.left), height(node.right))

tree = Node("*", Node("+", Node(3), Node(4)), Node("-", Node(5), Node(2)))
print(infix(tree))
print(postfix(tree))
print(evaluate(tree))
print(height(tree))
```

Output:

```text
((3 + 4) * (5 - 2))
3 4 + 5 2 - *
21
2
```

In-order produces the familiar infix form, but it needs parentheses: without them, the trees for `(3 + 4) * 2` and `3 + (4 * 2)` would print identically. Post-order produces postfix notation, which needs no parentheses and can be evaluated with a stack. The height function is post-order too, because a node's height is known only after both subtree heights are.

### Example 4: Level order, one level at a time

Many problems need to know where one level ends and the next begins. Processing the queue in batches of its current length gives exactly one level per batch.

```python
from collections import deque

class Node:
    def __init__(self, key, left=None, right=None):
        self.key, self.left, self.right = key, left, right

def levels(root):
    result, queue = [], deque([root] if root else [])
    while queue:
        level = []
        for _ in range(len(queue)):    # exactly the nodes currently queued: one level
            node = queue.popleft()
            level.append(node.key)
            for child in (node.left, node.right):
                if child:
                    queue.append(child)
        result.append(level)
    return result

root = Node("F",
            Node("B", Node("A"), Node("D", Node("C"), Node("E"))),
            Node("G", None, Node("I", Node("H"))))

by_level = levels(root)
print(by_level)
print("right side view:", [level[-1] for level in by_level])
print("maximum width:", max(len(level) for level in by_level))
```

Output:

```text
[['F'], ['B', 'G'], ['A', 'D', 'I'], ['C', 'E', 'H']]
right side view: ['F', 'G', 'I', 'H']
maximum width: 3
```

The "right side view" (the nodes you would see looking at the tree from the right) is the last node of each level. The same batching pattern finds the minimum depth of a leaf, connects nodes on the same level, or prints a tree level by level.

## Applications

- **File systems:** computing the total size of a directory is a post-order traversal (a folder's size is known only after its contents are summed), while printing an indented directory listing is pre-order.
- **Compilers and interpreters** evaluate and generate code for abstract syntax trees in post-order, and pretty-printers use in-order to show expressions in infix form.
- **Memory management:** in C and C++, a tree must be freed in post-order, so that no node is released while its children still need to be reached through it.
- **Serialisation:** a pre-order listing with markers for missing children records a tree in a form that can be rebuilt exactly, which is how trees are saved to files or sent over a network.
- **Search trees and heaps:** in-order traversal of a binary search tree yields its keys in sorted order, and a binary heap stores its nodes in level order in an array.

## Common mistakes

- **Missing the base case.** Every recursive traversal must handle an empty subtree (`None`); otherwise reading `node.left` on `None` raises an error.
- **Confusing depth with height,** or mixing conventions for the height of an empty tree. Pick one convention ($-1$ for empty, 0 for a single node) and use it consistently.
- **Pushing children in the wrong order** in iterative pre-order. A stack reverses order, so push the right child before the left.
- **Using `list.pop(0)` as a queue** for level order. Removing from the front of a list is $O(n)$; `collections.deque.popleft` is $O(1)$.
- **Trusting recursion on deep trees.** A degenerate tree can be as deep as it has nodes; use an explicit stack when the height may be large.
- **Assuming pre-order plus post-order determines a tree.** They do not when some node has a single child; in-order is needed together with one of them.

## Revision notes

- Pre-order: node, left, right. In-order: left, node, right. Post-order: left, right, node. Level order: by depth, using a queue.
- All traversals are $\Theta(n)$ time. Depth-first uses $O(h)$ space; level order uses $O(w)$ space.
- Height ranges from $\lfloor \log_2 n \rfloor$ (balanced) to $n - 1$ (degenerate). A perfect tree of height $h$ has $2^{h+1} - 1$ nodes.
- Iterative pre-order: pop, visit, push right then left. Iterative in-order: go left pushing, pop, visit, go right. Post-order: reverse a node-right-left pre-order.
- Post-order for anything that needs the children's results first (evaluation, height, size, freeing); pre-order for copying and serialising; in-order for sorted output from a BST.
- Pre-order plus in-order (distinct keys) determines a binary tree uniquely.

## Practice questions

:::question basic
A tree has root 1. Node 1's left child is 2 and its right child is 3. Node 2 has children 4 (left) and 5 (right). Node 3 has only a right child, 6. Write the pre-order, in-order, post-order, and level-order sequences.
:::answer
Pre-order: 1 2 4 5 3 6. In-order: 4 2 5 1 3 6. Post-order: 4 5 2 6 3 1. Level order: 1 2 3 4 5 6. For in-order, the left subtree of 1 gives 4 2 5, then 1, then the right subtree gives 3 6 (node 3 has no left child, so it comes before 6).
:::

:::question basic
A perfect binary tree has 15 nodes. What is its height, and how many leaves does it have?
:::answer
A perfect tree of height $h$ has $2^{h+1} - 1$ nodes, so $2^{h+1} - 1 = 15$ gives $h = 3$. It has $2^h = 8$ leaves, which is just over half of the nodes.
:::

:::question intermediate
You must free every node of a binary tree in C, where each node is reachable only through its parent's pointers. Which traversal order should you use, and why?
:::answer
Post-order. A node is freed only after both of its subtrees have been freed, so its `left` and `right` pointers are still valid while they are needed. Freeing a node first (pre-order) would leave the code reading pointers from memory that has already been released, which is undefined behaviour.
:::

:::question intermediate
A binary tree with distinct keys has pre-order `A B D E C F` and in-order `D B E A F C`. Reconstruct the tree and give its post-order.
:::answer
The first pre-order key, A, is the root. In the in-order sequence, `D B E` is left of A and `F C` is right of A. The next pre-order key, B, is the root of the left subtree; in-order `D B E` puts D on its left and E on its right. The remaining pre-order keys are `C F`, so C roots the right subtree, and in-order `F C` makes F the left child of C. The tree is A(B(D, E), C(F, -)), and its post-order is `D E B F C A`.
:::

:::question intermediate
Compare the extra memory used by recursive depth-first traversal and by level-order traversal on (a) a perfect tree with $n$ nodes and (b) a degenerate tree with $n$ nodes.
:::answer
(a) In a perfect tree, the height is about $\log_2 n$, so depth-first uses $O(\log n)$ stack space, but the last level holds $(n + 1)/2$ nodes, so the level-order queue needs $\Theta(n)$ space. (b) In a degenerate tree, the depth-first stack grows to $n$ frames, $\Theta(n)$, while each level has one node, so the queue never holds more than one node: $O(1)$. Neither strategy is better in every case.
:::

:::question advanced
Show that the pre-order and post-order sequences alone cannot always identify a binary tree.
:::answer
Take a root A with a single child B. If B is the left child, pre-order is `A B` and post-order is `B A`. If B is the right child, pre-order is still `A B` and post-order is still `B A`. The two trees are different but produce identical sequences. Their in-order sequences differ (`B A` versus `A B`), which is why in-order is needed. (If the tree is known to be full, every internal node has two children and pre-order plus post-order does determine it.)
:::

:::question advanced
Write a depth-first (not breadth-first) function that returns the number of nodes on each level of a binary tree. What is its time and space complexity?
:::answer
Pass the depth down the recursion and count nodes per depth:

```python
def level_counts(node, depth=0, counts=None):
    if counts is None:
        counts = []
    if node is not None:
        if depth == len(counts):
            counts.append(0)           # first node seen at this depth
        counts[depth] += 1
        level_counts(node.left, depth + 1, counts)
        level_counts(node.right, depth + 1, counts)
    return counts
```

Each node is visited once, so the time is $\Theta(n)$. The space is $O(h)$ for the recursion plus $O(h)$ for the list of counts, compared with $O(w)$ for the queue in a breadth-first version.
:::

## Further learning

- **Next:** *Binary Search Trees (BST)* adds an ordering rule that makes in-order traversal produce sorted output and allows fast search.
- **Related:** *Breadth-First Search & Depth-First Search* applies the same two strategies to general graphs, where cycles must also be handled.
- **Related:** *Stack ADT & Implementations* and *Circular Queues & Deque* describe the structures that drive depth-first and level-order traversal.
