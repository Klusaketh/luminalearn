---
lesson: access-control-os-security
title: Access Control and OS Security Fundamentals
summary: How operating systems decide who may do what - protection domains, the access matrix, ACLs and capabilities, UNIX permissions, discretionary and mandatory access control - and the common attacks and defences every system must handle.
minutes: 45
type: theory
objectives:
  - Distinguish protection from security and apply the principles of least privilege, complete mediation, and fail-safe defaults
  - Model rights with an access matrix and compare its implementation as access control lists and as capability lists
  - Interpret UNIX permission bits, including setuid and the sticky bit, and evaluate an access request
  - Describe common attack classes, such as buffer overflows, privilege escalation, and TOCTOU races, and the defences against them
---

## Introduction

A shared computer holds the data of many users and runs programs written by many authors, some careless and some malicious. The operating system must ensure that each user and each program can do exactly what it is entitled to do and nothing more: read its own files but not someone else's mail, use the network but not reconfigure the firewall, install updates only with an administrator's approval.

Two related ideas are at work. **Protection** is the set of mechanisms the OS uses to control access to resources, such as files, memory, and devices. **Security** is the broader goal of defending the system against attack, including attacks that exploit bugs in programs or trick users. This lesson covers the models used to express "who may do what", the way UNIX-like systems implement them, and the classic attacks and defences that every operating system must deal with.

**Before you start:** you should know user and kernel mode, processes, and inodes and file permissions at a basic level.

## Core theory

### Design principles

In 1975, Jerome Saltzer and Michael Schroeder set out design principles for protection that are still cited today. Among the most important:

- **Least privilege:** every program and user should run with the minimum rights needed for its task, so that a compromise or a bug does limited damage.
- **Complete mediation:** every access to every object must be checked, not just the first one.
- **Fail-safe defaults:** deny access unless it is explicitly granted.
- **Economy of mechanism:** keep protection mechanisms small and simple enough to verify.
- **Separation of privilege:** require more than one condition (for example, a password and a hardware key) for sensitive operations.

### Domains and the access matrix

A **protection domain** is a set of (object, rights) pairs, describing what a process may do. A process runs in one domain at a time, often determined by its user, and may switch domains (for example, when it executes a setuid program or makes a system call).

The **access matrix** describes all rights in the system: one row per domain, one column per object, and each entry the set of rights the domain has on the object.

| Domain | `report.txt` | `payroll.db` | printer |
| :--- | :--- | :--- | :--- |
| alice | read, write, own | | print |
| bob | read | read | print |
| payroll service | | read, write | |

The matrix is sparse, so it is stored in one of two ways:

- **Access control lists (ACLs):** store each **column** with its object: "who may access this file, and how". Checking a request means looking up the requesting domain in the object's list. ACLs make it easy to see and revoke all access to an object; they are used by file systems in Windows (NTFS), macOS, and Linux.
- **Capability lists:** store each **row** with its domain: a list of unforgeable tokens, each naming an object and the rights it grants. Presenting a capability proves the right to use it. Capabilities make delegation easy (pass the token) but revocation hard (find every copy). File descriptors are capability-like: once a process has opened a file, the descriptor carries the right to read or write it.

### UNIX permissions

Each file's inode holds an owner, a group, and nine permission bits: read (`r`), write (`w`), and execute (`x`) for the **owner**, the **group**, and **others**, often written in octal: `rwxr-x---` is 750.

To check an access, the kernel uses exactly one class: if the process's user ID is the owner, the owner bits apply; otherwise, if one of its groups is the file's group, the group bits apply; otherwise the others bits apply. The classes are not combined, so an owner whose own bits deny access is denied even if the group bits would allow it. The superuser (**root**, user ID 0) bypasses most checks.

For directories, `r` allows listing names, `w` allows creating and deleting entries, and `x` allows **traversing** (using the directory in a path).

Three special bits:

