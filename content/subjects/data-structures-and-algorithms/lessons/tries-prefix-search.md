---
lesson: tries-prefix-search
title: Tries and Prefix Search
summary: Store strings character by character in a tree so that lookups, prefix tests, autocomplete, and longest-prefix matching take time proportional to the key length.
minutes: 45
type: theory
objectives:
  - Describe how a trie spells out keys along root-to-node paths and why it needs end-of-word markers
  - Implement insertion, exact search, prefix testing, and prefix enumeration, and analyse each in terms of key length
  - Compare tries with hash tables and balanced search trees for string keys, including their memory cost
  - Apply tries and compressed tries to autocomplete and longest-prefix matching
---

## Introduction

Type "algo" into a search box and suggestions such as "algorithm" and "algorithms" appear at once. Producing them over millions of candidate phrases is a **prefix query**: find every stored string that begins with a given prefix. Hash tables cannot answer it, because hashing scatters "algorithm" and "algorithms" to unrelated slots. Balanced search trees can, but every step compares whole strings.

A **trie** (from re*trie*val, usually pronounced "try") is a tree built for exactly this. Each edge is labelled with a character, and each node stands for the prefix spelled by the path from the root to it. Strings that share a prefix share the nodes for that prefix. Finding a key of length $L$ takes $L$ steps, however many keys are stored, and all keys with a given prefix sit together in one subtree.

**Before you start:** you should know trees, tree traversals, and hash maps.

## Core theory

### Structure

- The **root** represents the empty string.
- Each node has at most one child per character. The child reached by character $c$ from the node for prefix $p$ represents $p + c$.
- Each node has an **end-of-word flag** that marks whether its prefix is itself a stored key. The flag is essential: if "card" is stored, the nodes for "c", "ca", "car", and "card" all exist, but "car" is a key only if its flag is set.

For example, storing car, card, care, cart, cat, do, and dog gives this trie, where `*` marks a node whose flag is set:

```text
(root)
 ├─ c ─ a ─ r* ─┬─ d*
 │      │       ├─ e*
 │      │       └─ t*
 │      └─ t*
 └─ d ─ o* ─ g*
```

The 23 characters of these seven keys need only 10 nodes below the root, because shared prefixes are stored once.

### Operations

| Operation | Method | Time |
| :--- | :--- | :--- |
| `insert(w)` | walk down, creating missing children; set the flag on the last node | $O(L)$ |
| `search(w)` | walk down; fail if a child is missing; succeed only if the final flag is set | $O(L)$ |
| `starts_with(p)` | walk down; succeed if every child exists | $O(L)$ |
| enumerate keys with prefix $p$ | walk to $p$'s node, then traverse its subtree | $O(L + S)$, where $S$ is the size of that subtree |
| `delete(w)` | clear the flag, then remove nodes that have no children and no flag, bottom-up | $O(L)$ |

Here $L$ is the length of the key or prefix, and these bounds assume finding a child takes constant time. The cost does not depend on the number of keys $n$, which is the main attraction. If the children are visited in alphabetical order, a pre-order traversal lists keys in **lexicographic order**, and a word always comes before its extensions.

### Representing the children

| Representation | Child lookup | Memory per node | Notes |
| :--- | :--- | :--- | :--- |
| Array indexed by character | $O(1)$ | one slot per possible character, used or not | fast; wasteful for large alphabets |
| Hash map | $O(1)$ expected | proportional to the number of children | flexible; works for Unicode |
| Sorted list or array | $O(\log \sigma)$ by binary search | compact | slower lookups |

($\sigma$ is the alphabet size.) With an array of 26 pointers per node, a trie for English words can use far more memory than the words themselves, because most slots are empty. Memory is the main weakness of tries.

### Compressed tries

Long chains of nodes with a single child waste space. A **compressed trie** (also called a radix tree or Patricia trie) merges each such chain into one edge labelled with a string. For "test", "team", and "toast", the plain trie has 10 nodes below the root, while the compressed trie has 5: edges "t", then "e" and "oast", then "st" and "am" below "e". Every internal node of a compressed trie has at least two children (or marks the end of a key), so the number of nodes is $O(n)$ for $n$ keys rather than $O(\text{total characters})$.

### Comparison with other structures

| | Hash table | Balanced BST | Trie |
| :--- | :--- | :--- | :--- |
| Exact lookup | $O(L)$ to hash, then $O(1)$ expected | $O(\log n)$ string comparisons, each up to $O(L)$ | $O(L)$ |
| Prefix query | not supported | $O(L \log n + \text{output})$ via a range search | $O(L + \text{output})$ |
| Sorted iteration | not supported | yes | yes, with ordered children |
| Memory | low | low | high unless compressed |

