"""
LuminaLearn AI — Sprint 6.2B Academic Content Seeding System.
Populates normalized, scalable academic content hierarchy:
Category -> Subject -> Course -> Module -> Topic -> Lesson.

Idempotent: Can be executed multiple times without duplicating or overwriting records.
Compatible with SQLite (dev fallback) and PostgreSQL (production).
"""
import asyncio
from datetime import datetime, timezone
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, init_db
from app.models.content import (
    ContentCategory,
    Course,
    Lesson,
    Module,
    Subject,
    Topic,
)

# ------------------------------------------------------------------------------
# 1. CATALOG DEFINITION DATA
# ------------------------------------------------------------------------------

CATEGORIES_DATA = [
    {
        "name": "Computer Science",
        "slug": "computer-science",
        "description": "Foundational computing systems, algorithm analysis, computer architecture, and distributed systems.",
        "display_order": 1,
    },
    {
        "name": "Programming",
        "slug": "programming",
        "description": "Core software engineering paradigms, procedural, object-oriented, and modern scripting languages.",
        "display_order": 2,
    },
    {
        "name": "Artificial Intelligence",
        "slug": "artificial-intelligence",
        "description": "Intelligent agents, machine learning algorithms, deep neural representations, and computer vision.",
        "display_order": 3,
    },
    {
        "name": "Mathematics",
        "slug": "mathematics",
        "description": "Formal mathematical foundations for computer science, discrete structures, probability, and linear algebra.",
        "display_order": 4,
    },
]

