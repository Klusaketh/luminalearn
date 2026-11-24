---
lesson: c-linked-data-structures
title: Linked Data Structures in C
summary: Building a singly linked list and a stack in C with malloc and free: node structures, insertion, traversal, deletion, and releasing every node without leaks.
minutes: 50
type: theory
objectives:
  - Define a self-referential node structure and allocate nodes on the heap
  - Implement insertion at the head and tail, traversal, search, and deletion for a singly linked list
  - Implement a stack on top of a linked list and free an entire structure without leaks or dangling pointers
review: ai-draft
---
## Introduction

Arrays store elements side by side, which makes indexing fast but inserting in the middle slow, because later elements must shift. A **linked list** stores each element in its own **node** that points to the next one, so nodes can live anywhere in memory and insertion only rewires pointers. Building one in C brings together structures, pointers, and heap allocation, and it is the basis of stacks, queues, hash-table buckets, and adjacency lists for graphs.

**Before you start:** you should know structures, pointers, pointers to pointers, and `malloc` / `free`.

## Core theory

### The node

```c
typedef struct Node {
    int value;
    struct Node *next;
} Node;
```

The structure contains a pointer to its own type, which is allowed because a pointer has a fixed size. The list itself is represented by a pointer to the first node, `head`; an empty list is `head == NULL`, and the last node's `next` is `NULL`.

### Core operations and their costs

| Operation | How | Cost |
| :--- | :--- | :--- |
| Insert at head | new node's `next` = head; head = new node | $O(1)$ |
| Insert at tail | walk to the last node (or keep a `tail` pointer) | $O(n)$, or $O(1)$ with `tail` |
| Search | follow `next` until found or `NULL` | $O(n)$ |
| Delete a value | find the node and its predecessor, relink, free | $O(n)$ |
| Access the $k$th item | walk $k$ links | $O(k)$ |

Functions that may change the head, such as inserting at the front or deleting the first node, must receive the head **by address** (`Node **head`) so they can update the caller's pointer. Using a pointer to the link being changed (`Node **link`) also removes the special case for deleting the first node, as Example 1 shows.

### Freeing a list

Every node was allocated separately, so every node must be freed. The loop must read `next` **before** freeing the current node, because the node's memory may not be used afterwards:

```c
while (head) { Node *next = head->next; free(head); head = next; }
```

### A stack on a linked list

A **stack** is last-in, first-out. With a linked list, `push` inserts at the head and `pop` removes from the head, both $O(1)$, and the stack can grow until memory runs out. `pop` on an empty stack must be handled, for example by returning a success flag.

## Worked examples

### Example 1: A singly linked list

```c
#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int value;
    struct Node *next;
} Node;

int push_front(Node **head, int value) {
    Node *n = malloc(sizeof *n);
    if (n == NULL) return 0;
    n->value = value;
    n->next = *head;
    *head = n;
    return 1;
}

int push_back(Node **head, int value) {
    Node **link = head;
    while (*link != NULL) link = &(*link)->next;
    return push_front(link, value);
}

int remove_value(Node **head, int value) {
    for (Node **link = head; *link != NULL; link = &(*link)->next) {
        if ((*link)->value == value) {
            Node *gone = *link;
            *link = gone->next;
            free(gone);
            return 1;
        }
    }
    return 0;
}

void print_list(const Node *n) {
    for (; n != NULL; n = n->next) printf("%d -> ", n->value);
    printf("NULL\n");
}

void free_list(Node **head) {
    while (*head != NULL) {
        Node *next = (*head)->next;
        free(*head);
        *head = next;
    }
}

int main(void) {
    Node *head = NULL;
    push_back(&head, 20);
    push_front(&head, 10);
    push_back(&head, 30);
    print_list(head);
    remove_value(&head, 10);
    remove_value(&head, 30);
    print_list(head);
    printf("remove 99: %d\n", remove_value(&head, 99));
    free_list(&head);
    print_list(head);
    return 0;
}
```

Output:

```text
10 -> 20 -> 30 -> NULL
20 -> NULL
remove 99: 0
NULL
```

`link` always points at the pointer that leads to the current node: first `head` itself, then some node's `next` field. Changing `*link` therefore works the same for the first node and every other node. `push_back` reuses `push_front` on the final `NULL` link.

### Example 2: A stack with push, pop, and peek