## Worked examples

### Example 1: A trie with search and prefix tests

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.nodes = 1

    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
                self.nodes += 1
            node = node.children[ch]
        node.is_word = True

    def _walk(self, prefix):
        node = self.root
        for ch in prefix:
            node = node.children.get(ch)
            if node is None:
                return None
        return node

    def search(self, word):
        node = self._walk(word)
        return node is not None and node.is_word

    def starts_with(self, prefix):
        return self._walk(prefix) is not None

words = ["car", "card", "care", "cart", "cat", "dog", "do"]
t = Trie()
for w in words:
    t.insert(w)

print(t.search("car"), t.search("ca"), t.search("cars"))
print(t.starts_with("ca"), t.starts_with("dox"))
print("nodes:", t.nodes, "characters:", sum(len(w) for w in words))
```

Output:

```text
True False False
True False
nodes: 11 characters: 23
```

`search("ca")` is `False` even though the path exists, because no stored key ends at that node; `starts_with("ca")` is `True` for the same reason that the path exists. `search("cars")` fails at the missing child `s`. The count of 11 includes the root.

### Example 2: Autocomplete in lexicographic order

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False

def insert(root, word):
    node = root
    for ch in word:
        node = node.children.setdefault(ch, TrieNode())
    node.is_word = True

def complete(root, prefix, limit=None):
    node = root
    for ch in prefix:                          # O(L): find the prefix's node
        node = node.children.get(ch)
        if node is None:
            return []
    results = []

    def collect(node, path):                   # pre-order, children in sorted order
        if limit is not None and len(results) >= limit:
            return
        if node.is_word:
            results.append(path)
        for ch in sorted(node.children):
            collect(node.children[ch], path + ch)

    collect(node, prefix)
    return results

root = TrieNode()
for w in ["car", "card", "care", "cart", "cat", "dog", "do", "carbon"]:
    insert(root, w)

print(complete(root, "car"))
print(complete(root, "c", limit=3))
print(complete(root, "do"))
print(complete(root, "x"))
```

Output:

```text
['car', 'carbon', 'card', 'care', 'cart']
['car', 'carbon', 'card']
['do', 'dog']
[]
```

Every completion of "car" lives in the subtree below the node for "car", so the search never looks at "cat" or "dog". Visiting children in sorted order gives alphabetical output, and pre-order puts "car" before "carbon". With a limit, the traversal stops early, which is what an autocomplete box needs. Real systems usually also store a popularity score with each key and return the highest-scoring completions instead of the first ones alphabetically.

### Example 3: Longest-prefix matching

Internet routers forward each packet using the **longest** stored prefix that matches its destination address. The same walk down a trie finds it: remember the last node with a route on the way down. This example uses 6-bit addresses written as strings; real IPv4 addresses have 32 bits.

```python
def build(routes):
    root = {}
    for prefix, hop in routes.items():
        node = root
        for bit in prefix:
            node = node.setdefault(bit, {})
        node["hop"] = hop
    return root

def lookup(root, address):
    best, node = root.get("hop"), root
    for bit in address:
        node = node.get(bit)
        if node is None:
            break
        best = node.get("hop", best)       # a longer matching prefix replaces the previous one
    return best

routes = {"": "default", "01": "A", "10": "B", "1011": "C"}
table = build(routes)
for address in ["101101", "100111", "011000", "110000", "001111"]:
    print(address, "->", lookup(table, address))
```

Output:

```text
101101 -> C
100111 -> B
011000 -> A
110000 -> default
001111 -> default
```

For 101101, both "10" and "1011" match, and the walk replaces B with C when it reaches the deeper node. For 110000, no stored prefix beyond the empty one matches, so the default route applies. The lookup costs one step per address bit, independent of the size of the routing table, which is why routers use compressed binary tries (and specialised hardware) for this task.

## Applications

- **Autocomplete and search suggestions**, where all completions of a prefix are in one subtree, often with scores stored at word nodes.
- **Spell checkers and word games:** checking whether a string is a word, and pruning a search as soon as a prefix cannot lead to any word (for example, in a Boggle solver).
- **IP routing:** longest-prefix matching over routing tables, typically with compressed binary tries.
- **Multi-pattern string search:** the Aho-Corasick algorithm adds failure links to a trie of patterns to find all of them in a text in one pass.
- **Bioinformatics and text indexing:** suffix tries and suffix trees, which are compressed tries of all suffixes of a text, support fast substring queries.

## Common mistakes