# 22 Canonical Subjects with course, module, and topic hierarchies
SUBJECTS_CATALOG = [
    # --- Computer Science ---
    {
        "category_slug": "computer-science",
        "name": "Data Structures & Algorithms",
        "slug": "data-structures-and-algorithms",
        "short_description": "Master algorithmic complexity, memory representation, and classic data structures.",
        "description": "Comprehensive curriculum covering algorithmic complexity analysis, linear structures, trees, graphs, dynamic programming, and optimization techniques.",
        "icon_key": "code-2",
        "difficulty_level": "Intermediate",
        "display_order": 1,
        "courses": [
            {
                "title": "Data Structures & Algorithms Core",
                "slug": "dsa-core",
                "description": "In-depth study of memory layout, algorithmic analysis, and problem-solving strategies.",
                "difficulty": "Intermediate",
                "estimated_hours": 45,
                "modules": [
                    {
                        "title": "Complexity Analysis",
                        "slug": "dsa-complexity-analysis",
                        "description": "Asymptotic bounds, time-space trade-offs, and recurrence relations.",
                        "estimated_minutes": 120,
                        "topics": [
                            {"title": "Big-O, Big-Omega & Theta Notations", "slug": "asymptotic-notations", "summary": "Mathematical definitions of asymptotic upper, lower, and tight bounds.", "difficulty": "Beginner", "estimated_minutes": 40},
                            {"title": "Space Complexity & Memory Trade-offs", "slug": "space-complexity-tradeoffs", "summary": "Evaluating auxiliary memory allocations versus computational runtime.", "difficulty": "Beginner", "estimated_minutes": 35},
                            {"title": "Amortized Analysis", "slug": "amortized-analysis", "summary": "Analyzing average time per operation across a worst-case sequence.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Arrays",
                        "slug": "dsa-arrays",
                        "description": "Contiguous memory structures, multi-dimensional addressing, and linear scanning.",
                        "estimated_minutes": 150,
                        "topics": [
                            {"title": "Static vs Dynamic Arrays", "slug": "static-vs-dynamic-arrays", "summary": "Contiguous storage, resizing amortized cost, and index arithmetic.", "difficulty": "Beginner", "estimated_minutes": 45},
                            {"title": "Sliding Window & Two-Pointers", "slug": "sliding-window-two-pointers", "summary": "Subarray scanning techniques for linear algorithmic optimizations.", "difficulty": "Intermediate", "estimated_minutes": 55},
                        ]
                    },
                    {
                        "title": "Strings",
                        "slug": "dsa-strings",
                        "description": "Character encoding, immutable buffer operations, and substring indexing.",
                        "estimated_minutes": 100,
                        "topics": [
                            {"title": "String Manipulation & Encodings", "slug": "string-manipulation-encodings", "summary": "ASCII, UTF-8 buffer layouts and in-place transformations.", "difficulty": "Beginner", "estimated_minutes": 45},
                            {"title": "Pattern Matching Basics", "slug": "pattern-matching-basics", "summary": "Naive and KMP prefix functions for string search.", "difficulty": "Intermediate", "estimated_minutes": 55},
                        ]
                    },
                    {
                        "title": "Linked Lists",
                        "slug": "dsa-linked-lists",
                        "description": "Node pointer structures, dynamic allocation, and non-contiguous collections.",
                        "estimated_minutes": 140,
                        "topics": [
                            {"title": "Singly & Doubly Linked Lists", "slug": "singly-doubly-linked-lists", "summary": "Pointer manipulation, head/tail sentinels, and node insertion/deletion.", "difficulty": "Beginner", "estimated_minutes": 45},
                            {"title": "Fast & Slow Pointer Techniques", "slug": "fast-slow-pointers", "summary": "Cycle detection (Floyd's algorithm) and middle node retrieval.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Stacks",
                        "slug": "dsa-stacks",
                        "description": "LIFO abstract data type, call stack simulation, and parenthetical parsing.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Stack ADT & Implementations", "slug": "stack-adt-implementations", "summary": "Array-backed vs node-backed LIFO containers.", "difficulty": "Beginner", "estimated_minutes": 45},
                            {"title": "Monotonic Stacks & Parentheses", "slug": "monotonic-stacks", "summary": "Monotonic stacks for next-greater element and expression evaluation.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Queues",
                        "slug": "dsa-queues",
                        "description": "FIFO sequencing, ring buffers, and deque implementations.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Circular Queues & Deque", "slug": "circular-queues-deque", "summary": "Modulo index pointer wrapping and double-ended queues.", "difficulty": "Beginner", "estimated_minutes": 45},
                            {"title": "Priority Queues Overview", "slug": "priority-queues-overview", "summary": "Ordered retrieval using heap structures.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Hashing",
                        "slug": "dsa-hashing",
                        "description": "Direct addressing, hash collision resolution, and hash table sizing.",
                        "estimated_minutes": 110,
                        "topics": [
                            {"title": "Hash Functions & Collision Handling", "slug": "hash-functions-collisions", "summary": "Separate chaining, open addressing, and load factor thresholding.", "difficulty": "Intermediate", "estimated_minutes": 55},
                        ]
                    },
                    {
                        "title": "Trees",
                        "slug": "dsa-trees",
                        "description": "Hierarchical structures, tree traversals, and balance guarantees.",
                        "estimated_minutes": 180,
                        "topics": [
                            {"title": "Binary Tree Traversals", "slug": "binary-tree-traversals", "summary": "Pre-order, In-order, Post-order, and Level-order BFS visits.", "difficulty": "Intermediate", "estimated_minutes": 60},
                            {"title": "Binary Search Trees (BST)", "slug": "binary-search-trees", "summary": "Ordering invariants, logarithmic lookups, and deletions.", "difficulty": "Intermediate", "estimated_minutes": 60},
                        ]
                    },
                    {
                        "title": "Heaps",
                        "slug": "dsa-heaps",
                        "description": "Complete binary trees with heap properties for priority management.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Min & Max Heap Implementation", "slug": "heap-implementation", "summary": "Array-backed complete trees, sift-up, and sift-down operations.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Graphs",
                        "slug": "dsa-graphs",
                        "description": "Vertices, edges, traversal algorithms, and shortest paths.",
                        "estimated_minutes": 200,
                        "topics": [
                            {"title": "Graph Representations", "slug": "graph-representations", "summary": "Adjacency matrix vs adjacency list space-time comparison.", "difficulty": "Intermediate", "estimated_minutes": 45},
                            {"title": "Breadth-First Search & Depth-First Search", "slug": "bfs-dfs-traversals", "summary": "Queue-driven BFS and recursive DFS cycle detection.", "difficulty": "Intermediate", "estimated_minutes": 60},
                        ]
                    },
                    {
                        "title": "Searching",
                        "slug": "dsa-searching",
                        "description": "Sequential scanning and binary partitioning search strategies.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Binary Search & Invariants", "slug": "binary-search-invariants", "summary": "Half-interval elimination on monotonic domains.", "difficulty": "Beginner", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Sorting",
                        "slug": "dsa-sorting",
                        "description": "Quadratic, logarithmic, and linear time sorting algorithms.",
                        "estimated_minutes": 120,
                        "topics": [
                            {"title": "Merge Sort & QuickSort", "slug": "mergesort-quicksort", "summary": "Divide-and-conquer partitioning, pivot selection, and stability.", "difficulty": "Intermediate", "estimated_minutes": 60},
                        ]
                    },
                    {
                        "title": "Recursion",
                        "slug": "dsa-recursion",
                        "description": "Self-referential functions, base cases, and activation call frames.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Call Stack & Recurrence Trees", "slug": "call-stack-recurrence-trees", "summary": "Stack frame unwinding and Master Theorem analysis.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Greedy Algorithms",
                        "slug": "dsa-greedy",
                        "description": "Local optimal choice heuristics and correctness proofs.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Greedy Choice & Optimal Substructure", "slug": "greedy-choice-property", "summary": "Interval scheduling and fractional knapsack problem solving.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Dynamic Programming",
                        "slug": "dsa-dynamic-programming",
                        "description": "Optimal substructure, overlapping subproblems, memoization, and tabulation.",
                        "estimated_minutes": 180,
                        "topics": [
                            {"title": "Memoization vs Tabulation", "slug": "memoization-vs-tabulation", "summary": "Top-down recursive caching vs bottom-up iterative DP table construction.", "difficulty": "Advanced", "estimated_minutes": 60},
                            {"title": "0/1 Knapsack Problem", "slug": "knapsack-01-problem", "summary": "State transition equation and 2D DP matrix space optimization.", "difficulty": "Advanced", "estimated_minutes": 60},
                        ]
                    },
                ]
            }
        ]
    },
    {
        "category_slug": "computer-science",
        "name": "Operating Systems",
        "slug": "operating-systems",
        "short_description": "Kernels, concurrency, CPU scheduling, virtual memory, and hardware interaction.",
        "description": "Core principles of operating system architecture, process management, multi-threading, concurrency synchronization, virtual memory paging, and storage file systems.",
        "icon_key": "cpu",
        "difficulty_level": "Intermediate",
        "display_order": 2,
        "courses": [
            {
                "title": "Operating Systems Fundamentals",
                "slug": "operating-systems-fundamentals",
                "description": "System architecture, hardware abstraction, concurrency synchronization, and memory hierarchies.",
                "difficulty": "Intermediate",
                "estimated_hours": 40,
                "modules": [
                    {
                        "title": "Introduction",
                        "slug": "os-introduction",
                        "description": "Role of the OS, dual-mode operation, system calls, and kernel architectures.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "OS Roles & Kernel Architectures", "slug": "os-roles-kernel-architectures", "summary": "Monolithic, microkernel, and hybrid kernel designs.", "difficulty": "Beginner", "estimated_minutes": 30},
                            {"title": "System Calls & Dual-Mode Execution", "slug": "system-calls-dual-mode", "summary": "User mode vs kernel mode transitions and trap handling.", "difficulty": "Beginner", "estimated_minutes": 30},
                        ]
                    },
                    {
                        "title": "Processes & Threads",
                        "slug": "os-processes-and-threads",
                        "description": "Process state transitions, PCB descriptors, threads, and context switching.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Process Control Block & Lifecycle", "slug": "process-control-block-lifecycle", "summary": "New, Ready, Running, Waiting, Terminated states and PCB contents.", "difficulty": "Beginner", "estimated_minutes": 45},
                            {"title": "Kernel vs User Threads", "slug": "kernel-vs-user-threads", "summary": "Thread control blocks, POSIX pthreads, and 1:1 vs M:N thread models.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "CPU Scheduling",
                        "slug": "os-cpu-scheduling",
                        "description": "Dispatchers, preemptive algorithms, turnaround and response time metrics.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Scheduling Criteria & Dispatcher", "slug": "scheduling-criteria-dispatcher", "summary": "Throughput, turnaround, waiting, and response times.", "difficulty": "Beginner", "estimated_minutes": 40},
                            {"title": "Preemptive Scheduling Algorithms", "slug": "preemptive-scheduling-algorithms", "summary": "Round Robin, Shortest Remaining Time First (SRTF), and Priority scheduling.", "difficulty": "Intermediate", "estimated_minutes": 50},
                        ]
                    },
                    {
                        "title": "Synchronization",
                        "slug": "os-synchronization",
                        "description": "Race conditions, critical sections, Peterson's algorithm, mutexes, and semaphores.",
                        "estimated_minutes": 100,
                        "topics": [
                            {"title": "Critical Section Problem & Mutexes", "slug": "critical-section-problem", "summary": "Mutual exclusion, progress, and bounded waiting requirements.", "difficulty": "Intermediate", "estimated_minutes": 50},
                            {"title": "Semaphores & Condition Variables", "slug": "semaphores-condition-variables", "summary": "Counting and binary semaphores, classic dining philosophers problem.", "difficulty": "Intermediate", "estimated_minutes": 50},
                        ]
                    },
                    {
                        "title": "Deadlocks",
                        "slug": "os-deadlocks",
                        "description": "Four necessary conditions, resource allocation graphs, Banker's algorithm.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Deadlock Characterization & Prevention", "slug": "deadlock-characterization", "summary": "Mutual exclusion, hold and wait, no preemption, circular wait.", "difficulty": "Intermediate", "estimated_minutes": 40},
                            {"title": "Banker's Algorithm & Avoidance", "slug": "bankers-algorithm", "summary": "Safe state verification and resource request algorithm.", "difficulty": "Intermediate", "estimated_minutes": 40},
                        ]
                    },
                    {
                        "title": "Memory Management",
                        "slug": "os-memory-management",
                        "description": "Base/limit registers, logical to physical translation, internal/external fragmentation.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Address Binding & Dynamic Relocation", "slug": "address-binding-relocation", "summary": "Compile time, load time, and execution time address mapping.", "difficulty": "Intermediate", "estimated_minutes": 45},
                            {"title": "Paging & Page Tables", "slug": "paging-page-tables", "summary": "Frames, pages, TLB (Translation Lookaside Buffer) hit rates.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Virtual Memory",
                        "slug": "os-virtual-memory",
                        "description": "Demand paging, page faults, replacement algorithms (FIFO, LRU, Optimal).",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Demand Paging & Page Fault Handling", "slug": "demand-paging-page-faults", "summary": "Hardware page fault interrupt service routines and disk swap space.", "difficulty": "Intermediate", "estimated_minutes": 45},
                            {"title": "Page Replacement Algorithms", "slug": "page-replacement-algorithms", "summary": "FIFO, Least Recently Used (LRU), and Second Chance algorithms.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "File Systems",
                        "slug": "os-file-systems",
                        "description": "Inodes, directory structures, contiguous, linked, and indexed disk allocations.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "File System Structure & Inodes", "slug": "file-system-structure-inodes", "summary": "Metadata storage, inode pointer structures, and open file tables.", "difficulty": "Intermediate", "estimated_minutes": 40},
                        ]
                    },
                    {
                        "title": "I/O Systems",
                        "slug": "os-io-systems",
                        "description": "Device controllers, polling vs interrupts, DMA channels, and disk scheduling.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Direct Memory Access (DMA) & Interrupts", "slug": "dma-and-interrupts", "summary": "Offloading CPU cycle load via hardware DMA controllers.", "difficulty": "Intermediate", "estimated_minutes": 35},
                        ]
                    },
                ]
            }
        ]
    },
    {
        "category_slug": "computer-science",
        "name": "Database Management Systems",
        "slug": "database-management-systems",
        "short_description": "Relational algebra, SQL, normalization, transactions, concurrency, and indexing.",
        "description": "Comprehensive study of relational database models, entity-relationship modeling, formal relational algebra, SQL DDL/DML, normalization forms, transaction ACID properties, and B+ tree storage indexing.",
        "icon_key": "database",
        "difficulty_level": "Intermediate",
        "display_order": 3,
        "courses": [
            {
                "title": "Database Management Systems Fundamentals",
                "slug": "dbms-fundamentals",
                "description": "Foundations of relational database design, query optimization, ACID transactions, and index structures.",
                "difficulty": "Intermediate",
                "estimated_hours": 38,
                "modules": [
                    {
                        "title": "Database Fundamentals",
                        "slug": "dbms-fundamentals-module",
                        "description": "File systems limitations, data abstraction levels, and ANSI/SPARC 3-tier architecture.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "File Systems vs DBMS", "slug": "file-systems-vs-dbms", "summary": "Data redundancy, inconsistency, and declarative querying advantages.", "difficulty": "Beginner", "estimated_minutes": 30},
                            {"title": "3-Schema Architecture", "slug": "three-schema-architecture", "summary": "Physical, logical, and external schema separation for data independence.", "difficulty": "Beginner", "estimated_minutes": 30},
                        ]
                    },
                    {
                        "title": "Relational Model",
                        "slug": "dbms-relational-model",
                        "description": "Mathematical relations, tuples, domain constraints, and relational algebra.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Relational Model & Tuple Algebra", "slug": "relational-model-tuple-algebra", "summary": "Relations as tables, attribute domains, and selection/projection operators.", "difficulty": "Beginner", "estimated_minutes": 40},
                        ]
                    },
                    {
                        "title": "ER Model",
                        "slug": "dbms-er-model",
                        "description": "Entity-Relationship modeling, cardinalities, weak entity sets, and ER-to-relational mapping.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Entity Sets & Cardinality Ratios", "slug": "entity-sets-cardinalities", "summary": "1:1, 1:N, M:N relationship constraints and Crow's foot notation.", "difficulty": "Beginner", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Keys & Constraints",
                        "slug": "dbms-keys-and-constraints",
                        "description": "Candidate keys, primary keys, foreign keys, and referential integrity constraints.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "Key Types & Integrity Constraints", "slug": "key-types-and-constraints", "summary": "Superkeys, minimal keys, cascading foreign key delete/update actions.", "difficulty": "Beginner", "estimated_minutes": 40},
                        ]
                    },
                    {
                        "title": "SQL",
                        "slug": "dbms-sql",
                        "description": "Structured Query Language, DDL, DML, aggregate expressions, and subqueries.",
                        "estimated_minutes": 120,
                        "topics": [
                            {"title": "Declarative SQL Queries & Filtering", "slug": "declarative-sql-queries", "summary": "SELECT, WHERE, GROUP BY, HAVING, and aggregate functions.", "difficulty": "Beginner", "estimated_minutes": 60},
                        ]
                    },
                    {
                        "title": "Joins",
                        "slug": "dbms-joins",
                        "description": "Relational join algorithms, inner joins, outer joins, and cartesian products.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Inner, Outer & Self Joins", "slug": "inner-outer-self-joins", "summary": "Equi-joins, left/right outer joins, and nested loop execution.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Normalization",
                        "slug": "dbms-normalization",
                        "description": "Functional dependencies, Armstrong's axioms, 1NF, 2NF, 3NF, and BCNF decomposition.",
                        "estimated_minutes": 120,
                        "topics": [
                            {"title": "Functional Dependencies & Normal Forms", "slug": "functional-dependencies-normal-forms", "summary": "Lossless-join decomposition, dependency preservation, and 3NF vs BCNF.", "difficulty": "Intermediate", "estimated_minutes": 60},
                        ]
                    },
                    {
                        "title": "Transactions",
                        "slug": "dbms-transactions",
                        "description": "Transaction states, ACID guarantees, and serializability.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "ACID Properties & Transaction States", "slug": "acid-properties-transaction-states", "summary": "Atomicity, Consistency, Isolation, and Durability enforcement.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Concurrency Control",
                        "slug": "dbms-concurrency-control",
                        "description": "Locking protocols, 2-Phase Locking (2PL), deadlock prevention, and timestamp ordering.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Two-Phase Locking (2PL) & Conflicts", "slug": "two-phase-locking-protocol", "summary": "Growing and shrinking phases, cascading rollbacks, strict 2PL.", "difficulty": "Advanced", "estimated_minutes": 50},
                        ]
                    },
                    {
                        "title": "Indexing",
                        "slug": "dbms-indexing",
                        "description": "Primary and secondary indexes, dense vs sparse indexes, B+ Trees.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "B+ Tree Index Structures", "slug": "b-plus-tree-indexes", "summary": "Balanced node splitting, leaf pointer chains, and logarithmic search cost.", "difficulty": "Advanced", "estimated_minutes": 50},
                        ]
                    },
                    {
                        "title": "Recovery",
                        "slug": "dbms-recovery",
                        "description": "Write-Ahead Logging (WAL), undo/redo logging, checkpoints, and ARIES recovery.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "Write-Ahead Logging & Checkpoints", "slug": "wal-and-checkpoint-recovery", "summary": "Crash recovery algorithms and idempotent log processing.", "difficulty": "Advanced", "estimated_minutes": 45},
                        ]
                    },
                ]
            }
        ]
    },
    {
        "category_slug": "computer-science",
        "name": "Computer Networks",
        "slug": "computer-networks",
        "short_description": "OSI and TCP/IP protocol stacks, IP routing, transport guarantees, and application protocols.",
        "description": "Comprehensive network architecture course spanning physical signaling, data link framing, IPv4/IPv6 subnetting, routing protocols (OSPF, BGP), reliable transport (TCP/UDP), and DNS/HTTP application layers.",
        "icon_key": "network",
        "difficulty_level": "Intermediate",
        "display_order": 4,
        "courses": [
            {
                "title": "Computer Networks Fundamentals",
                "slug": "computer-networks-fundamentals",
                "description": "Layered network protocols, reliable packet delivery, IP routing, and sockets.",
                "difficulty": "Intermediate",
                "estimated_hours": 35,
                "modules": [
                    {
                        "title": "Network Models",
                        "slug": "cn-network-models",
                        "description": "OSI 7-layer model vs TCP/IP 4-layer model, encapsulation, and packet headers.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "OSI vs TCP/IP Protocol Stacks", "slug": "osi-vs-tcp-ip-models", "summary": "Protocol layering, encapsulation, and header multiplexing.", "difficulty": "Beginner", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Physical Layer",
                        "slug": "cn-physical-layer",
                        "description": "Bandwidth, Nyquist/Shannon capacity theorems, transmission media.",
                        "estimated_minutes": 50,
                        "topics": [
                            {"title": "Channel Capacity & Transmission Media", "slug": "channel-capacity-transmission", "summary": "Signal attenuation, SNR, and Shannon limit bounds.", "difficulty": "Beginner", "estimated_minutes": 30},
                        ]
                    },
                    {
                        "title": "Data Link Layer",
                        "slug": "cn-data-link-layer",
                        "description": "Framing, error detection (CRC), flow control, and CSMA/CD Ethernet.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "Framing, CRC & CSMA/CD Protocol", "slug": "framing-crc-csma-cd", "summary": "Bit stuffing, cyclic redundancy checks, and MAC broadcast domains.", "difficulty": "Intermediate", "estimated_minutes": 40},
                        ]
                    },
                    {
                        "title": "Network Layer",
                        "slug": "cn-network-layer",
                        "description": "Datagram forwarding, routing algorithms, virtual circuits.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Routing Concepts & Distance Vector vs Link State", "slug": "routing-concepts-link-state", "summary": "Dijkstra algorithm in OSPF and Bellman-Ford in RIP.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "IP Addressing",
                        "slug": "cn-ip-addressing",
                        "description": "IPv4 subnetting, CIDR prefix notation, NAT, and IPv6 headers.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "IPv4 Subnetting & CIDR Calculation", "slug": "ipv4-subnetting-cidr", "summary": "Network masks, usable host ranges, and broadcast boundaries.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Routing",
                        "slug": "cn-routing-protocols",
                        "description": "Autonomous systems, intra-domain routing (OSPF), and inter-domain routing (BGP).",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "BGP & Inter-Domain Autonomous Routing", "slug": "bgp-inter-domain-routing", "summary": "Path vector routing and AS peering policies.", "difficulty": "Advanced", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Transport Layer",
                        "slug": "cn-transport-layer",
                        "description": "Port multiplexing, reliability, flow control, and congestion avoidance.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "TCP 3-Way Handshake & Flow Control", "slug": "tcp-handshake-flow-control", "summary": "SYN/ACK flags, sequence numbers, and sliding window flow control.", "difficulty": "Intermediate", "estimated_minutes": 50},
                        ]
                    },
                    {
                        "title": "TCP / UDP",
                        "slug": "cn-tcp-udp",
                        "description": "Connection-oriented vs datagram transport comparison, AIMD congestion control.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "TCP Congestion Control vs UDP Low Latency", "slug": "tcp-congestion-vs-udp", "summary": "Slow start, congestion avoidance, fast retransmit, and UDP datagrams.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Application Layer",
                        "slug": "cn-application-layer",
                        "description": "DNS hierarchy, HTTP/1.1 vs HTTP/2/3, TLS encryption handshakes.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "DNS & Modern HTTP Protocols", "slug": "dns-and-http-protocols", "summary": "Recursive DNS resolution, HTTP keep-alive, multiplexing, and QUIC.", "difficulty": "Beginner", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Network Security Basics",
                        "slug": "cn-network-security-basics",
                        "description": "Symmetric/asymmetric cryptography, firewalls, and DDoS mitigation.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "TLS Handshake & Firewall Architectures", "slug": "tls-handshake-firewalls", "summary": "Public key exchange, certificate authorities, and packet filtering.", "difficulty": "Intermediate", "estimated_minutes": 35},
                        ]
                    },
                ]
            }
        ]
    },
    {
        "category_slug": "computer-science",
        "name": "Digital Logic",
        "slug": "digital-logic",
        "short_description": "Boolean algebra, combinational circuits, sequential flip-flops, and finite state machines.",
        "description": "Binary number systems, Boolean algebra reduction, Karnaugh maps, combinational logic design (adders, multiplexers), and sequential circuits (flip-flops, registers, counters).",
        "icon_key": "binary",
        "difficulty_level": "Beginner",
        "display_order": 5,
        "courses": [
            {
                "title": "Digital Logic Fundamentals",
                "slug": "digital-logic-fundamentals",
                "description": "Binary logic gates, Boolean simplification, and synchronous sequential circuits.",
                "difficulty": "Beginner",
                "estimated_hours": 30,
                "modules": [
                    {
                        "title": "Number Systems",
                        "slug": "dl-number-systems",
                        "description": "Binary, octal, hexadecimal representations, and 2's complement arithmetic.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Binary Conversions & 2's Complement", "slug": "binary-conversions-twos-complement", "summary": "Signed binary integer arithmetic and overflow detection.", "difficulty": "Beginner", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Boolean Algebra",
                        "slug": "dl-boolean-algebra",
                        "description": "Postulates, De Morgan's laws, sum-of-products (SOP), and product-of-sums (POS).",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "De Morgan's Laws & Canonical Forms", "slug": "de-morgans-laws-canonical-forms", "summary": "Boolean identities and minterm/maxterm canonical forms.", "difficulty": "Beginner", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Logic Gates",
                        "slug": "dl-logic-gates",
                        "description": "AND, OR, NOT, NAND, NOR universal gates, XOR, and propagation delays.",
                        "estimated_minutes": 50,
                        "topics": [
                            {"title": "Universal Gates & Truth Tables", "slug": "universal-gates-truth-tables", "summary": "NAND/NOR complete functional sets.", "difficulty": "Beginner", "estimated_minutes": 30},
                        ]
                    },
                    {
                        "title": "K-Maps",
                        "slug": "dl-k-maps",
                        "description": "2, 3, and 4-variable Karnaugh maps, prime implicants, and don't-care conditions.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Karnaugh Map Minimization", "slug": "k-map-minimization", "summary": "Gray code adjacency grouping for minimal SOP expressions.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Combinational Circuits",
                        "slug": "dl-combinational-circuits",
                        "description": "Half/full adders, subtractors, multiplexers, demultiplexers, decoders.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Adders & Multiplexers Design", "slug": "adders-multiplexers-design", "summary": "Ripple carry adders and MUX-based Boolean logic implementation.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Sequential Circuits",
                        "slug": "dl-sequential-circuits",
                        "description": "Latches, clocking schemes, setup/hold times, and metastability.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "Latches vs Flip-Flops Timing", "slug": "latches-vs-flip-flops", "summary": "Level-sensitive latches vs edge-triggered flip-flop timing diagrams.", "difficulty": "Intermediate", "estimated_minutes": 40},
                        ]
                    },
                    {
                        "title": "Flip-Flops",
                        "slug": "dl-flip-flops",
                        "description": "SR, JK, D, and T flip-flops, characteristic equations, and excitation tables.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "JK & D Flip-Flop Operation", "slug": "jk-d-flip-flop-operation", "summary": "Toggle modes, race-around conditions, and master-slave setups.", "difficulty": "Intermediate", "estimated_minutes": 40},
                        ]
                    },
                    {
                        "title": "Registers",
                        "slug": "dl-registers",
                        "description": "SISO, SIPO, PISO, PIPO shift registers and universal shift registers.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Shift Register Architectures", "slug": "shift-register-architectures", "summary": "Serial and parallel data conversion registers.", "difficulty": "Beginner", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Counters",
                        "slug": "dl-counters",
                        "description": "Asynchronous ripple counters and synchronous decade/mod-N counters.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "Synchronous Counter Design", "slug": "synchronous-counter-design", "summary": "Excitation table synthesis for modulo-N sequence counters.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                ]
            }
        ]
    },
    {
        "category_slug": "computer-science",
        "name": "Computer Organization & Architecture",
        "slug": "computer-organization-and-architecture",
        "short_description": "CPU datapath, instruction pipelines, memory hierarchy, cache coherence, and RISC/CISC.",
        "description": "Instruction set architectures (RISC-V/MIPS), arithmetic logic units, single-cycle and pipelined datapath design, pipeline hazards, branch prediction, and multi-level cache hierarchies.",
        "icon_key": "server",
        "difficulty_level": "Advanced",
        "display_order": 6,
        "courses": [
            {
                "title": "Computer Organization & Architecture",
                "slug": "coa-fundamentals",
                "description": "Von Neumann architecture, pipelined processors, memory caches, and bus interconnects.",
                "difficulty": "Advanced",
                "estimated_hours": 42,
                "modules": [
                    {
                        "title": "Instruction Set Architecture",
                        "slug": "coa-isa",
                        "description": "RISC vs CISC, machine instruction formats, addressing modes, and register files.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "RISC vs CISC & Instruction Formats", "slug": "risc-vs-cisc-instruction-formats", "summary": "Load-store architectures vs memory-operand CISC instructions.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Pipelining & Hazards",
                        "slug": "coa-pipelining",
                        "description": "5-stage classic pipeline (IF, ID, EX, MEM, WB), structural, data, and control hazards.",
                        "estimated_minutes": 100,
                        "topics": [
                            {"title": "Pipeline Hazards & Forwarding", "slug": "pipeline-hazards-forwarding", "summary": "RAW dependencies, pipeline stalls, forwarding paths, and branch delay slots.", "difficulty": "Advanced", "estimated_minutes": 55},
                        ]
                    },
                    {
                        "title": "Memory Hierarchy & Caches",
                        "slug": "coa-memory-hierarchy",
                        "description": "Direct-mapped, set-associative caches, cache hit/miss penalties, and write policies.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Cache Associativity & Mapping", "slug": "cache-associativity-mapping", "summary": "Tag, index, offset bit calculation and replacement policies (LRU).", "difficulty": "Advanced", "estimated_minutes": 50},
                        ]
                    },
                ]
            }
        ]
    },

    # --- Programming ---
    {
        "category_slug": "programming",
        "name": "Python",
        "slug": "python",
        "short_description": "Clean modern Python programming from syntax fundamentals to OOP and algorithms.",
        "description": "Complete Python programming curriculum spanning dynamic typing, scoping, data structures, object-oriented design, functional features, context managers, and core libraries.",
        "icon_key": "file-code",
        "difficulty_level": "Beginner",
        "display_order": 7,
        "courses": [
            {
                "title": "Python Programming",
                "slug": "python-programming",
                "description": "Comprehensive journey from foundational syntax to object-oriented programming and standard libraries.",
                "difficulty": "Beginner",
                "estimated_hours": 32,
                "modules": [
                    {
                        "title": "Fundamentals",
                        "slug": "python-fundamentals",
                        "description": "Python interpreter model, dynamic typing, primitive types, and operators.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Python Variables & Data Types", "slug": "python-variables-data-types", "summary": "Dynamic references, integers, floats, booleans, and mutability distinctions.", "difficulty": "Beginner", "estimated_minutes": 35},
                            {"title": "Type Casting & Operators", "slug": "python-type-casting-operators", "summary": "Implicit vs explicit casting, arithmetic and boolean operators.", "difficulty": "Beginner", "estimated_minutes": 25},
                        ]
                    },
                    {
                        "title": "Control Flow",
                        "slug": "python-control-flow",
                        "description": "Conditionals, truthy/falsy evaluation, for and while iteration.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Conditional Branching & Loops", "slug": "python-conditionals-and-loops", "summary": "If-elif-else statements, while loops, for loops with range, break and continue.", "difficulty": "Beginner", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Functions",
                        "slug": "python-functions",
                        "description": "Function definitions, parameter binding (*args, **kwargs), closures, and lambda.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Defining Functions & Scope Resolution", "slug": "python-defining-functions-scope", "summary": "Def syntax, default arguments, LEGB scope rules, and first-class functions.", "difficulty": "Beginner", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Collections",
                        "slug": "python-collections",
                        "description": "Lists, tuples, dictionaries, sets, and comprehension expressions.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Lists, Dictionaries & Comprehensions", "slug": "python-lists-dicts-comprehensions", "summary": "List slicing, dict hash tables, set operations, and list/dict comprehensions.", "difficulty": "Beginner", "estimated_minutes": 50},
                        ]
                    },
                    {
                        "title": "Strings",
                        "slug": "python-strings",
                        "description": "String formatting (f-strings), slicing, and common methods.",
                        "estimated_minutes": 50,
                        "topics": [
                            {"title": "String Formatting & Methods", "slug": "python-string-formatting", "summary": "F-strings, split/join methods, and immutable byte representations.", "difficulty": "Beginner", "estimated_minutes": 30},
                        ]
                    },
                    {
                        "title": "OOP",
                        "slug": "python-oop",
                        "description": "Classes, instance variables, dunder methods, inheritance, and encapsulation.",
                        "estimated_minutes": 100,
                        "topics": [
                            {"title": "Classes, Inheritance & Polymorphism", "slug": "python-classes-inheritance", "summary": "__init__, self convention, super(), method overriding, and duck typing.", "difficulty": "Intermediate", "estimated_minutes": 55},
                        ]
                    },
                    {
                        "title": "Exception Handling",
                        "slug": "python-exception-handling",
                        "description": "Try, except, else, finally blocks and custom exception hierarchies.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Try-Except Blocks & Custom Exceptions", "slug": "python-exceptions-hierarchy", "summary": "Handling built-in errors and raising domain-specific exceptions.", "difficulty": "Beginner", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Files",
                        "slug": "python-files",
                        "description": "File modes, context managers (with statement), JSON serialization.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "File I/O & Context Managers", "slug": "python-file-io-context-managers", "summary": "Open modes, auto-closing resources, and JSON loading/dumping.", "difficulty": "Beginner", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Modules & Packages",
                        "slug": "python-modules-and-packages",
                        "description": "Import system, __name__ == '__main__', packages, and virtual environments.",
                        "estimated_minutes": 50,
                        "topics": [
                            {"title": "Module System & Package Imports", "slug": "python-module-system-imports", "summary": "Import mechanics, sys.path resolution, and package structuring.", "difficulty": "Beginner", "estimated_minutes": 30},
                        ]
                    },
                    {
                        "title": "Basic Algorithms",
                        "slug": "python-basic-algorithms",
                        "description": "Standard Python algorithmic patterns, bisect, collections.Counter, and sorting keys.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "Algorithmic Patterns in Python", "slug": "python-algorithmic-patterns", "summary": "Custom sort keys, defaultdict, Counter, and deque idioms.", "difficulty": "Intermediate", "estimated_minutes": 40},
                        ]
                    },
                ]
            }
        ]
    },
    {
        "category_slug": "programming",
        "name": "C Programming",
        "slug": "c-programming",
        "short_description": "Procedural programming, direct memory manipulation with pointers, and manual memory management.",
        "description": "Essential C programming covering pointers, arrays, memory allocation, struct layouts, file handling, and the C preprocessor.",
        "icon_key": "terminal",
        "difficulty_level": "Beginner",
        "display_order": 8,
        "courses": [
            {
                "title": "C Programming",
                "slug": "c-programming",
                "description": "Structured programming, manual pointer arithmetic, and system memory management.",
                "difficulty": "Beginner",
                "estimated_hours": 30,
                "modules": [
                    {
                        "title": "Fundamentals",
                        "slug": "c-fundamentals",
                        "description": "C syntax, standard I/O (printf/scanf), primitive types, and compile pipeline.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "C Syntax & Compilation Stages", "slug": "c-compilation-stages", "summary": "Preprocessor, compiler, assembler, and linker workflow.", "difficulty": "Beginner", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Operators",
                        "slug": "c-operators",
                        "description": "Bitwise operations, arithmetic, relational, and logical evaluation.",
                        "estimated_minutes": 50,
                        "topics": [
                            {"title": "Bitwise Operators & Masks", "slug": "c-bitwise-operators", "summary": "Shifting, bit masking, and bitwise boolean manipulation.", "difficulty": "Beginner", "estimated_minutes": 30},
                        ]
                    },
                    {
                        "title": "Control Flow",
                        "slug": "c-control-flow",
                        "description": "If-else conditions, switch-case statements, for and while loops.",
                        "estimated_minutes": 50,
                        "topics": [
                            {"title": "Iteration & Switch Statements", "slug": "c-iteration-switch", "summary": "Loop constructs, break, continue, and switch fall-through.", "difficulty": "Beginner", "estimated_minutes": 30},
                        ]
                    },
                    {
                        "title": "Functions",
                        "slug": "c-functions",
                        "description": "Pass-by-value, prototypes, static functions, and recursive stacks.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Function Prototypes & Call Stack", "slug": "c-prototypes-call-stack", "summary": "Stack frames, function declarations, and return registers.", "difficulty": "Beginner", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Arrays",
                        "slug": "c-arrays",
                        "description": "1D and 2D arrays, contiguous storage, and bounds safety.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Array Memory Layout & Indexing", "slug": "c-array-memory-layout", "summary": "Base address arithmetic and multi-dimensional row-major storage.", "difficulty": "Beginner", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Strings",
                        "slug": "c-strings",
                        "description": "Null-terminated char buffers and string.h standard functions.",
                        "estimated_minutes": 50,
                        "topics": [
                            {"title": "Null-Terminated String Manipulation", "slug": "c-null-terminated-strings", "summary": "strcpy, strlen, strcmp, and buffer overflow prevention.", "difficulty": "Beginner", "estimated_minutes": 30},
                        ]
                    },
                    {
                        "title": "Pointers",
                        "slug": "c-pointers",
                        "description": "Memory addresses, pointer dereferencing, pointer arithmetic, and double pointers.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Pointers & Address Arithmetic", "slug": "c-pointers-address-arithmetic", "summary": "The * and & operators, void pointers, and pointer offsets.", "difficulty": "Intermediate", "estimated_minutes": 50},
                        ]
                    },
                    {
                        "title": "Structures",
                        "slug": "c-structures",
                        "description": "Struct declarations, padding/alignment, unions, and typedef.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "Struct Alignment & Member Access", "slug": "c-struct-alignment", "summary": "Arrow -> vs dot . operators, memory padding, and unions.", "difficulty": "Intermediate", "estimated_minutes": 40},
                        ]
                    },
                    {
                        "title": "Dynamic Memory",
                        "slug": "c-dynamic-memory",
                        "description": "Heap allocation with malloc, calloc, realloc, and free.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Heap Allocation & Memory Leaks", "slug": "c-heap-allocation-free", "summary": "malloc/free lifecycle, dangling pointers, and memory sanitization.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "File Handling",
                        "slug": "c-file-handling",
                        "description": "FILE stream pointers, fopen, fread, fwrite, and fclose.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Binary & Text File Streams", "slug": "c-file-streams", "summary": "Buffered I/O, EOF flags, and binary struct serialization.", "difficulty": "Intermediate", "estimated_minutes": 35},
                        ]
                    },
                ]
            }
        ]
    },
    {
        "category_slug": "programming",
        "name": "C++",
        "slug": "cpp",
        "short_description": "Modern C++ with OOP, templates, RAII, STL containers, and move semantics.",
        "description": "Comprehensive C++ curriculum focusing on object-oriented programming, standard template library (STL), memory management, and modern C++ features.",
        "icon_key": "code",
        "difficulty_level": "Intermediate",
        "display_order": 9,
        "courses": [
            {
                "title": "C++ Programming",
                "slug": "cpp-programming",
                "description": "Modern C++ from procedural core to templates, STL, and object-oriented abstractions.",
                "difficulty": "Intermediate",
                "estimated_hours": 36,
                "modules": [
                    {
                        "title": "Fundamentals",
                        "slug": "cpp-fundamentals",
                        "description": "C++ streams, namespaces, auto typing, and modern enhancements.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "C++ Modern Syntax & Streams", "slug": "cpp-syntax-and-streams", "summary": "iostream, namespaces, references, and type inference.", "difficulty": "Beginner", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Functions",
                        "slug": "cpp-functions",
                        "description": "Function overloading, default arguments, inline functions, and pass by reference.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Overloading & Pass-By-Reference", "slug": "cpp-overloading-references", "summary": "Const references, function name mangling, and inline execution.", "difficulty": "Beginner", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Arrays & Strings",
                        "slug": "cpp-arrays-and-strings",
                        "description": "std::vector, std::array, and std::string modern wrappers.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Standard Containers (vector & string)", "slug": "cpp-vector-and-string", "summary": "Dynamic array growth, capacity vs size, and string methods.", "difficulty": "Beginner", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Pointers & References",
                        "slug": "cpp-pointers-and-references",
                        "description": "Lvalue/rvalue references, smart pointers (unique_ptr, shared_ptr), and RAII.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Smart Pointers & RAII Paradigm", "slug": "cpp-smart-pointers-raii", "summary": "std::unique_ptr, std::shared_ptr, and automatic destructor cleanup.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Classes & Objects",
                        "slug": "cpp-classes-and-objects",
                        "description": "Constructors, destructors, rule of three/five, and access specifiers.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Class Encapsulation & Constructors", "slug": "cpp-class-encapsulation", "summary": "Initialization lists, copy constructors, and operator overloading.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Inheritance",
                        "slug": "cpp-inheritance",
                        "description": "Public/protected/private inheritance, constructor chaining, and multiple inheritance.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "Inheritance Models & Base Classes", "slug": "cpp-inheritance-models", "summary": "Base-derived class relationships and diamond problem resolution.", "difficulty": "Intermediate", "estimated_minutes": 40},
                        ]
                    },
                    {
                        "title": "Polymorphism",
                        "slug": "cpp-polymorphism",
                        "description": "Virtual functions, vtable mechanics, abstract classes, and pure virtual interfaces.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Virtual Functions & VTable Dispatch", "slug": "cpp-virtual-functions-vtable", "summary": "Runtime dynamic dispatch and abstract interfaces.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Templates",
                        "slug": "cpp-templates",
                        "description": "Function and class templates, type traits, and compile-time specialization.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Generic Programming with Templates", "slug": "cpp-generic-templates", "summary": "Template instantiation, template parameters, and generic algorithms.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "STL",
                        "slug": "cpp-stl",
                        "description": "Standard Template Library containers, iterators, and <algorithm> utilities.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "STL Containers & Iterators", "slug": "cpp-stl-containers-iterators", "summary": "Map, set, unordered_map, priority_queue, and std::sort.", "difficulty": "Intermediate", "estimated_minutes": 50},
                        ]
                    },
                    {
                        "title": "File Handling",
                        "slug": "cpp-file-handling",
                        "description": "fstream, ifstream, and ofstream stream operations.",
                        "estimated_minutes": 50,
                        "topics": [
                            {"title": "Modern File Streams", "slug": "cpp-file-streams", "summary": "RAII file opening, formatted text reading, and binary streams.", "difficulty": "Beginner", "estimated_minutes": 30},
                        ]
                    },
                ]
            }
        ]
    },
    {
        "category_slug": "programming",
        "name": "Java",
        "slug": "java",
        "short_description": "Platform-independent OOP, JVM architecture, garbage collection, and collections.",
        "description": "Enterprise-grade Java programming covering JVM bytecode, OOP principles, interfaces, exception handling, collections framework, generics, and concurrent multithreading.",
        "icon_key": "coffee",
        "difficulty_level": "Intermediate",
        "display_order": 10,
        "courses": [
            {
                "title": "Java Programming",
                "slug": "java-programming",
                "description": "Enterprise object-oriented Java covering JVM internals, collections, and concurrency.",
                "difficulty": "Intermediate",
                "estimated_hours": 38,
                "modules": [
                    {
                        "title": "Java Fundamentals",
                        "slug": "java-fundamentals",
                        "description": "JVM, JRE, JDK, bytecode compilation, primitives, and string pool.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "JVM Architecture & Bytecode", "slug": "jvm-architecture-bytecode", "summary": "Class loaders, execution engine, heap/stack areas, and JIT compiler.", "difficulty": "Beginner", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Classes & Objects",
                        "slug": "java-classes-and-objects",
                        "description": "Class members, constructors, static keyword, and garbage collection.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "Class Definitions & Memory Allocation", "slug": "java-class-definitions-memory", "summary": "Reference types, garbage collection roots, and method overloading.", "difficulty": "Beginner", "estimated_minutes": 40},
                        ]
                    },
                    {
                        "title": "Inheritance",
                        "slug": "java-inheritance",
                        "description": "Single inheritance, super keyword, and method overriding (@Override).",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Extending Classes & Super Keyword", "slug": "java-extending-classes", "summary": "Subclassing, superclass constructor invocation, and final classes.", "difficulty": "Beginner", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Polymorphism",
                        "slug": "java-polymorphism",
                        "description": "Compile-time vs runtime polymorphism, dynamic method dispatch.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Runtime Polymorphism & Dynamic Binding", "slug": "java-runtime-polymorphism", "summary": "Upcasting, downcasting, and instanceof type checking.", "difficulty": "Intermediate", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Abstraction",
                        "slug": "java-abstraction",
                        "description": "Abstract classes, partial implementation, and design guidelines.",
                        "estimated_minutes": 50,
                        "topics": [
                            {"title": "Abstract Classes & Method Contracts", "slug": "java-abstract-classes", "summary": "Declaring abstract methods and enforcing derived contracts.", "difficulty": "Intermediate", "estimated_minutes": 30},
                        ]
                    },
                    {
                        "title": "Interfaces",
                        "slug": "java-interfaces",
                        "description": "Interface contracts, multiple implementation, default/static methods.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Interface Contracts & Default Methods", "slug": "java-interface-contracts", "summary": "Multiple inheritance of type and functional interfaces.", "difficulty": "Intermediate", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Exception Handling",
                        "slug": "java-exception-handling",
                        "description": "Checked vs unchecked exceptions, try-catch-finally, and try-with-resources.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Checked vs Runtime Exceptions", "slug": "java-checked-runtime-exceptions", "summary": "Throwable hierarchy, AutoCloseable, and custom exceptions.", "difficulty": "Intermediate", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Collections",
                        "slug": "java-collections",
                        "description": "List, Set, Map interfaces, ArrayList, HashSet, HashMap, and iterators.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Java Collections Framework Core", "slug": "java-collections-framework-core", "summary": "HashMap bucketing, equals/hashCode contracts, and List implementations.", "difficulty": "Intermediate", "estimated_minutes": 50},
                        ]
                    },
                    {
                        "title": "Generics",
                        "slug": "java-generics",
                        "description": "Type parameters, bounded type parameters, and wildcard expressions (? extends T).",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "Generic Types & Wildcard Bounds", "slug": "java-generic-types-wildcards", "summary": "Type erasure, PECS rule (Producer Extends, Consumer Super).", "difficulty": "Intermediate", "estimated_minutes": 40},
                        ]
                    },
                    {
                        "title": "Multithreading",
                        "slug": "java-multithreading",
                        "description": "Thread class, Runnable interface, synchronized keyword, and Executors.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Thread Synchronization & Concurrency", "slug": "java-thread-synchronization", "summary": "Intrinsic locks, volatile keyword, and java.util.concurrent thread pools.", "difficulty": "Advanced", "estimated_minutes": 50},
                        ]
                    },
                ]
            }
        ]
    },

    # --- Artificial Intelligence ---
    {
        "category_slug": "artificial-intelligence",
        "name": "Artificial Intelligence",
        "slug": "artificial-intelligence",
        "short_description": "Intelligent agents, uninformed/informed search, logic reasoning, and planning.",
        "description": "Foundations of classical AI covering rational agents, state-space search (A* search, minimax), knowledge representation, first-order logic, automated planning, and ethical considerations.",
        "icon_key": "brain",
        "difficulty_level": "Intermediate",
        "display_order": 11,
        "courses": [
            {
                "title": "AI Fundamentals",
                "slug": "ai-fundamentals",
                "description": "State space exploration, heuristic search, logic, and intelligent agent environments.",
                "difficulty": "Intermediate",
                "estimated_hours": 32,
                "modules": [
                    {
                        "title": "Introduction to AI",
                        "slug": "ai-intro",
                        "description": "History of AI, Turing test, strong vs weak AI, and agent architectures.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Foundations of Artificial Intelligence", "slug": "foundations-of-ai", "summary": "Rationality, Turing test, and AI winter cycles.", "difficulty": "Beginner", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Intelligent Agents",
                        "slug": "ai-intelligent-agents",
                        "description": "PEAS framework (Performance, Environment, Actuators, Sensors) and agent types.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "PEAS Model & Agent Taxonomies", "slug": "peas-model-agent-taxonomies", "summary": "Simple reflex, model-based, goal-based, and utility-based agents.", "difficulty": "Beginner", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Search",
                        "slug": "ai-search-algorithms",
                        "description": "Uninformed search (BFS, DFS), informed heuristic search (A*, greedy best-first).",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "A* Search & Admissible Heuristics", "slug": "a-star-heuristic-search", "summary": "Evaluation function f(n) = g(n) + h(n), consistency, and optimality proofs.", "difficulty": "Intermediate", "estimated_minutes": 50},
                        ]
                    },
                    {
                        "title": "Knowledge Representation",
                        "slug": "ai-knowledge-representation",
                        "description": "Ontologies, semantic networks, frames, and conceptual graphs.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "Ontologies & Semantic Frameworks", "slug": "ontologies-semantic-frameworks", "summary": "Structuring domain relationships and conceptual dependencies.", "difficulty": "Intermediate", "estimated_minutes": 40},
                        ]
                    },
                    {
                        "title": "Reasoning",
                        "slug": "ai-reasoning",
                        "description": "Propositional logic, first-order predicate calculus, resolution refutation.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "First-Order Logic & Resolution", "slug": "first-order-logic-resolution", "summary": "Unification, clausal normal form, and automated deduction.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Planning",
                        "slug": "ai-planning",
                        "description": "Classical planning, STRIPS representation, and partial-order planning.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "STRIPS & Forward/Backward State Search", "slug": "strips-planning", "summary": "Preconditions, actions, add/delete lists, and goal state satisfaction.", "difficulty": "Intermediate", "estimated_minutes": 40},
                        ]
                    },
                    {
                        "title": "AI Ethics",
                        "slug": "ai-ethics",
                        "description": "Algorithmic bias, transparency, explainability, safety, and alignment.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Bias, Fairness & Explainability in AI", "slug": "bias-fairness-explainability", "summary": "Auditing disparate impact, XAI interpretability, and alignment principles.", "difficulty": "Beginner", "estimated_minutes": 35},
                        ]
                    },
                ]
            }
        ]
    },
    {
        "category_slug": "artificial-intelligence",
        "name": "Machine Learning",
        "slug": "machine-learning",
        "short_description": "Supervised learning, unsupervised clustering, feature engineering, and evaluation.",
        "description": "Mathematical formulations and algorithmic implementation of regression, decision trees, support vector machines, clustering, dimensionality reduction, regularization, and cross-validation.",
        "icon_key": "sparkles",
        "difficulty_level": "Intermediate",
        "display_order": 12,
        "courses": [
            {
                "title": "Machine Learning Fundamentals",
                "slug": "machine-learning-fundamentals",
                "description": "Core algorithms in supervised learning, unsupervised clustering, and statistical validation.",
                "difficulty": "Intermediate",
                "estimated_hours": 40,
                "modules": [
                    {
                        "title": "ML Workflow",
                        "slug": "ml-workflow",
                        "description": "Problem framing, train/validation/test splits, and baseline models.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "The End-to-End ML Pipeline", "slug": "end-to-end-ml-pipeline", "summary": "Data ingestion, leakage prevention, and experiment logging.", "difficulty": "Beginner", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Data Preparation",
                        "slug": "ml-data-preparation",
                        "description": "Missing value imputation, categorical encoding, scaling, and normalization.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "Feature Scaling & One-Hot Encoding", "slug": "feature-scaling-encoding", "summary": "StandardScaler vs MinMaxScaler and handling high-cardinality features.", "difficulty": "Beginner", "estimated_minutes": 40},
                        ]
                    },
                    {
                        "title": "Regression",
                        "slug": "ml-regression",
                        "description": "Ordinary Least Squares, gradient descent, Mean Squared Error loss.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Linear Regression & Gradient Descent", "slug": "linear-regression-gradient-descent", "summary": "Normal equation, analytical derivation, and iterative gradient updates.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Classification",
                        "slug": "ml-classification",
                        "description": "Logistic regression, decision trees, Random Forests, and SVMs.",
                        "estimated_minutes": 100,
                        "topics": [
                            {"title": "Logistic Regression & Decision Trees", "slug": "logistic-regression-decision-trees", "summary": "Sigmoid activations, log loss, Gini impurity, and information gain.", "difficulty": "Intermediate", "estimated_minutes": 55},
                        ]
                    },
                    {
                        "title": "Clustering",
                        "slug": "ml-clustering",
                        "description": "K-Means, hierarchical agglomerative clustering, and DBSCAN.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "K-Means & Density-Based Clustering", "slug": "k-means-and-dbscan", "summary": "Centroid initialization, elbow method, and density reachability.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Feature Engineering",
                        "slug": "ml-feature-engineering",
                        "description": "Domain features, interaction terms, and PCA dimensionality reduction.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Principal Component Analysis (PCA)", "slug": "pca-dimensionality-reduction", "summary": "Eigenvectors, covariance matrix decomposition, and variance retention.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Model Evaluation",
                        "slug": "ml-model-evaluation",
                        "description": "Confusion matrix, Precision, Recall, F1 score, ROC-AUC curves.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "Classification Metrics & ROC Curves", "slug": "classification-metrics-roc", "summary": "Type I vs Type II errors, PR curves, and AUC statistical power.", "difficulty": "Intermediate", "estimated_minutes": 40},
                        ]
                    },
                    {
                        "title": "Overfitting & Regularization",
                        "slug": "ml-overfitting-regularization",
                        "description": "Bias-variance trade-off, L1 Lasso, L2 Ridge, and elastic net penalization.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "L1/L2 Regularization & Bias-Variance", "slug": "regularization-bias-variance", "summary": "Shrinkage penalties, sparsity induction, and cross-validation tuning.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                ]
            }
        ]
    },
    {
        "category_slug": "artificial-intelligence",
        "name": "Deep Learning",
        "slug": "deep-learning",
        "short_description": "Multilayer perceptrons, backpropagation, CNNs, RNNs, and transformer introduction.",
        "description": "Deep artificial neural networks covering computational graphs, automatic differentiation, activation functions, convolutional vision networks, sequence models, and attention mechanisms.",
        "icon_key": "network",
        "difficulty_level": "Advanced",
        "display_order": 13,
        "courses": [
            {
                "title": "Deep Learning Fundamentals",
                "slug": "deep-learning-fundamentals",
                "description": "Neural representation learning, backpropagation calculus, and deep architectures.",
                "difficulty": "Advanced",
                "estimated_hours": 42,
                "modules": [
                    {
                        "title": "Neural Networks",
                        "slug": "dl-neural-networks",
                        "description": "Perceptrons, dense linear layers, and multi-layer architectures.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "Multilayer Perceptron & Matrix Algebra", "slug": "mlp-matrix-algebra", "summary": "Forward pass formulation, weight tensors, and bias vectors.", "difficulty": "Intermediate", "estimated_minutes": 40},
                        ]
                    },
                    {
                        "title": "Activation Functions",
                        "slug": "dl-activation-functions",
                        "description": "Sigmoid, Tanh, ReLU, Leaky ReLU, GELU, and vanishing gradients.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Non-Linear Activations & Gradient Flow", "slug": "non-linear-activations", "summary": "Saturation regimes, dead ReLUs, and zero-centered gradients.", "difficulty": "Intermediate", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Backpropagation",
                        "slug": "dl-backpropagation",
                        "description": "Multivariate chain rule, computational graphs, and loss gradient propagation.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Computational Graphs & Chain Rule", "slug": "computational-graphs-chain-rule", "summary": "Reverse-mode automatic differentiation step-by-step calculus.", "difficulty": "Advanced", "estimated_minutes": 50},
                        ]
                    },
                    {
                        "title": "Optimization",
                        "slug": "dl-optimization",
                        "description": "SGD with Momentum, RMSprop, Adam, and learning rate scheduling.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Adam Optimizer & Adaptive Learning Rates", "slug": "adam-optimizer-adaptive-learning", "summary": "First and second moment estimation with bias corrections.", "difficulty": "Advanced", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "CNNs",
                        "slug": "dl-cnns",
                        "description": "2D convolution kernels, padding, stride, pooling, and feature hierarchies.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Convolutional Layers & Spatial Invariance", "slug": "convolutional-layers-spatial-invariance", "summary": "Kernel sliding, receptive fields, and max-pooling operations.", "difficulty": "Advanced", "estimated_minutes": 50},
                        ]
                    },
                    {
                        "title": "RNNs",
                        "slug": "dl-rnns",
                        "description": "Recurrent loops, Backpropagation Through Time (BPTT), and LSTM gates.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Recurrent Cells, LSTMs & Gated Units", "slug": "lstms-and-gated-recurrent-units", "summary": "Forget gate, input gate, cell state updates, and vanishing gradient remedies.", "difficulty": "Advanced", "estimated_minutes": 50},
                        ]
                    },
                    {
                        "title": "Transformers Introduction",
                        "slug": "dl-transformers-intro",
                        "description": "Scaled dot-product attention, multi-head attention, and positional encodings.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Self-Attention Mechanism & Transformers", "slug": "self-attention-mechanism", "summary": "Query, Key, Value tensor projections and parallel sequence processing.", "difficulty": "Advanced", "estimated_minutes": 50},
                        ]
                    },
                ]
            }
        ]
    },
    {
        "category_slug": "artificial-intelligence",
        "name": "Generative Adversarial Networks (GANs)",
        "slug": "generative-adversarial-networks",
        "short_description": "Minimax game theory, generators, discriminators, Wasserstein loss, and DCGAN.",
        "description": "Theoretical framework and practical training of Generative Adversarial Networks, mode collapse mitigation, deep convolutional GANs, and conditional image synthesis.",
        "icon_key": "wand-2",
        "difficulty_level": "Advanced",
        "display_order": 14,
        "courses": [
            {
                "title": "Generative Adversarial Networks",
                "slug": "gans-fundamentals",
                "description": "Two-player minimax games, implicit density estimation, and generative image synthesis.",
                "difficulty": "Advanced",
                "estimated_hours": 30,
                "modules": [
                    {
                        "title": "Generative Modeling",
                        "slug": "gan-generative-modeling",
                        "description": "Explicit vs implicit generative models, data distribution sampling.",
                        "estimated_minutes": 50,
                        "topics": [
                            {"title": "Implicit Density Generative Frameworks", "slug": "implicit-density-generative-frameworks", "summary": "Sampling latent spaces and transforming distributions.", "difficulty": "Intermediate", "estimated_minutes": 30},
                        ]
                    },
                    {
                        "title": "Generator",
                        "slug": "gan-generator",
                        "description": "Latent vector mapping, transposed convolutions, and generator loss.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Generator Architecture & Latent Spaces", "slug": "generator-architecture-latent-spaces", "summary": "Transposed 2D convolutions and fractional stride upsampling.", "difficulty": "Advanced", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Discriminator",
                        "slug": "gan-discriminator",
                        "description": "Binary real/fake classification, strided convolutions, and spectral norm.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Discriminator Classifier & Critic Network", "slug": "discriminator-classifier-critic", "summary": "Distinguishing true sample distribution from generated artifacts.", "difficulty": "Advanced", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "GAN Training",
                        "slug": "gan-training",
                        "description": "Minimax objective, alternating gradient updates, and Nash equilibrium.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Minimax Two-Player Game Dynamics", "slug": "minimax-game-dynamics", "summary": "Alternating optimization steps and gradient saturation avoidance.", "difficulty": "Advanced", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Loss Functions",
                        "slug": "gan-loss-functions",
                        "description": "Minimax cross-entropy, Non-saturating loss, Wasserstein distance.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "Wasserstein Loss & Earth Mover Distance", "slug": "wasserstein-loss-earth-mover", "summary": "WGAN Lipschitz continuity constraint and gradient penalty (WGAN-GP).", "difficulty": "Advanced", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "DCGAN",
                        "slug": "gan-dcgan",
                        "description": "Deep Convolutional GAN architectural guidelines and batch normalization.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "DCGAN Architectural Principles", "slug": "dcgan-architectural-principles", "summary": "Replacing pooling with strided convolutions and leaky ReLU activations.", "difficulty": "Advanced", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "Conditional GAN",
                        "slug": "gan-conditional-gan",
                        "description": "Class-conditioned latent synthesis and label embedding concat.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Conditional Image Generation (cGAN)", "slug": "conditional-image-generation", "summary": "Conditioning generator and discriminator on category labels.", "difficulty": "Advanced", "estimated_minutes": 35},
                        ]
                    },
                    {
                        "title": "GAN Challenges",
                        "slug": "gan-challenges",
                        "description": "Mode collapse, vanishing gradients, non-convergence, and evaluation FID.",
                        "estimated_minutes": 60,
                        "topics": [
                            {"title": "Mode Collapse & Fréchet Inception Distance", "slug": "mode-collapse-and-fid-metric", "summary": "Identifying collapse states and measuring distribution fidelity with FID.", "difficulty": "Advanced", "estimated_minutes": 35},
                        ]
                    },
                ]
            }
        ]
    },
    {
        "category_slug": "artificial-intelligence",
        "name": "Natural Language Processing",
        "slug": "natural-language-processing",
        "short_description": "Tokenization, language models, word embeddings, sequence-to-sequence, and transformers.",
        "description": "Modern computational linguistics covering Byte-Pair Encoding tokenization, Word2Vec, GloVe, recurrent language models, BERT masked modeling, and GPT autoregressive architectures.",
        "icon_key": "message-square",
        "difficulty_level": "Advanced",
        "display_order": 15,
        "courses": [
            {
                "title": "Natural Language Processing",
                "slug": "nlp-fundamentals",
                "description": "Computational linguistics, text representation, transformer language models, and generation.",
                "difficulty": "Advanced",
                "estimated_hours": 36,
                "modules": [
                    {
                        "title": "Text Processing & Tokenization",
                        "slug": "nlp-tokenization",
                        "description": "Subword tokenization, BPE, WordPiece, and vocabulary mapping.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "Subword Tokenization (BPE & WordPiece)", "slug": "subword-tokenization-bpe", "summary": "Vocabulary construction and handling out-of-vocabulary words.", "difficulty": "Intermediate", "estimated_minutes": 40},
                        ]
                    },
                    {
                        "title": "Word Embeddings",
                        "slug": "nlp-word-embeddings",
                        "description": "Distributed semantic representations, Skip-Gram, CBOW, and GloVe.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Word2Vec & Distributed Semantics", "slug": "word2vec-distributed-semantics", "summary": "Vector space analogies, cosine similarity, and negative sampling.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Pre-trained Language Models",
                        "slug": "nlp-pretrained-models",
                        "description": "BERT encoder architecture, GPT decoder generation, and fine-tuning paradigms.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Encoder vs Decoder Transformer Models", "slug": "encoder-vs-decoder-models", "summary": "Masked language modeling (BERT) vs causal autoregression (GPT).", "difficulty": "Advanced", "estimated_minutes": 50},
                        ]
                    },
                ]
            }
        ]
    },
    {
        "category_slug": "artificial-intelligence",
        "name": "Computer Vision",
        "slug": "computer-vision",
        "short_description": "Digital image representation, filtering, edge detection, object detection, and segmentation.",
        "description": "Core computer vision algorithms spanning spatial filtering, morphological operations, convolutional backbones (ResNet), object detection (YOLO), and semantic segmentation (U-Net).",
        "icon_key": "eye",
        "difficulty_level": "Advanced",
        "display_order": 16,
        "courses": [
            {
                "title": "Computer Vision Fundamentals",
                "slug": "computer-vision-fundamentals",
                "description": "Image processing, feature descriptors, convolutional backbones, and object detection.",
                "difficulty": "Advanced",
                "estimated_hours": 36,
                "modules": [
                    {
                        "title": "Image Formation & Filtering",
                        "slug": "cv-image-filtering",
                        "description": "Color spaces, Gaussian blurring, Sobel gradients, and Canny edge detection.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "Spatial Convolution & Edge Detection", "slug": "spatial-convolution-edge-detection", "summary": "Image gradients, non-maximum suppression, and hysteresis thresholding.", "difficulty": "Intermediate", "estimated_minutes": 40},
                        ]
                    },
                    {
                        "title": "Deep Vision Backbones",
                        "slug": "cv-vision-backbones",
                        "description": "VGG, ResNet residual connections, and feature pyramid networks.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "ResNet & Residual Skip Connections", "slug": "resnet-residual-skip-connections", "summary": "Identity shortcuts, degradation problem resolution, and deep feature maps.", "difficulty": "Advanced", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Object Detection & Segmentation",
                        "slug": "cv-detection-segmentation",
                        "description": "Bounding box regression, IoU, non-max suppression, YOLO, and U-Net.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Single-Shot Object Detection (YOLO)", "slug": "single-shot-object-detection", "summary": "Grid anchor boxes, class probabilities, and intersection-over-union.", "difficulty": "Advanced", "estimated_minutes": 50},
                        ]
                    },
                ]
            }
        ]
    },

    # --- Mathematics ---
    {
        "category_slug": "mathematics",
        "name": "Discrete Mathematics",
        "slug": "discrete-mathematics",
        "short_description": "Set theory, predicate logic, relations, combinatorics, and graph theory.",
        "description": "Formal discrete structures essential for computing: sets, functions, equivalence relations, mathematical induction, pigeonhole principle, permutations, combinations, and recurrence relations.",
        "icon_key": "sigma",
        "difficulty_level": "Beginner",
        "display_order": 17,
        "courses": [
            {
                "title": "Discrete Mathematics",
                "slug": "discrete-mathematics",
                "description": "Formal mathematical logic, sets, relations, combinatorics, and induction proofs.",
                "difficulty": "Beginner",
                "estimated_hours": 34,
                "modules": [
                    {
                        "title": "Sets & Relations",
                        "slug": "dm-sets-and-relations",
                        "description": "Set operations, Cartesian products, equivalence relations, and partial orders.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Equivalence Relations & Partitions", "slug": "equivalence-relations-partitions", "summary": "Reflexive, symmetric, transitive properties and equivalence classes.", "difficulty": "Beginner", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Combinatorics",
                        "slug": "dm-combinatorics",
                        "description": "Permutations, combinations, inclusion-exclusion, and Pigeonhole principle.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Counting Principles & Pigeonhole Principle", "slug": "counting-principles-pigeonhole", "summary": "Permutation formulas, binomial coefficients, and Dirichlet pigeonhole proofs.", "difficulty": "Beginner", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Mathematical Induction",
                        "slug": "dm-mathematical-induction",
                        "description": "Weak induction, strong induction, and well-ordering principle.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "Induction Proof Techniques", "slug": "induction-proof-techniques", "summary": "Base case validation, inductive hypothesis, and inductive step.", "difficulty": "Intermediate", "estimated_minutes": 40},
                        ]
                    },
                ]
            }
        ]
    },
    {
        "category_slug": "mathematics",
        "name": "Probability",
        "slug": "probability",
        "short_description": "Sample spaces, Bayes theorem, random variables, and expectation.",
        "description": "Probability theory for computer science and data modeling: Kolmogorov axioms, conditional probability, Bayes rule, discrete/continuous random variables, and variance.",
        "icon_key": "dice-5",
        "difficulty_level": "Intermediate",
        "display_order": 18,
        "courses": [
            {
                "title": "Probability for Computing",
                "slug": "probability-for-computing",
                "description": "Sample spaces, conditional independence, random variables, and probability distributions.",
                "difficulty": "Intermediate",
                "estimated_hours": 32,
                "modules": [
                    {
                        "title": "Probability Axioms & Bayes Rule",
                        "slug": "prob-axioms-bayes",
                        "description": "Sample spaces, disjoint events, conditional probability, and Bayes Theorem.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Conditional Probability & Bayes Theorem", "slug": "conditional-prob-bayes-theorem", "summary": "Prior probability, likelihood, posterior distribution, and independence.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Random Variables & Expectations",
                        "slug": "prob-random-variables",
                        "description": "PMF, PDF, cumulative distribution functions, expected value, and variance.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Expectation, Variance & Moments", "slug": "expectation-variance-moments", "summary": "Linearity of expectation, covariance, and standard deviation.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                ]
            }
        ]
    },
    {
        "category_slug": "mathematics",
        "name": "Statistics",
        "slug": "statistics",
        "short_description": "Descriptive statistics, hypothesis testing, confidence intervals, and regression.",
        "description": "Inferential statistics and data modeling: central tendency, dispersion, Central Limit Theorem, t-tests, z-tests, p-values, and maximum likelihood estimation.",
        "icon_key": "bar-chart",
        "difficulty_level": "Intermediate",
        "display_order": 19,
        "courses": [
            {
                "title": "Statistical Inference & Modeling",
                "slug": "statistical-inference-modeling",
                "description": "Sampling distributions, Central Limit Theorem, hypothesis testing, and p-values.",
                "difficulty": "Intermediate",
                "estimated_hours": 30,
                "modules": [
                    {
                        "title": "Sampling & Central Limit Theorem",
                        "slug": "stat-sampling-clt",
                        "description": "Sample distributions, standard error, and Central Limit Theorem asymptotic normality.",
                        "estimated_minutes": 70,
                        "topics": [
                            {"title": "Central Limit Theorem & Sampling Error", "slug": "clt-and-sampling-error", "summary": "Distribution of sample means and standard error scaling with sqrt(n).", "difficulty": "Intermediate", "estimated_minutes": 40},
                        ]
                    },
                    {
                        "title": "Hypothesis Testing",
                        "slug": "stat-hypothesis-testing",
                        "description": "Null/alternative hypotheses, Type I/II errors, p-values, t-tests, and ANOVA.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Significance Testing & P-Values", "slug": "significance-testing-p-values", "summary": "Formulating hypotheses, rejection regions, and critical values.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                ]
            }
        ]
    },
    {
        "category_slug": "mathematics",
        "name": "Linear Algebra",
        "slug": "linear-algebra",
        "short_description": "Vector spaces, matrix transformations, determinants, eigenvalues, and SVD.",
        "description": "Core linear algebra powering graphics and AI: vector arithmetic, dot products, matrix multiplication, linear independence, rank, nullity, determinants, eigenvalues, and SVD decomposition.",
        "icon_key": "grid",
        "difficulty_level": "Intermediate",
        "display_order": 20,
        "courses": [
            {
                "title": "Linear Algebra Fundamentals",
                "slug": "linear-algebra-fundamentals",
                "description": "Vector spaces, linear maps, matrix determinants, and spectral eigenvalue decomposition.",
                "difficulty": "Intermediate",
                "estimated_hours": 36,
                "modules": [
                    {
                        "title": "Vectors & Matrix Operations",
                        "slug": "la-vectors-and-matrices",
                        "description": "Vector dot products, norms, matrix multiplication, transpose, and rank.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Vector Spaces & Matrix Multiplication", "slug": "vector-spaces-matrix-mult", "summary": "Basis, dimension, column spaces, and matrix transformation geometry.", "difficulty": "Beginner", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Eigenvalues & Eigenvectors",
                        "slug": "la-eigenvalues-eigenvectors",
                        "description": "Characteristic polynomial, diagonal matrices, and spectral theorem.",
                        "estimated_minutes": 90,
                        "topics": [
                            {"title": "Eigenvalue Decomposition & SVD", "slug": "eigenvalue-decomposition-svd", "summary": "Singular value decomposition (SVD) and geometric stretch factors.", "difficulty": "Intermediate", "estimated_minutes": 50},
                        ]
                    },
                ]
            }
        ]
    },
    {
        "category_slug": "mathematics",
        "name": "Calculus",
        "slug": "calculus",
        "short_description": "Limits, derivatives, partial derivatives, integrals, and gradient vectors.",
        "description": "Single-variable and multivariable calculus: limits, continuous functions, differentiation rules, chain rule, partial derivatives, gradients, and Taylor series.",
        "icon_key": "function-square",
        "difficulty_level": "Intermediate",
        "display_order": 21,
        "courses": [
            {
                "title": "Calculus for Engineering & AI",
                "slug": "calculus-for-engineering",
                "description": "Differentiation, integration, multivariable partial derivatives, and gradient fields.",
                "difficulty": "Intermediate",
                "estimated_hours": 35,
                "modules": [
                    {
                        "title": "Differentiation & Chain Rule",
                        "slug": "calc-differentiation",
                        "description": "Instantaneous rate of change, product rule, quotient rule, and multivariate chain rule.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Derivatives & The Chain Rule", "slug": "derivatives-and-chain-rule", "summary": "Analytical differentiation and composing multivariate functions.", "difficulty": "Beginner", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Multivariable Gradients & Optimization",
                        "slug": "calc-gradients-optimization",
                        "description": "Partial derivatives, Jacobian matrix, Hessian matrix, and critical points.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Gradients, Jacobians & Hessians", "slug": "gradients-jacobians-hessians", "summary": "Direction of steepest ascent, saddle points, and curvature tensors.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                ]
            }
        ]
    },
    {
        "category_slug": "mathematics",
        "name": "Numerical Methods",
        "slug": "numerical-methods",
        "short_description": "Root finding, numerical integration, differential equations, and floating point errors.",
        "description": "Numerical analysis for scientific computing: IEEE 754 floating point precision, root-finding (Newton-Raphson), interpolation, numerical quadrature, and Runge-Kutta ODE solvers.",
        "icon_key": "calculator",
        "difficulty_level": "Advanced",
        "display_order": 22,
        "courses": [
            {
                "title": "Numerical Methods & Scientific Computing",
                "slug": "numerical-methods-fundamentals",
                "description": "Iterative algorithms, error analysis, numerical differentiation, and matrix solvers.",
                "difficulty": "Advanced",
                "estimated_hours": 32,
                "modules": [
                    {
                        "title": "Root Finding & Non-linear Equations",
                        "slug": "num-root-finding",
                        "description": "Bisection method, secant method, and Newton-Raphson quadratic convergence.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Newton-Raphson & Fixed-Point Iteration", "slug": "newton-raphson-method", "summary": "Derivative-based root approximation and convergence guarantees.", "difficulty": "Intermediate", "estimated_minutes": 45},
                        ]
                    },
                    {
                        "title": "Numerical Integration & ODEs",
                        "slug": "num-integration-odes",
                        "description": "Trapezoidal rule, Simpson's 1/3 rule, and Euler/Runge-Kutta differential solvers.",
                        "estimated_minutes": 80,
                        "topics": [
                            {"title": "Runge-Kutta (RK4) Method", "slug": "runge-kutta-rk4-solver", "summary": "Fourth-order iterative stepping for initial value problems.", "difficulty": "Advanced", "estimated_minutes": 45},
                        ]
                    },
                ]
            }
        ]
    },
]

# ------------------------------------------------------------------------------
# 2. HIGH-QUALITY SEED LESSONS (Controlled Initial Subset)
# ------------------------------------------------------------------------------

SEED_LESSONS_DATA = [
    # 1. DSA — Complexity Analysis
    {
        "topic_slug": "asymptotic-notations",
        "title": "Foundations of Big-O Complexity",
        "slug": "foundations-of-big-o-complexity",
        "summary": "Understand asymptotic growth rates, worst-case upper bounds, and practical efficiency benchmarking.",
        "estimated_minutes": 20,
        "lesson_type": "theory",
        "learning_objectives": [
            "Define Big-O, Big-Omega, and Big-Theta notations rigorously",
            "Identify dominant polynomial and logarithmic terms as input size N grows",
            "Evaluate algorithmic code snippets for time and auxiliary space bounds"
        ],
        "content": """# Foundations of Big-O Complexity

## 1. What is Algorithmic Complexity?

When evaluating computer algorithms, measuring runtime in milliseconds or CPU clock cycles is unreliable because machine hardware, operating system scheduling, and compiler optimizations vary widely across environments.

**Asymptotic analysis** abstracts away hardware-dependent constants by evaluating how an algorithm's execution time and memory footprint scale as the input size $n$ approaches infinity.

---

## 2. The Three Asymptotic Notations

Mathematically, given functions $f(n)$ and $g(n)$:

1. **Big-O ($O$) — Asymptotic Upper Bound (Worst Case)**:
   $$f(n) = O(g(n)) \\iff \\exists c > 0, n_0 > 0 \\text{ such that } 0 \\le f(n) \\le c \\cdot g(n) \\; \\forall n \\ge n_0$$
   Big-O establishes a strict mathematical ceiling on resource consumption.

2. **Big-Omega ($\\Omega$) — Asymptotic Lower Bound (Best Case)**:
   $$f(n) = \\Omega(g(n)) \\iff \\exists c > 0, n_0 > 0 \\text{ such that } 0 \\le c \\cdot g(n) \\le f(n) \\; \\forall n \\ge n_0$$
   Big-Omega specifies the minimum resource investment required.

3. **Big-Theta ($\\Theta$) — Asymptotically Tight Bound (Average / Exact Order)**:
   $$f(n) = \\Theta(g(n)) \\iff f(n) = O(g(n)) \\text{ and } f(n) = \\Omega(g(n))$$
   The function is bounded both above and below within constant factors.

---

## 3. Hierarchy of Common Growth Rates

Ranked from fastest to slowest scaling:

| Notation | Complexity Name | Typical Example |
| :--- | :--- | :--- |
| $O(1)$ | Constant Time | Hash table lookup, array index lookup |
| $O(\\log n)$ | Logarithmic Time | Binary search on sorted array |
| $O(n)$ | Linear Time | Linear array traversal, single loop |
| $O(n \\log n)$ | Linearithmic Time | MergeSort, QuickSort (average case) |
| $O(n^2)$ | Quadratic Time | Nested loops (BubbleSort, Matrix mult naive) |
| $O(2^n)$ | Exponential Time | Naive recursive Fibonacci computation |
| $O(n!)$ | Factorial Time | Generating all permutations of an array |

---

## 4. Worked Code Example: Drop Non-Dominant Terms

```python
def analyze_data(arr: list[int]) -> int:
    n = len(arr)
    total = 0

    # Part 1: Linear Loop -> O(n)
    for num in arr:
        total += num

    # Part 2: Nested Quadratic Loops -> O(n^2)
    pairs_sum = 0
    for i in range(n):
        for j in range(n):
            pairs_sum += arr[i] * arr[j]

    # Overall Time Complexity: O(n + n^2) -> O(n^2)
    return total + pairs_sum
```

In the example above, while Part 1 takes $O(n)$ time, Part 2 scales as $O(n^2)$. Because $n^2$ outgrows $n$ for large values of $n$, the non-dominant term is dropped, yielding an overall worst-case complexity of **$O(n^2)$**.

---

## 5. Key Points to Remember

- Big-O measures the **growth rate of resource consumption**, not absolute clock time.
- Always drop constant multipliers: $O(3n + 5)$ simplifies to $O(n)$.
- Always drop non-dominant polynomial components: $O(n^3 + 100n^2 + 500)$ simplifies to $O(n^3)$.
- Auxiliary space complexity measures only additional memory allocated by the algorithm, excluding the initial input array itself.
"""
    },
    # 2. DSA — Arrays
    {
        "topic_slug": "static-vs-dynamic-arrays",
        "title": "Array Memory Layout and Operations",
        "slug": "array-memory-layout-and-operations",
        "summary": "Examine contiguous physical RAM layouts, pointer arithmetic, and amortized resizing in dynamic arrays.",
        "estimated_minutes": 25,
        "lesson_type": "theory",
        "learning_objectives": [
            "Explain contiguous memory allocation and zero-indexed pointer arithmetic",
            "Calculate memory addresses using base address and element byte sizes",
            "Understand why append operations in dynamic arrays achieve O(1) amortized time"
        ],
        "content": """# Array Memory Layout and Operations

## 1. Physical Representation in RAM

An **array** is a linear data structure storing elements of uniform type in a single contiguous block of physical memory.

Because all elements are stored adjacent to one another in physical RAM, any element can be accessed in **$O(1)$ constant time** using direct pointer arithmetic:

$$\\text{Address}(A[i]) = \\text{BaseAddress} + (i \\times \\text{ElementSizeInBytes})$$

For example, if a 32-bit integer (4 bytes) array begins at base address `0x1000`, the element at index `3` resides at:
$$\\text{Address}(A[3]) = 0x1000 + (3 \\times 4) = 0x100C$$

---

## 2. Static vs Dynamic Arrays

- **Static Arrays**: Fixed capacity defined at allocation time. Resizing requires allocating a brand new memory buffer and manually copying elements.
- **Dynamic Arrays** (e.g., Python `list`, C++ `std::vector`, Java `ArrayList`): Automatically expand capacity when full by allocating a new block (typically $1.5\\times$ to $2\\times$ the previous size) and transferring elements.

---

## 3. Time Complexity Summary of Array Operations

| Operation | Time Complexity | Explanation |
| :--- | :--- | :--- |
| **Random Access** (`arr[i]`) | $O(1)$ | Direct pointer arithmetic calculation |
| **Search (Unsorted)** | $O(n)$ | Must scan elements sequentially |
| **Search (Sorted)** | $O(\\log n)$ | Binary search halving the search space |
| **Append (End)** | $O(1)$ Amortized | Appends in constant time unless full |
| **Insertion (Index `k`)** | $O(n)$ | Requires shifting all elements after `k` rightward |
| **Deletion (Index `k`)** | $O(n)$ | Requires shifting all elements after `k` leftward |

---

## 4. Code Demonstration: Memory Resizing in Dynamic Arrays

```python
import sys

# Observe dynamic capacity growth in Python's list implementation
dynamic_list = []
last_size = sys.getsizeof(dynamic_list)

print(f"Initial empty list byte size: {last_size} bytes")

for i in range(20):
    dynamic_list.append(i)
    current_size = sys.getsizeof(dynamic_list)
    if current_size != last_size:
        print(f"Resized at element count {len(dynamic_list)}: {last_size} -> {current_size} bytes")
        last_size = current_size
```

---

## 5. Key Points to Remember

- Arrays provide unbeatable $O(1)$ random access speed due to contiguous hardware spatial locality and CPU L1/L2 cache prefetching.
- Insertions and deletions in the middle or beginning incur an expensive $O(n)$ shift overhead.
- Dynamic array resizing doubles capacity geometrically, guaranteeing an average amortized append cost of $O(1)$.
"""
    },
    # 3. DSA — Linked Lists
    {
        "topic_slug": "singly-doubly-linked-lists",
        "title": "Singly Linked List Implementation and Pointer Traversal",
        "slug": "singly-linked-list-implementation",
        "summary": "Construct node structures with dynamic pointers, implement head/tail insertions, and avoid memory traps.",
        "estimated_minutes": 25,
        "lesson_type": "theory",
        "learning_objectives": [
            "Construct a node class encapsulating data values and next pointers",
            "Implement O(1) head insertion and O(n) traversal operations",
            "Differentiate linked lists from contiguous arrays regarding memory overhead"
        ],
        "content": """# Singly Linked List Implementation and Pointer Traversal

## 1. Core Architecture

Unlike arrays, a **linked list** does not require contiguous blocks of memory. Each element (called a **Node**) is allocated independently on the heap and contains:
1. **Data payload**: The stored value.
2. **Next pointer (`next`)**: A memory reference pointing to the subsequent node in the chain.

The entry point of the list is called the **Head**. The last node in the chain points to `None` (or `NULL`), designating the end of the sequence.

---

## 2. Structural Comparison: Array vs Linked List

| Characteristic | Array | Singly Linked List |
| :--- | :--- | :--- |
| **Memory Allocation** | Contiguous chunk | Dispersed heap nodes |
| **Random Access** | $O(1)$ via index | $O(n)$ traversal required |
| **Insertion at Head** | $O(n)$ shifting cost | $O(1)$ pointer update |
| **Insertion at Tail** | $O(1)$ amortized | $O(1)$ with tail pointer; $O(n)$ without |
| **Memory Overhead** | Low (data only) | Higher (extra pointer per node) |

---

## 3. Python Node and LinkedList Implementation

```python
class Node:
    # Single node storing data and a reference to the next node.
    def __init__(self, value: int):
        self.value = value
        self.next = None


class SinglyLinkedList:
    def __init__(self):
        self.head = None

    def insert_at_head(self, value: int) -> None:
        # O(1) operation: insert new value at front of list.
        new_node = Node(value)
        new_node.next = self.head
        self.head = new_node

    def search(self, target: int) -> bool:
        # O(n) operation: sequentially traverse pointer chain.
        current = self.head
        while current is not None:
            if current.value == target:
                return True
            current = current.next
        return False
```

---

## 4. Key Points to Remember

- Linked lists excel at frequent insertions and deletions at the list boundary ($O(1)$ when pointing to the target node).
- Linked lists do NOT support constant-time random indexing ($arr[i]$) because each pointer must be traversed sequentially from the head node.
- Each node consumes additional memory to store pointer references (4 or 8 bytes per reference depending on 32-bit or 64-bit architecture).
"""
    },

    # 4. DBMS — Relational Model
    {
        "topic_slug": "relational-model-tuple-algebra",
        "title": "Relational Data Model & Tuple Algebra",
        "slug": "relational-data-model-and-tuples",
        "summary": "Understand Edgar Codd's formal mathematical relation concepts, attributes, domains, and relational algebra.",
        "estimated_minutes": 25,
        "lesson_type": "theory",
        "learning_objectives": [
            "Define relations, tuples, domains, and degree versus cardinality",
            "Apply fundamental relational algebra operators: Selection, Projection, Cartesian Product",
            "Understand declarative relational integrity constraints"
        ],
        "content": """# Relational Data Model & Tuple Algebra

## 1. Mathematical Foundation

Proposed by Edgar F. Codd in 1970, the **relational model** represents data as mathematical relations.

A **relation** is a set of unordered **tuples** (rows) conforming to a strict schema of **attributes** (columns):
- **Domain**: The set of permissible atomic values for an attribute.
- **Degree (Arity)**: The total number of attributes (columns) in the relation.
- **Cardinality**: The total number of tuples (rows) currently stored in the relation.

---

## 2. Fundamental Relational Algebra Operators

Relational algebra is a procedural query language consisting of operations that take one or more relations as input and produce a new relation as output:

1. **Selection ($\\sigma$)**: Filters rows satisfying a predicate:
   $$\\sigma_{\\text{age} \\ge 18}(\\text{Students})$$

2. **Projection ($\\pi$)**: Filters specific columns, discarding unselected attributes and eliminating duplicate rows:
   $$\\pi_{\\text{name, email}}(\\text{Students})$$

3. **Cartesian Product ($\\times$)**: Combines every tuple in relation $R$ with every tuple in relation $S$:
   $$\\text{Students} \\times \\text{Courses}$$

4. **Union ($\\cup$)**: Combines tuples from two union-compatible relations.

5. **Set Difference ($-$)**: Identifies tuples present in relation $R$ but absent in relation $S$.

---

## 3. Relational Invariants

- **First Normal Form (1NF) / Atomicity**: Attribute values must be atomic (indivisible). Multi-valued sets or nested tables are forbidden.
- **No Duplicate Tuples**: Because a relation is formally a mathematical set, duplicate tuples cannot exist (enforced by candidate keys).
- **Attribute Order Independence**: Attributes and tuples have no defined physical sequence.

---

## 4. Key Points to Remember

- Relations represent mathematical sets of tuples, meaning ordering is meaningless and duplicate rows are prohibited.
- Relational algebra forms the underlying theoretical execution plan that SQL queries are compiled and optimized into.
"""
    },
    # 5. DBMS — Keys
    {
        "topic_slug": "key-types-and-constraints",
        "title": "Database Keys & Referential Integrity Constraints",
        "slug": "database-keys-and-referential-integrity",
        "summary": "Differentiate superkeys, candidate keys, primary keys, and foreign key cascading constraints.",
        "estimated_minutes": 25,
        "lesson_type": "theory",
        "learning_objectives": [
            "Distinguish between Superkey, Candidate Key, and Primary Key",
            "Understand Foreign Key referential integrity rules and CASCADE/SET NULL actions",
            "Evaluate composite keys for relational schemas"
        ],
        "content": """# Database Keys & Referential Integrity Constraints

## 1. Hierarchy of Relational Keys

In relational databases, **keys** are attribute subsets used to uniquely identify tuples and establish relationships across tables:

1. **Superkey**: Any set of attributes that uniquely identifies a row in a relation.
2. **Candidate Key**: A **minimal** superkey. No proper subset of a candidate key can uniquely identify a tuple.
3. **Primary Key**: The specific candidate key chosen by the database designer to serve as the default unique identifier. Primary keys **must not contain NULL values**.
4. **Alternate (Secondary) Key**: Any candidate key that was not selected as the primary key.
5. **Foreign Key**: An attribute in table $A$ that references the primary key of table $B$, linking related entities.

---

## 2. Referential Integrity Constraints

A **referential integrity constraint** dictates that if a table contains a foreign key, the value in that column must either:
1. Match a valid, existing primary key value in the referenced parent table, OR
2. Be `NULL` (if the foreign key column is defined as nullable).

### Cascading Delete & Update Options:
- `ON DELETE CASCADE`: Deleting a parent row automatically deletes all matching child rows.
- `ON DELETE SET NULL`: Deleting a parent row updates child foreign key values to `NULL`.
- `ON DELETE RESTRICT` / `NO ACTION`: Aborts the parent deletion if matching child rows exist.

---

## 3. SQL Key Syntax Example

```sql
CREATE TABLE departments (
    dept_id UUID PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE employees (
    emp_id UUID PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    dept_id UUID,
    CONSTRAINT fk_employee_department
        FOREIGN KEY (dept_id)
        REFERENCES departments(dept_id)
        ON DELETE SET NULL
);
```

---

## 4. Key Points to Remember

- A Primary Key must be both **unique** and **non-nullable**.
- Every Candidate Key is a Superkey, but not every Superkey is a Candidate Key (because superkeys can contain redundant attributes).
- Foreign keys maintain mathematical consistency between relational tables, preventing orphaned child records.
"""
    },
    # 6. DBMS — SQL Basics
    {
        "topic_slug": "declarative-sql-queries",
        "title": "Declarative SQL Queries, Filtering, and Grouping",
        "slug": "declarative-sql-queries-filtering-grouping",
        "summary": "Master the logical execution order of SQL queries, WHERE vs HAVING clauses, and aggregate functions.",
        "estimated_minutes": 25,
        "lesson_type": "theory",
        "learning_objectives": [
            "Contrast declarative SQL execution with procedural programming logic",
            "Trace the exact logical execution sequence of SQL clauses",
            "Differentiate row filtering (WHERE) from group aggregation filtering (HAVING)"
        ],
        "content": """# Declarative SQL Queries, Filtering, and Grouping

## 1. Declarative Programming Paradigm

SQL (Structured Query Language) is a **declarative language**: you specify **what data** you want to retrieve, not **how to physically navigate the disk** to retrieve it. The DBMS query optimizer translates declarative SQL into an optimized physical relational algebra execution plan.

---

## 2. Logical Execution Order of a SQL Query

Although queries are written starting with `SELECT`, the database engine processes clauses in this sequence:

1. **`FROM` / `JOIN`**: Determine and combine source tables.
2. **`WHERE`**: Filter raw individual rows before any grouping occurs.
3. **`GROUP BY`**: Aggregate remaining rows into groups sharing identical values.
4. **`HAVING`**: Filter the aggregated groups using aggregate conditions.
5. **`SELECT`**: Project the requested columns and compute expressions.
6. **`DISTINCT`**: Remove duplicate output rows.
7. **`ORDER BY`**: Sort final result rows.
8. **`LIMIT` / `OFFSET`**: Restrict the count of returned tuples.

---

## 3. `WHERE` vs `HAVING` Difference

- **`WHERE` clause**: Filters individual tuples *before* aggregation. Cannot reference aggregate functions like `COUNT()`, `AVG()`, or `SUM()`.
- **`HAVING` clause**: Filters entire groups *after* aggregation. Designed specifically to evaluate aggregate conditions.

```sql
SELECT 
    dept_id,
    COUNT(emp_id) AS total_employees,
    AVG(salary) AS avg_salary
FROM employees
WHERE is_active = TRUE               -- Row-level filter: only active staff
GROUP BY dept_id                     -- Group rows by department
HAVING COUNT(emp_id) >= 5            -- Group-level filter: only large depts
ORDER BY avg_salary DESC;            -- Sort output
```

---

## 4. Key Points to Remember

- The `SELECT` statement is executed near the end of the query lifecycle, which is why column aliases defined in `SELECT` cannot be used inside `WHERE` clauses.
- Aggregate functions collapse multiple rows into a single summary value per group.
"""
    },

    # 7. Operating Systems — Processes
    {
        "topic_slug": "process-control-block-lifecycle",
        "title": "Process Control Block & Lifecycle States",
        "slug": "process-control-block-and-lifecycle",
        "summary": "Inspect process state diagrams, the Process Control Block (PCB), and context switching overhead.",
        "estimated_minutes": 25,
        "lesson_type": "theory",
        "learning_objectives": [
            "Draw and explain the 5-state process lifecycle model",
            "Identify the critical fields stored within a Process Control Block (PCB)",
            "Analyze the hardware context switch sequence and associated CPU cache invalidation"
        ],
        "content": """# Process Control Block & Lifecycle States

## 1. What is a Process?

A **program** is a passive collection of machine instructions stored on disk (e.g., an executable binary file). A **process** is an active program in execution, complete with:
- **Text Section**: The compiled executable code.
- **Data Section**: Global and static variables.
- **Heap**: Dynamically allocated memory at runtime (`malloc`, `new`).
- **Stack**: Activation call frames storing local variables and return addresses.
- **Program Counter (PC)**: Register pointing to the next instruction to execute.

---

## 2. The 5-State Process Model

```
   [New] ──> [Ready] <───(Interrupt / Preemption)─── [Running] ──> [Terminated]
               ^                                       │
               │                                       ▼
               └────────── [Waiting / Blocked] <───────┘
                              (I/O or Event)
```

1. **New**: The process is being created and loaded into memory.
2. **Ready**: The process is loaded in memory waiting for CPU allocation by the scheduler.
3. **Running**: Instructions are actively being executed on the CPU core.
4. **Waiting (Blocked)**: The process cannot proceed until an I/O event or signal completes.
5. **Terminated**: The process has finished execution and OS resources are reclaimed.

---

## 3. The Process Control Block (PCB)

The OS kernel maintains a data structure called the **PCB (Process Control Block)** for every active process:
- **Process ID (PID)**: Unique integer identifier.
- **Process State**: Current state (Ready, Running, Blocked, etc.).
- **Program Counter**: Memory address of next instruction.
- **CPU Registers**: Accumulators, index registers, stack pointer saved during interrupts.
- **Memory Management Information**: Base/limit registers or page tables.
- **Accounting & I/O Status**: CPU time consumed, open file descriptor tables.

---

## 4. Context Switch Overhead

When the CPU switches from Process $P_1$ to Process $P_2$:
1. The kernel saves $P_1$'s registers and state into $P_1$'s PCB.
2. The kernel updates $P_1$'s state (e.g., to Ready or Waiting).
3. The scheduler selects $P_2$.
4. The kernel restores $P_2$'s registers from $P_2$'s PCB.
5. The CPU resumes execution of $P_2$ at its saved Program Counter.

**Context switching is pure overhead**: the CPU performs no productive user computation while switching. Furthermore, the CPU L1/L2 hardware caches are often invalidated, causing cache misses on the new process.

---

## 5. Key Points to Remember

- A process is a program in execution with isolated virtual address space.
- The PCB stores all state required to pause and resume a process transparently.
- Context switches introduce non-trivial latency and hardware cache penalties.
"""
    },
    # 8. Operating Systems — Threads
    {
        "topic_slug": "kernel-vs-user-threads",
        "title": "Kernel vs User Threads and Concurrency Models",
        "slug": "kernel-vs-user-threads-concurrency",
        "summary": "Compare user-space green threads with kernel threads and explore multi-threading models.",
        "estimated_minutes": 25,
        "lesson_type": "theory",
        "learning_objectives": [
            "Differentiate heavy processes from lightweight threads",
            "Contrast User-Level Threads (ULT) with Kernel-Level Threads (KLT)",
            "Compare the Many-to-One, One-to-One, and Many-to-Many threading models"
        ],
        "content": """# Kernel vs User Threads and Concurrency Models

## 1. Process vs Thread

A **thread** (often called a lightweight process) is the smallest sequence of programmed instructions that can be managed independently by a scheduler.

Within a single process, multiple threads **share**:
- Text (code) section
- Data section (global variables)
- Heap (dynamically allocated memory)
- Operating system resources (open files, sockets)

However, each thread maintains its own **private**:
- Thread ID (TID)
- Program Counter (PC)
- CPU register set
- Private call stack (for local function variables)

---

## 2. User-Level Threads (ULT) vs Kernel-Level Threads (KLT)

### User-Level Threads (ULT):
- Managed completely by user-space runtime libraries without kernel awareness.
- **Advantage**: Fast thread creation and switching (no kernel mode trap required).
- **Disadvantage**: If one thread performs a blocking system call (e.g., disk I/O), the **entire process** blocks because the kernel sees only one process.

### Kernel-Level Threads (KLT):
- Directly supported and scheduled by the operating system kernel.
- **Advantage**: True parallelism across multiple CPU cores; one thread blocking on I/O does not block sibling threads.
- **Disadvantage**: Thread creation and context switches require kernel context transitions (`sysenter`/`sysexit`), adding overhead.

---

## 3. Multi-Threading Models

1. **Many-to-One (Green Threads)**: Many user threads map to a single kernel thread. No true multicore execution.
2. **One-to-One (Standard in Modern Linux / Windows)**: Every user thread maps directly to a distinct kernel thread. True multicore parallel execution.
3. **Many-to-Many (Hybrid)**: Multiplexes many user-level threads onto a smaller or equal number of kernel threads.

---

## 4. Key Points to Remember

- Threads within the same process share heap and global variables, making communication fast but creating race condition risks.
- Modern OS platforms (Linux via NPTL, Windows) implement the **One-to-One model**, allowing threads to utilize multiple CPU cores concurrently.
"""
    },
    # 9. Operating Systems — CPU Scheduling
    {
        "topic_slug": "preemptive-scheduling-algorithms",
        "title": "Preemptive and Non-Preemptive CPU Scheduling Algorithms",
        "slug": "cpu-scheduling-algorithms-round-robin",
        "summary": "Calculate turnaround and waiting times for FCFS, SJF, SRTF, and Round Robin scheduling.",
        "estimated_minutes": 25,
        "lesson_type": "theory",
        "learning_objectives": [
            "Distinguish between non-preemptive and preemptive scheduling",
            "Calculate average turnaround time and average waiting time using Gantt charts",
            "Analyze Round Robin behavior under varying time quantum lengths"
        ],
        "content": """# Preemptive and Non-Preemptive CPU Scheduling Algorithms

## 1. Core Scheduling Objectives

The CPU scheduler determines which ready process is assigned to an idle CPU core. Its goal is to optimize:
- **CPU Utilization**: Percentage of time the CPU is actively executing tasks.
- **Throughput**: Number of completed processes per unit of time.
- **Turnaround Time ($TAT$)**: Total elapsed time from process submission to termination:
  $$TAT = \\text{Completion Time} - \\text{Arrival Time}$$
- **Waiting Time ($WT$)**: Total time spent waiting in the ready queue:
  $$WT = TAT - \\text{Burst Time}$$
- **Response Time**: Time from submission until the first output/response is produced.

---

## 2. Common Scheduling Algorithms

### 1. First-Come, First-Served (FCFS)
- Non-preemptive. Simple FIFO queue.
- Suffers from the **convoy effect**: short processes get trapped waiting behind a massive CPU-bound process.

### 2. Shortest Job First (SJF)
- Assigns CPU to the process with the shortest CPU burst.
- Mathematically optimal for minimizing average waiting time.
- Impractical for general OS kernels because upcoming burst durations cannot be known in advance.

### 3. Shortest Remaining Time First (SRTF)
- Preemptive version of SJF. If a newly arrived process has a burst shorter than the currently running process's remaining time, the running process is preempted.

### 4. Round Robin (RR)
- Designed for time-sharing systems.
- Every process receives a fixed slice of CPU time called a **time quantum** (typically 10–100 ms).
- If the process does not complete within the quantum, it is preempted and returned to the tail of the ready queue.

---

## 3. The Time Quantum Dilemma in Round Robin

- If the quantum is **infinitely large**: Round Robin degrades into non-preemptive FCFS.
- If the quantum is **infinitesimally small**: Round Robin creates severe context-switch overhead, wasting CPU cycles on state saving/restoring.
- **Rule of Thumb**: Set the quantum such that roughly 80% of typical CPU bursts are shorter than the quantum.

---

## 4. Key Points to Remember

- Preemptive algorithms can interrupt a running process mid-execution; non-preemptive algorithms allow a process to run until it yields or terminates.
- Round Robin guarantees starvation-free execution and responsive interactive computing at the cost of context switch overhead.
"""
    },

    # 10. Python — Variables & Data Types
    {
        "topic_slug": "python-variables-data-types",
        "title": "Python Memory Model, Dynamic Typing & Primitive Types",
        "slug": "python-memory-model-dynamic-typing",
        "summary": "Explore Python's object model, reference counts, mutability differences, and primitive types.",
        "estimated_minutes": 20,
        "lesson_type": "theory",
        "learning_objectives": [
            "Explain Python's 'everything is an object' paradigm and PyObject memory headers",
            "Differentiate mutable collections from immutable primitives",
            "Predict variable assignment behavior using identity checks (`id()` and `is`)"
        ],
        "content": """# Python Memory Model, Dynamic Typing & Primitive Types

## 1. Everything is an Object

In Python, variables do not hold values directly. Instead, variables are **names (pointers/references)** bound to objects residing on the heap.

Every Python object contains a C-level header structure (`PyObject`) storing:
1. **Reference count**: Number of active variables pointing to this object.
2. **Type pointer (`ob_type`)**: Pointer to the object's type descriptor (e.g., `<class 'int'>`).
3. **Value / payload**: The actual data stored.

```python
x = 42
# 'x' is simply a name bound to an integer object with value 42.
```

---

## 2. Mutability vs Immutability

Python data types fall strictly into two categories:

| Category | Types | Behavior |
| :--- | :--- | :--- |
| **Immutable** | `int`, `float`, `bool`, `str`, `tuple`, `frozenset` | Value cannot be modified in-place; modifications create a new object |
| **Mutable** | `list`, `dict`, `set`, custom user classes | Value can be altered in-place without changing object identity |

### Mutability Pitfall Example:
```python
# Immutable strings
s = "lumina"
s_id_before = id(s)
s += "learn"
s_id_after = id(s)
print(s_id_before == s_id_after)  # False: A new string object was created

# Mutable lists
lst = [1, 2, 3]
lst_id_before = id(lst)
lst.append(4)
lst_id_after = id(lst)
print(lst_id_before == lst_id_after)  # True: Mutated in-place
```

---

## 3. The `==` vs `is` Operator

- **`==` (Value Equality)**: Evaluates whether two objects contain the same data by invoking `__eq__()`.
- **`is` (Identity Equality)**: Evaluates whether two references point to the exact same physical memory address (`id(a) == id(b)`).

```python
a = [1, 2, 3]
b = [1, 2, 3]

print(a == b)  # True: Same values
print(a is b)  # False: Different heap allocations
```

---

## 4. Key Points to Remember

- Python uses **dynamic typing**: variable types are checked at runtime, not compile-time.
- Integers, floats, strings, and tuples are immutable; modifying them always allocates a new object in memory.
- Default mutable argument values in functions (e.g., `def fn(items=[]):`) persist across invocations and should be avoided.
"""
    },
    # 11. Python — Control Flow
    {
        "topic_slug": "python-conditionals-and-loops",
        "title": "Conditional Branching and Iteration Mechanisms",
        "slug": "conditional-branching-and-iteration",
        "summary": "Understand Python truthy/falsy semantics, short-circuit boolean evaluation, and for-else loops.",
        "estimated_minutes": 20,
        "lesson_type": "theory",
        "learning_objectives": [
            "Evaluate truthiness of empty collections, zeros, and None",
            "Utilize short-circuit evaluation in boolean expressions",
            "Implement for-else search patterns effectively"
        ],
        "content": """# Conditional Branching and Iteration Mechanisms

## 1. Truth Value Testing (Truthy & Falsy)

In Python, every object has an inherent boolean truth value.

The following values evaluate to **Falsy**:
- Constants: `None`, `False`
- Numeric zeros: `0`, `0.0`, `0j`
- Empty sequences and collections: `""`, `()`, `[]`, `{}`, `set()`

Everything else evaluates to **Truthy** by default.

```python
users = []
if not users:
    print("No users found.")  # Idiomatic Python check instead of len(users) == 0
```

---

## 2. Short-Circuit Evaluation

Logical operators `and` and `or` use short-circuit evaluation and return the actual operand value, not just a plain boolean:
- **`A and B`**: Returns $A$ if $A$ is falsy; otherwise returns $B$.
- **`A or B`**: Returns $A$ if $A$ is truthy; otherwise returns $B$.

```python
# Provide default fallback value
display_name = user_input or "Anonymous Student"
```

---

## 3. The `for...else` Loop Construct

Python possesses a unique `else` block on loops. The `else` block executes **only if the loop completed naturally** without encountering a `break` statement:

```python
def find_prime(numbers: list[int]) -> int | None:
    for n in numbers:
        if n > 1 and all(n % i != 0 for i in range(2, int(n**0.5) + 1)):
            print(f"Found prime: {n}")
            break
    else:
        print("No prime number was found in the sequence.")
        return None
```

---

## 4. Key Points to Remember

- Rely on implicit truthiness testing (`if items:`) rather than comparing lengths (`if len(items) > 0:`).
- `for...else` blocks eliminate the need for boolean flag variables when searching through sequences.
"""
    },
    # 12. Python — Functions
    {
        "topic_slug": "python-defining-functions-scope",
        "title": "Function Signatures, Scope Resolution & First-Class Functions",
        "slug": "functions-scope-and-closures",
        "summary": "Master the LEGB scoping rule, *args/**kwargs parameter binding, closures, and higher-order functions.",
        "estimated_minutes": 25,
        "lesson_type": "theory",
        "learning_objectives": [
            "Trace variable resolution using the LEGB (Local, Enclosing, Global, Built-in) rule",
            "Construct flexible signatures using *args and **kwargs",
            "Build closures and understand higher-order functions"
        ],
        "content": """# Function Signatures, Scope Resolution & First-Class Functions

## 1. First-Class Functions

In Python, functions are **first-class citizens**:
- Functions can be assigned to variables.
- Functions can be passed as arguments into other functions.
- Functions can be returned from other functions.

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

say_hi = greet  # Function assigned to variable
print(say_hi("Alice"))
```

---

## 2. Variable Scope and the LEGB Rule

When Python resolves a variable name, it searches four scopes sequentially:

1. **L — Local**: Names assigned inside the current function body.
2. **E — Enclosing**: Names defined in outer enclosing functions (closures).
3. **G — Global**: Names defined at the top level of the current module.
4. **B — Built-in**: Names preloaded into Python (e.g., `len`, `range`, `print`).

If a variable is not found in any of the four scopes, a `NameError` is raised.

---

## 3. Closures and Function Factories

A **closure** occurs when a nested function retains access to variables in its enclosing scope even after the outer function has finished executing:

```python
def make_multiplier(factor: int):
    # Enclosing scope variable: factor
    def multiply(n: int) -> int:
        return n * factor  # 'factor' is captured by the closure
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))  # Outputs: 10
print(triple(5))  # Outputs: 15
```

---

## 4. Variadic Arguments (`*args` and `**kwargs`)

- `*args`: Collects extra positional arguments into an immutable `tuple`.
- `**kwargs`: Collects extra keyword arguments into a mutable `dict`.

```python
def configure_agent(agent_name: str, *tags: str, **settings: int | str):
    print(f"Agent: {agent_name}")
    print(f"Tags tuple: {tags}")
    print(f"Settings dict: {settings}")

configure_agent("Socrates", "ai", "tutor", temperature=0.7, max_tokens=500)
```

---

## 5. Key Points to Remember

- The LEGB rule guarantees deterministic variable lookup order from innermost to outermost scope.
- Use `global` and `nonlocal` sparingly, as mutability across scopes makes code harder to reason about and test.
- Closures form the underlying mechanics of Python **decorators**.
"""
    }
]


# ------------------------------------------------------------------------------
# 3. IDEMPOTENT DATABASE SEEDING ENGINE
# ------------------------------------------------------------------------------

async def seed_academic_content(db: AsyncSession) -> dict[str, int]:
    """
    Idempotent content seeder populating Categories, Subjects, Courses,
    Modules, Topics, and Lessons.
    """
    stats = {
        "categories_created": 0,
        "categories_skipped": 0,
        "subjects_created": 0,
        "subjects_skipped": 0,
        "courses_created": 0,
        "courses_skipped": 0,
        "modules_created": 0,
        "modules_skipped": 0,
        "topics_created": 0,
        "topics_skipped": 0,
        "lessons_created": 0,
        "lessons_skipped": 0,
    }

    # 1. Seed Categories
    category_map: dict[str, ContentCategory] = {}
    for cat_data in CATEGORIES_DATA:
        stmt = select(ContentCategory).where(ContentCategory.slug == cat_data["slug"])
        existing = (await db.execute(stmt)).scalars().first()

        if existing:
            category_map[cat_data["slug"]] = existing
            stats["categories_skipped"] += 1
        else:
            category = ContentCategory(
                id=uuid.uuid4(),
                name=cat_data["name"],
                slug=cat_data["slug"],
                description=cat_data["description"],
                display_order=cat_data["display_order"],
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(category)
            await db.flush()
            category_map[cat_data["slug"]] = category
            stats["categories_created"] += 1

    # 2. Seed Subjects, Courses, Modules, Topics
    subject_map: dict[str, Subject] = {}
    topic_map: dict[str, Topic] = {}

    for sub_data in SUBJECTS_CATALOG:
        cat = category_map[sub_data["category_slug"]]
        
        # Check Subject by slug
        stmt = select(Subject).where(Subject.slug == sub_data["slug"])
        existing_sub = (await db.execute(stmt)).scalars().first()

        if existing_sub:
            subject = existing_sub
            subject_map[sub_data["slug"]] = subject
            stats["subjects_skipped"] += 1
        else:
            subject = Subject(
                id=uuid.uuid4(),
                category_id=cat.id,
                name=sub_data["name"],
                slug=sub_data["slug"],
                short_description=sub_data["short_description"],
                description=sub_data["description"],
                icon_key=sub_data.get("icon_key", "book"),
                difficulty_level=sub_data.get("difficulty_level", "All Levels"),
                display_order=sub_data["display_order"],
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(subject)
            await db.flush()
            subject_map[sub_data["slug"]] = subject
            stats["subjects_created"] += 1

        # Seed Courses for Subject
        for c_order, course_data in enumerate(sub_data.get("courses", []), start=1):
            stmt = select(Course).where(
                Course.subject_id == subject.id,
                Course.slug == course_data["slug"]
            )
            existing_course = (await db.execute(stmt)).scalars().first()

            if existing_course:
                course = existing_course
                stats["courses_skipped"] += 1
            else:
                course = Course(
                    id=uuid.uuid4(),
                    subject_id=subject.id,
                    title=course_data["title"],
                    slug=course_data["slug"],
                    description=course_data["description"],
                    difficulty=course_data.get("difficulty", "Beginner"),
                    estimated_hours=course_data.get("estimated_hours", 10),
                    display_order=c_order,
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                db.add(course)
                await db.flush()
                stats["courses_created"] += 1

            # Seed Modules for Course
            for m_order, mod_data in enumerate(course_data.get("modules", []), start=1):
                stmt = select(Module).where(
                    Module.course_id == course.id,
                    Module.slug == mod_data["slug"]
                )
                existing_module = (await db.execute(stmt)).scalars().first()

                if existing_module:
                    module = existing_module
                    stats["modules_skipped"] += 1
                else:
                    module = Module(
                        id=uuid.uuid4(),
                        course_id=course.id,
                        title=mod_data["title"],
                        slug=mod_data["slug"],
                        description=mod_data["description"],
                        estimated_minutes=mod_data.get("estimated_minutes", 60),
                        display_order=m_order,
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc),
                    )
                    db.add(module)
                    await db.flush()
                    stats["modules_created"] += 1

                # Seed Topics for Module
                for t_order, top_data in enumerate(mod_data.get("topics", []), start=1):
                    stmt = select(Topic).where(
                        Topic.module_id == module.id,
                        Topic.slug == top_data["slug"]
                    )
                    existing_topic = (await db.execute(stmt)).scalars().first()

                    if existing_topic:
                        topic = existing_topic
                        topic_map[top_data["slug"]] = topic
                        stats["topics_skipped"] += 1
                    else:
                        topic = Topic(
                            id=uuid.uuid4(),
                            module_id=module.id,
                            title=top_data["title"],
                            slug=top_data["slug"],
                            summary=top_data.get("summary", ""),
                            estimated_minutes=top_data.get("estimated_minutes", 30),
                            difficulty=top_data.get("difficulty", "Beginner"),
                            display_order=t_order,
                            created_at=datetime.now(timezone.utc),
                            updated_at=datetime.now(timezone.utc),
                        )
                        db.add(topic)
                        await db.flush()
                        topic_map[top_data["slug"]] = topic
                        stats["topics_created"] += 1

    # 3. Seed High-Quality Controlled Initial Lessons
    for l_order, lesson_data in enumerate(SEED_LESSONS_DATA, start=1):
        target_topic = topic_map.get(lesson_data["topic_slug"])
        if not target_topic:
            # Fallback lookup from DB if already existed
            stmt = select(Topic).where(Topic.slug == lesson_data["topic_slug"])
            target_topic = (await db.execute(stmt)).scalars().first()
            if target_topic:
                topic_map[lesson_data["topic_slug"]] = target_topic

        if not target_topic:
            print(f"[WARN] Target topic '{lesson_data['topic_slug']}' not found. Skipping lesson '{lesson_data['title']}'.")
            continue

        stmt = select(Lesson).where(
            Lesson.topic_id == target_topic.id,
            Lesson.slug == lesson_data["slug"]
        )
        existing_lesson = (await db.execute(stmt)).scalars().first()

        if existing_lesson:
            stats["lessons_skipped"] += 1
        else:
            lesson = Lesson(
                id=uuid.uuid4(),
                topic_id=target_topic.id,
                title=lesson_data["title"],
                slug=lesson_data["slug"],
                summary=lesson_data["summary"],
                content=lesson_data["content"],
                learning_objectives=lesson_data["learning_objectives"],
                estimated_minutes=lesson_data["estimated_minutes"],
                display_order=l_order,
                lesson_type=lesson_data["lesson_type"],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(lesson)
            await db.flush()
            stats["lessons_created"] += 1

    await db.commit()
    return stats


async def main() -> None:
    print("[INIT] Initializing LuminaLearn Academic Content Engine Seeder...")
    await init_db()

    async with AsyncSessionLocal() as session:
        stats = await seed_academic_content(session)

    print("\n" + "=" * 60)
    print("[SUMMARY] ACADEMIC CONTENT SEEDING COMPLETE")
    print("=" * 60)
    print(f"Categories Created : {stats['categories_created']:>4} | Skipped: {stats['categories_skipped']:>4}")
    print(f"Subjects Created   : {stats['subjects_created']:>4} | Skipped: {stats['subjects_skipped']:>4}")
    print(f"Courses Created    : {stats['courses_created']:>4} | Skipped: {stats['courses_skipped']:>4}")
    print(f"Modules Created    : {stats['modules_created']:>4} | Skipped: {stats['modules_skipped']:>4}")
    print(f"Topics Created     : {stats['topics_created']:>4} | Skipped: {stats['topics_skipped']:>4}")
    print(f"Lessons Created    : {stats['lessons_created']:>4} | Skipped: {stats['lessons_skipped']:>4}")
    print("=" * 60)



if __name__ == "__main__":
    asyncio.run(main())