```c
#include <stdio.h>
#include <stdlib.h>

typedef struct Item { char ch; struct Item *below; } Item;

int push(Item **top, char ch) {
    Item *it = malloc(sizeof *it);
    if (!it) return 0;
    it->ch = ch;
    it->below = *top;
    *top = it;
    return 1;
}

int pop(Item **top, char *out) {
    if (*top == NULL) return 0;
    Item *it = *top;
    *out = it->ch;
    *top = it->below;
    free(it);
    return 1;
}

int balanced(const char *s) {
    Item *stack = NULL;
    char open;
    int ok = 1;
    for (; *s && ok; s++) {
        if (*s == '(' || *s == '[') ok = push(&stack, *s);
        else if (*s == ')') ok = pop(&stack, &open) && open == '(';
        else if (*s == ']') ok = pop(&stack, &open) && open == '[';
    }
    ok = ok && stack == NULL;
    while (pop(&stack, &open)) { }
    return ok;
}

int main(void) {
    const char *tests[] = {"([]())", "([)]", "((", "a[b(c)]d"};
    for (int i = 0; i < 4; i++) printf("%-8s %s\n", tests[i], balanced(tests[i]) ? "balanced" : "not balanced");
    return 0;
}
```

Output:

```text
([]())   balanced
([)]     not balanced
((       not balanced
a[b(c)]d balanced
```

Each opening bracket is pushed; each closing bracket must match the most recent unmatched opener, which is exactly what `pop` returns. The final loop frees any nodes left on the stack, so even unbalanced inputs leak nothing.

## Applications

- **Undo history and call stacks:** stacks built from linked nodes.
- **Hash tables:** each bucket is a linked list of entries with the same hash.
- **Graphs:** adjacency lists store each vertex's neighbours as a list.
- **Operating systems:** process queues and free-memory lists are linked structures.

## Common mistakes

- **Losing the rest of the list.** Set the new node's `next` before changing `head`.
- **Using a node after freeing it.** Save `next` first, then free.
- **Passing `Node *head` to a function that changes the head.** The caller's pointer does not change; pass `Node **`.
- **Forgetting to free the whole list.** Every `malloc` needs a matching `free`.

## Revision notes

- Node: value plus pointer to the next node; empty list is `NULL`.
- Head insertion and removal are $O(1)$; search and access by position are $O(n)$.
- Functions that may change the head take `Node **`.
- A pointer-to-link (`Node **link`) removes the special case for the first node.
- Free a list by saving `next` before each `free`.
- A linked stack pushes and pops at the head.

## Practice questions

:::question basic
What value marks the end of a singly linked list, and how is an empty list represented?
:::answer
The last node's `next` pointer is `NULL`. An empty list is a head pointer that is itself `NULL`, meaning there is no first node.
:::

:::question basic
Why is inserting at the head of a linked list $O(1)$ while inserting at the front of an array is $O(n)$?
:::answer
Head insertion only allocates a node and updates two pointers, regardless of the list's length. Inserting at the front of an array must shift every existing element one place to the right, which takes time proportional to the number of elements.
:::

:::question intermediate
What is wrong with this loop: `for (Node *p = head; p != NULL; p = p->next) free(p);`?
:::answer
After `free(p)`, the update expression reads `p->next` from memory that has already been freed, which is a use-after-free. Save the next pointer first: `while (p) { Node *next = p->next; free(p); p = next; }`.
:::

:::question intermediate
Why does `void push_front(Node *head, int v)` fail to add a node visible to the caller?
:::answer
`head` is a copy of the caller's pointer. The function can make the copy point to the new node, but the caller's variable still points to the old first node, so the new node is unreachable and leaks. The function needs `Node **head` so it can update the caller's pointer.
:::

:::question advanced
Write the steps to reverse a singly linked list in place in $O(n)$ time and $O(1)$ extra space.
:::answer
Keep three pointers: `prev = NULL`, `cur = head`, and `next`. While `cur` is not `NULL`: save `next = cur->next`, point `cur->next = prev`, then move forward with `prev = cur` and `cur = next`. When the loop ends, `prev` is the new head. Each node is visited once and only three pointers are used.
:::

## Further learning

- **Next:** *Binary & Text File Streams* shows how to save the data held in such structures.
- **Related:** *Singly and Doubly Linked Lists* in Data Structures & Algorithms compares list variants and their costs.
