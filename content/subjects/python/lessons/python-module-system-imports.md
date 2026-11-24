---
lesson: python-module-system-imports
title: Module System & Package Imports
summary: How Python finds and loads modules, the forms of the import statement, how sys.path and packages work, and how to structure a project so imports stay predictable.
minutes: 30
type: theory
objectives:
  - Use import, from-import, and aliases correctly and explain what each binds in the current namespace
  - Describe how Python searches sys.path, caches modules in sys.modules, and runs a module only once
  - Organise code into packages with __init__.py and explain the role of if __name__ == "__main__"
review: ai-draft
---
## Introduction

A program that grows beyond a few hundred lines becomes hard to read in one file. Python lets you split code into **modules** (single `.py` files) and **packages** (folders of modules), and reuse them with the `import` statement. The same mechanism gives you the standard library and every package installed with `pip`. Understanding how imports work saves hours of confusion over errors like `ModuleNotFoundError` or code that runs twice.

**Before you start:** you should know functions, classes, and how to run a Python file from the command line.

## Core theory

### Modules and the import statement

Every `.py` file is a module whose name is the file name without `.py`. Importing it runs the file's top-level code once and creates a **module object** holding everything the file defined.

- `import math` binds the name `math`; you write `math.sqrt(2)`.
- `import numpy as np` binds an **alias**.
- `from math import sqrt, pi` binds `sqrt` and `pi` directly in your namespace.
- `from math import *` imports every public name. Avoid it: readers cannot tell where names came from, and it can silently overwrite your own names.

### How Python finds a module

For `import x`, Python first checks **`sys.modules`**, a dictionary cache of modules already loaded. If `x` is there, the existing module object is reused; this is why a module's top-level code runs only once per program, however many files import it.

Otherwise Python searches the directories in **`sys.path`**, in order: the directory of the script being run (or the current directory in an interactive session), directories from the `PYTHONPATH` environment variable, the standard library, and the `site-packages` folder where `pip` installs packages. The first match wins, so a file named `random.py` in your project hides the standard `random` module, a classic source of strange errors.

### Packages

A **package** is a directory of modules, usually containing an `__init__.py` file that runs when the package is imported. `import shop.cart` loads `shop/__init__.py` and then `shop/cart.py`. Inside a package, **relative imports** such as `from .cart import Cart` or `from ..utils import money` refer to sibling or parent modules; they work only for code imported as part of the package, not for a file run directly as a script.

### `__name__` and running modules

Each module has a `__name__` attribute. When a file is imported, `__name__` is its module name; when it is run directly, `__name__` is `"__main__"`. The idiom

```python
if __name__ == "__main__":
    main()
```

lets a file act as both a reusable module and a runnable script. `python -m package.module` runs a module inside a package with the package context set up correctly.

## Worked examples

### Example 1: Building and importing a small package

```python
import os, sys, importlib, pathlib

root = pathlib.Path("shop")
root.mkdir(exist_ok=True)
(root / "__init__.py").write_text("print('shop package loaded')\n")
(root / "pricing.py").write_text(
    "TAX = 0.18\n"
    "def with_tax(amount):\n"
    "    return round(amount * (1 + TAX), 2)\n"
)
sys.path.insert(0, os.getcwd())
importlib.invalidate_caches()

import shop.pricing
from shop.pricing import with_tax as taxed
import shop.pricing as again

print(taxed(100), shop.pricing.TAX)
print(again is shop.pricing, "shop.pricing" in sys.modules)
```

Output:

```text
shop package loaded
118.0 0.18
True True
```

The package message prints once even though the module is imported three times: later imports are served from `sys.modules`. `importlib.invalidate_caches()` is needed only because the files were created while the program was running.

### Example 2: The `__main__` guard

```python
import os, sys, importlib, pathlib, subprocess

pathlib.Path("greet.py").write_text(
    "def hello(name):\n"
    "    return f'Hello, {name}!'\n"
    "print('module name is', __name__)\n"
    "if __name__ == '__main__':\n"
    "    print(hello('script'))\n"
)
sys.path.insert(0, os.getcwd())
importlib.invalidate_caches()
import greet
print(greet.hello("importer"))
result = subprocess.run([sys.executable, "greet.py"], capture_output=True, text=True)
print(result.stdout.strip())
```

Output:

```text
module name is greet
Hello, importer!
module name is __main__
Hello, script!
```

Imported, the file's `__name__` is `greet` and the guarded block is skipped; run as a script, `__name__` is `__main__` and the block runs.

## Applications

- **Project structure:** a package per feature (`auth`, `billing`, `reports`) keeps large applications navigable.
- **Reusable libraries:** functions written once are imported by scripts, tests, and notebooks.
- **Command-line tools:** the `__main__` guard and `python -m` turn modules into commands.
- **Plugins:** `importlib.import_module(name)` loads modules whose names are known only at run time.

## Common mistakes

- **Naming a file after a standard module.** `random.py` or `json.py` in your folder shadows the real module.
- **Expecting a module to re-run on every import.** It runs once; later imports reuse `sys.modules`.
- **Using relative imports in a script run directly.** Run it with `python -m package.module` instead.
- **Circular imports.** Two modules importing each other at the top level can see half-initialised modules; move shared code to a third module.

## Revision notes

- A module is a `.py` file; a package is a directory of modules with `__init__.py`.
- `import m`, `import m as a`, `from m import x`; avoid `import *`.
- Lookup order: `sys.modules` cache, then each directory in `sys.path`.
- Top-level module code runs once per process.
- `__name__ == "__main__"` only when the file is run directly.
- Relative imports (`from .x import y`) work inside packages.

## Practice questions

:::question basic
What is the difference between `import math` and `from math import sqrt`?
:::answer
`import math` binds only the name `math`, so you call `math.sqrt(4)`. `from math import sqrt` binds `sqrt` directly in your namespace, so you call `sqrt(4)`; the name `math` is not defined unless imported separately.
:::

:::question basic
Why does a print statement at the top of a module run only once, even if three files import it?
:::answer
After the first import, the module object is stored in `sys.modules`. Later imports find it there and reuse it without running the file again.
:::

:::question intermediate
A student creates `random.py` with their own experiments, and `import random; random.randint(1, 6)` now fails. Why?
:::answer
The script's own directory comes first in `sys.path`, so `import random` finds the student's `random.py` instead of the standard library module. That file has no `randint`, so the call raises `AttributeError`. Renaming the file fixes it.
:::

:::question intermediate
What does `if __name__ == "__main__":` achieve in a file that defines helper functions?
:::answer
Code under the guard runs only when the file is executed directly, because only then is `__name__` equal to `"__main__"`. When another module imports the file, the helpers become available without running the demo or command-line code.
:::

:::question advanced
Module `a` does `from b import helper` at the top, and module `b` does `from a import config` at the top. Running `import a` fails with an ImportError about a partially initialised module. Explain and fix.
:::answer
Importing `a` starts executing it and registers it in `sys.modules`; its first line imports `b`, which then tries to take `config` from `a` before `a` has defined it, so the name does not exist yet. Fix it by moving the shared values to a third module both import, by importing inside the function that needs it, or by importing the module (`import a`) and reading `a.config` at call time.
:::

## Further learning

- **Next:** *Standard Library Essentials* tours the modules every Python program can import without installing anything.
- **Related:** *Unit Testing & Debugging* shows how test files import the code they test.