- **Omitting the end-of-word flag,** so that every prefix of a stored word is wrongly reported as a word.
- **Deleting nodes that other keys still use.** After clearing a flag, remove a node only if it has no children and no flag of its own, working upwards.
- **Using a fixed 26-slot array for general text,** which fails for uppercase letters, digits, and Unicode, and wastes memory when nodes have few children.
- **Assuming a trie always saves memory.** Each node carries a container and a flag; for a small set of unrelated words, a hash set is far smaller.
- **Calling prefix enumeration $O(L)$.** Reaching the prefix is $O(L)$, but listing the results costs time proportional to the subtree explored.

## Revision notes

- A trie node represents a prefix; children are indexed by the next character; a flag marks complete keys.
- Insert, search, prefix test, and delete are $O(L)$, independent of the number of keys.
- Prefix enumeration: walk to the prefix node, then traverse its subtree; sorted children give lexicographic order.
- Children as arrays (fast, memory-hungry), hash maps (flexible), or sorted lists (compact).
- Compressed tries merge single-child chains into string-labelled edges, giving $O(n)$ nodes.
- Use cases: autocomplete, spell checking, longest-prefix matching, Aho-Corasick.

## Practice questions

:::question basic
Insert "tea", "ten", "to", and "inn" into an empty trie. How many nodes does it have, including the root?
:::answer
Nine. "tea" adds t, e, a (three nodes); "ten" adds only n below "te"; "to" adds only o below "t"; "inn" adds i, n, n. That is $3 + 1 + 1 + 3 = 8$ nodes plus the root.
:::

:::question basic
A trie stores "card" but not "car". Why must `search("car")` return `False`, and what in the trie makes that possible?
:::answer
The nodes for c, a, and r exist because they lie on the path to "card", so the path alone cannot tell whether "car" was inserted. The end-of-word flag on the "car" node is unset, which records that no key ends there. `search` returns `True` only when the path exists and the final node's flag is set.
:::

:::question intermediate
Compare the cost of looking up a string of length $L$ in a trie and in a balanced BST holding $n$ strings.
:::answer
The trie follows one edge per character, so the lookup is $O(L)$ regardless of $n$ (assuming constant-time child lookup). The BST makes $O(\log n)$ comparisons, and each string comparison can examine up to $L$ characters, so the lookup is $O(L \log n)$ in the worst case. In practice, comparisons often stop early at the first differing character, but keys with long shared prefixes make the BST's comparisons expensive.
:::

:::question intermediate
A trie stores "car", "card", and "care". Describe exactly which nodes are removed when "card" is deleted.
:::answer
Walk to the node for "card" and clear its flag. That node now has no children and no flag, so remove it from its parent, the node for "car". Then check the "car" node: it has its own flag set (and still has the child e), so it must stay, and the deletion stops. Only the single node for the final d is removed.
:::

:::question intermediate
Why can a trie with a 26-element array in every node use much more memory than storing the words in a hash set?
:::answer
Every node allocates 26 child slots whether or not they are used. Near the leaves, most nodes have zero or one child, so almost all slots are empty pointers: about 26 pointers per node, with one node per distinct prefix. A hash set stores each word once plus modest table overhead. Tries save memory only when many keys share long prefixes; otherwise, hash-map children or a compressed trie are better choices.
:::

:::question advanced
Build the compressed trie (radix tree) for "test", "team", and "toast". How many nodes does it have compared with the uncompressed trie?
:::answer
From the root, a single edge "t" leads to a node with two children: edge "e" and edge "oast" (which ends at the key "toast"). Below the "e" node, edges "st" and "am" end at "test" and "team". Counting the root, the compressed trie has 6 nodes (root, t, te, test, team, toast). The uncompressed trie has 11: the root plus t, e, s, t for "test", a, m for "team", and o, a, s, t for "toast".
:::

:::question advanced
Design an autocomplete service that returns the three most popular completions of a prefix quickly. What do you store, and what is the trade-off?
:::answer
Store each phrase's popularity count at its word node. A simple design walks to the prefix node and searches its whole subtree for the top three, keeping them in a small heap; that is $O(L + S \log 3)$, where $S$ is the subtree size, which is slow for short prefixes like "a". A faster design stores, at every node, a precomputed list of the top three completions in its subtree. Then a query is $O(L)$: walk to the prefix node and read its list. The cost is extra memory at every node and more work on updates, because changing one phrase's count may change the lists of all nodes on its path, $O(L)$ nodes.
:::

## Further learning

- **Next:** *Min & Max Heap Implementation* builds the array-based binary heap behind priority queues.
- **Related:** *Pattern Matching Basics* covers single-pattern search; the Aho-Corasick algorithm generalises it to many patterns using a trie.
- **Related:** *Hash Functions & Collision Handling* is the usual alternative when only exact lookups are needed.