- **setuid** on an executable makes it run with the **owner's** user ID rather than the caller's. The `passwd` program uses it to let ordinary users update the protected password database, which is also why setuid programs are prime targets for attackers.
- **setgid** does the same for the group (and, on directories, makes new files inherit the directory's group).
- The **sticky bit** on a directory lets users delete only their own files there; `/tmp` is the classic example.

Modern Linux also splits root's power into separate **capabilities** (for instance, the right to bind to network ports below 1024), so a program can be given just the privilege it needs.

### Discretionary, mandatory, and role-based control

- **Discretionary access control (DAC):** the owner of an object decides who may access it. UNIX permissions and most ACLs are discretionary.
- **Mandatory access control (MAC):** a system-wide policy, which users cannot override, decides. Military-style multilevel security, formalised in the Bell-LaPadula model, forbids reading data above one's clearance ("no read up") and writing data below it ("no write down"). SELinux and AppArmor add mandatory policies to Linux.
- **Role-based access control (RBAC):** rights are assigned to **roles** (such as "nurse" or "database administrator"), and users acquire rights by being assigned roles, which simplifies administration in large organisations.

### Authentication

Access control depends on knowing who is asking. Systems authenticate users by something they know (a password), have (a hardware key or phone), or are (a fingerprint). Passwords must never be stored in plain text. They are stored as **salted hashes** computed with deliberately slow functions such as bcrypt, scrypt, Argon2, or PBKDF2: the **salt**, a random value stored with each hash, makes identical passwords hash differently and defeats precomputed tables, and the slowness makes guessing expensive.

### Common attacks

- **Buffer overflow:** a program copies input into a fixed-size buffer without checking its length; the excess overwrites adjacent memory, such as a function's return address on the stack, and can redirect execution to attacker-supplied code.
- **Privilege escalation:** exploiting a bug in a privileged program (a setuid binary or the kernel itself) to gain rights the attacker should not have.
- **Time-of-check to time-of-use (TOCTOU) races:** a program checks a condition, such as permission on a file name, and then acts on the name, but an attacker changes what the name refers to in between, for example by replacing the file with a symbolic link to a sensitive file.
- **Malware:** viruses (attach to programs), worms (spread themselves across networks), trojans (disguised as useful software), and **rootkits**, which hide an attacker's presence by modifying the OS.
- **Denial of service:** exhausting a resource (CPU, memory, connections, disk) so that legitimate users are refused service.
- **Social engineering:** tricking users into running malware or revealing credentials, which bypasses technical controls entirely.

### Defences

- **Address space layout randomization (ASLR):** load code, libraries, stack, and heap at random addresses, so an attacker cannot predict where to jump.
- **Non-executable memory (NX, DEP, W^X):** mark data pages, including the stack, non-executable, so injected bytes cannot run as code.
- **Stack canaries:** place a secret value before the return address and check it before returning; an overflow that overwrites the return address also changes the canary and is detected.
- **Sandboxing:** confine programs with restricted rights, for example with seccomp system-call filters, containers, or the per-app sandboxes of mobile operating systems.
- **Code signing and secure boot:** run only software signed by trusted parties, starting from the firmware.
- **Patching, auditing, and logging:** fix known vulnerabilities promptly, and record security-relevant events so that intrusions can be detected and investigated.

## Worked examples

### Example 1: An access matrix stored two ways

```python
matrix = {
    ("alice", "report.txt"): {"read", "write", "own"},
    ("bob", "report.txt"): {"read"},
    ("bob", "payroll.db"): {"read"},
    ("payroll", "payroll.db"): {"read", "write"},
}

acl, capabilities = {}, {}
for (domain, obj), rights in matrix.items():
    acl.setdefault(obj, {})[domain] = rights               # column stored with the object
    capabilities.setdefault(domain, {})[obj] = rights      # row stored with the domain

def allowed(domain, obj, right):
    return right in acl.get(obj, {}).get(domain, set())    # fail-safe default: deny

print("ACL of payroll.db:", {d: sorted(r) for d, r in acl["payroll.db"].items()})
print("capabilities of bob:", {o: sorted(r) for o, r in capabilities["bob"].items()})
for request in [("bob", "report.txt", "read"), ("bob", "report.txt", "write"),
                ("alice", "payroll.db", "read"), ("payroll", "payroll.db", "write")]:
    print(request, "->", "allowed" if allowed(*request) else "denied")
```

Output:

```text
ACL of payroll.db: {'bob': ['read'], 'payroll': ['read', 'write']}
capabilities of bob: {'report.txt': ['read'], 'payroll.db': ['read']}
('bob', 'report.txt', 'read') -> allowed
('bob', 'report.txt', 'write') -> denied
('alice', 'payroll.db', 'read') -> denied
('payroll', 'payroll.db', 'write') -> allowed
```

The ACL view answers "who can touch the payroll database?" in one lookup, which is what an auditor or administrator needs. The capability view answers "what can bob touch?", which is what a process carries with it. Alice has no entry for the database at all, and the check denies by default rather than allowing what is not listed.

### Example 2: Reading and evaluating UNIX permissions

```python
import stat

for mode in (0o100644, 0o100755, 0o40755, 0o104755, 0o41777, 0o100600):
    print(oct(mode), stat.filemode(mode))

def may(mode, file_uid, file_gid, uid, gids, want):
    """want is 'r', 'w' or 'x'. Exactly one class of bits is used: owner, else group, else other."""
    shift = {"r": 2, "w": 1, "x": 0}[want]
    if uid == 0:
        return True                                         # root bypasses the check (simplified)
    if uid == file_uid:
        bits = (mode >> 6) & 0o7
    elif file_gid in gids:
        bits = (mode >> 3) & 0o7
    else:
        bits = mode & 0o7
    return bool(bits >> shift & 1)

mode = 0o100470                                             # owner r--, group rwx, other ---
print(may(mode, 1000, 50, 1000, {50}, "w"), may(mode, 1000, 50, 1001, {50}, "w"), may(mode, 1000, 50, 1002, {7}, "r"))
```

Output:

```text
0o100644 -rw-r--r--
0o100755 -rwxr-xr-x
0o40755 drwxr-xr-x
0o104755 -rwsr-xr-x
0o41777 drwxrwxrwt
0o100600 -rw-------
False True False
```

The first character shows the file type (`-` for a regular file, `d` for a directory). An `s` in the owner's execute position means setuid, and a `t` in the others' execute position means the sticky bit, as on `/tmp` (mode 1777). The last line shows a classic surprise: for a file with mode 470, the owner (user 1000) may **not** write, even though the owner belongs to the group, which may; the kernel uses only the owner class for the owner. Another member of the group may write, and a user outside the group may not even read.

### Example 3: Storing passwords safely

```python
import hashlib
import hmac

def hash_password(password, salt, iterations=200_000):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)

salt_a = bytes.fromhex("8f3a1c5e9b2d4f60")      # in practice: os.urandom(16), stored with the hash
salt_b = bytes.fromhex("17c2e04b6a9d3f85")
stored = hash_password("correct horse", salt_a)

print(stored.hex()[:32])
print(hash_password("correct horse", salt_b).hex()[:32])
print(hmac.compare_digest(stored, hash_password("correct horse", salt_a)),
      hmac.compare_digest(stored, hash_password("Correct horse", salt_a)))
```

Output:

```text
6af06737f0e98001fafbec2a41d0d13e
fa97f38c584ebca459243ecec21d382f
True False
```

The same password produces completely different hashes with different salts, so an attacker who steals the password file cannot tell which users share a password and cannot use one precomputed table for everyone. Logging in recomputes the hash with the stored salt and compares it with `hmac.compare_digest`, which takes the same time whether or not the values match early, avoiding a timing leak. The 200,000 iterations make each guess costly for an attacker while adding only a fraction of a second to a legitimate login. Fixed salts appear here only so that the output is reproducible.

## Applications

- **File systems** in every major OS enforce owner, group, and ACL permissions on each open.
- **Mobile operating systems** sandbox every app and require explicit permission grants for the camera, location, and contacts, an application of least privilege.
- **Servers and containers** combine user separation, Linux capabilities, seccomp filters, and mandatory policies (SELinux, AppArmor) to limit what a compromised service can do.
- **Enterprises** manage access with roles (RBAC) and directory services, granting rights by job function.
- **Exploit mitigation:** ASLR, NX, and stack canaries are enabled by default in modern compilers and operating systems, making simple buffer-overflow attacks far harder.

## Common mistakes

- **Running services as root** when they need only one privilege, violating least privilege; drop privileges or use capabilities.
- **Assuming UNIX permission classes are combined.** Only one class applies; an owner can be denied rights that the group has.
- **Storing passwords with fast, unsalted hashes** such as a single round of SHA-256, which are cracked quickly with modern hardware.
- **Checking a file and then opening it by name** in a privileged program (a TOCTOU race); open first and then check the opened file, or use APIs that check and act atomically.
- **Treating access control as only about files.** Network ports, devices, memory, and inter-process communication need the same mediation.

## Revision notes

- Protection = mechanisms controlling access; security = defence against attacks.
- Principles: least privilege, complete mediation, fail-safe defaults, economy of mechanism, separation of privilege.
- Access matrix: domains × objects → rights. ACLs store columns (easy auditing and revocation); capabilities store rows (easy delegation).
- UNIX: owner/group/others × rwx; one class applies; directories: r list, w modify entries, x traverse; setuid, setgid, sticky bit.
- DAC (owner decides), MAC (system policy; Bell-LaPadula), RBAC (roles).
- Store passwords as slow salted hashes. Attacks: buffer overflow, privilege escalation, TOCTOU, malware, denial of service. Defences: ASLR, NX, canaries, sandboxing, signing, patching.

## Practice questions

:::question basic
What permissions does octal mode 640 give, and to whom?
:::answer
6 = `rw-` for the owner (read and write), 4 = `r--` for the group (read only), and 0 = `---` for everyone else (no access). The full string is `rw-r-----`.
:::

:::question basic
What is the principle of least privilege, and why does it limit the damage of an attack?
:::answer
Every user, program, and service should have only the rights it needs for its task, and only while it needs them. If a component with few rights is compromised or misbehaves, the attacker gains only those few rights; a web server that cannot write to system files cannot be used to modify them, even if an attacker takes it over.
:::

:::question intermediate
Compare access control lists and capability lists for revoking a user's access to one file, and for letting a process give another process access to one file.
:::answer
Revocation is easy with ACLs: remove the user's entry from the file's list, and every future access is denied. With capabilities, the system must find and invalidate every copy of the token, which may have been passed around, so revocation needs extra mechanisms such as indirection or expiry. Delegation is the reverse: with capabilities, the process simply passes the token (as UNIX processes can pass an open file descriptor over a socket); with ACLs, someone with the authority to change the ACL must add the other process's domain to it.
:::

:::question intermediate
Why is the setuid bit on a program such as `passwd` both useful and dangerous?
:::answer
It is useful because ordinary users need to change their own password, which means writing to a password database that only root may modify; running `passwd` with root's identity lets it perform this one controlled task. It is dangerous because any bug in the program, such as a buffer overflow in its input handling, lets an attacker execute code with root's privileges. Setuid programs must therefore be small, carefully audited, and drop privileges as soon as possible.
:::

:::question intermediate
Explain a time-of-check to time-of-use (TOCTOU) attack against a privileged program that calls `access(path)` and then `open(path)`.
:::answer
The program, running with elevated privileges, uses `access` to check whether the real user may write to `path`, and if so calls `open` to write to it. Between the two calls, the attacker replaces `path` with a symbolic link to a protected file such as the password database. The check succeeded on the attacker's own file, but the open acts on the protected file with the program's elevated privileges. The fix is to make the check and the use refer to the same object: drop privileges and open the file as the user, or open the file first and check the properties of the opened descriptor.
:::

:::question advanced
How do ASLR and non-executable memory each defeat a classic stack buffer overflow, and why are both used together?
:::answer
In a classic attack, the attacker overflows a stack buffer with machine code and overwrites the return address to point at that code. Non-executable memory marks the stack as data, so when the function returns, jumping into the injected bytes raises a fault instead of running them. Attackers responded by reusing code that is already executable, chaining existing instruction sequences in libraries (return-oriented programming), which NX does not stop. ASLR loads libraries, the stack, and the heap at random addresses each run, so the attacker does not know where those instruction sequences or buffers are. Each defence covers a weakness of the other, and stack canaries add a third layer by detecting the overwrite before the function returns.
:::

## Further learning

- **Next:** this completes the Operating Systems fundamentals course; revisit *OS Roles & Kernel Architectures* to see how protection shapes kernel design.
- **Related:** *File System Structure & Inodes* shows where permission bits and ownership are stored.
- **Related:** *System Calls & Dual-Mode Execution* explains the hardware boundary that makes protection enforceable.
