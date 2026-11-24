---
lesson: python-classes-inheritance
title: Classes, Inheritance & Polymorphism
summary: Defining classes with __init__ and methods, the role of self, inheriting and overriding behaviour with super(), and polymorphism through duck typing.
minutes: 55
type: theory
objectives:
  - Define a class with an initialiser, instance attributes, methods, and a readable string representation
  - Build a subclass that extends its parent with super() and overrides methods
  - Explain polymorphism and duck typing, and use them to write code that works with many types
review: ai-draft
---
## Introduction

As programs grow, related data and the functions that work on it belong together. A bank account has a balance and the operations deposit and withdraw; a shape has dimensions and an area. **Object-oriented programming** packages such data and behaviour into **classes**. A class is a blueprint, and each **object** (instance) made from it has its own data. This lesson shows how to write classes in Python, reuse them through **inheritance**, and write flexible code with **polymorphism**.

**Before you start:** you should know functions, parameters, return values, and lists.

## Core theory

### Classes, instances, and self

```python
class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
```

`class Account:` defines the blueprint. `__init__` is the **initialiser**: it runs when you call `Account("Asha")` and sets up the new object's **instance attributes**. Every method receives the instance as its first parameter, named `self` by convention; `acc.deposit(50)` is shorthand for `Account.deposit(acc, 50)`. Attributes assigned on `self` belong to that one object, while variables assigned directly in the class body are **class attributes** shared by all instances.

### Special methods

Methods with double underscores customise how objects behave with built-in syntax. `__str__` gives the text shown by `print` and f-strings; `__repr__` gives an unambiguous developer view; `__eq__` defines `==`; `__len__` makes `len(obj)` work. Defining them makes your objects feel like built-in types.

### Inheritance and super()

A **subclass** inherits every attribute and method of its **parent** and can add or replace them:

```python
class Savings(Account):
    def __init__(self, owner, balance=0, rate=0.04):
        super().__init__(owner, balance)
        self.rate = rate
```

`super().__init__(...)` runs the parent's initialiser so the inherited attributes are set up, then the subclass adds its own. A method with the same name as a parent method **overrides** it; the override can still call the parent version through `super()`. `isinstance(obj, Account)` is `True` for instances of `Account` and of every subclass. Inheritance models an "is a" relationship; when one object merely uses another ("has a"), store it as an attribute instead (**composition**).

### Polymorphism and duck typing

**Polymorphism** means one piece of code works with objects of different types, each responding in its own way. In Python it rests on **duck typing**: "if it walks like a duck and quacks like a duck, it is a duck". A function that calls `shape.area()` works with any object that has an `area` method, whether or not the classes share a parent. Python checks for the method only when the call happens.

## Worked examples

### Example 1: An account with a subclass

```python
class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def withdraw(self, amount):
        if amount > self.balance:
            return False
        self.balance -= amount
        return True

    def __str__(self):
        return f"{self.owner}: {self.balance}"


class Savings(Account):
    def __init__(self, owner, balance=0, rate=0.05):
        super().__init__(owner, balance)
        self.rate = rate

    def add_interest(self):
        self.balance += round(self.balance * self.rate)


acc = Savings("Asha", 1000)
print(acc.withdraw(1500), acc.withdraw(200))
acc.add_interest()
print(acc)
print(isinstance(acc, Account), isinstance(acc, Savings))
```

Output:

```text
False True
Asha: 840
True True
```

The first withdrawal is refused, the second leaves 800, and 5% interest adds 40. `print(acc)` uses the inherited `__str__`.

### Example 2: Polymorphism with duck typing

```python
import math

class Circle:
    def __init__(self, r):
        self.r = r
    def area(self):
        return math.pi * self.r ** 2

class Rectangle:
    def __init__(self, w, h):
        self.w, self.h = w, h
    def area(self):
        return self.w * self.h

shapes = [Circle(1), Rectangle(2, 3), Circle(0.5)]
for shape in shapes:
    print(type(shape).__name__, round(shape.area(), 2))
print(round(sum(s.area() for s in shapes), 2))
```

Output:

```text
Circle 3.14
Rectangle 6
Circle 0.79
9.93
```

`Circle` and `Rectangle` share no parent class, yet the loop treats them alike because both provide `area()`.

## Applications

- **Domain models:** classes such as `Student`, `Course`, and `Order` keep data and rules together.
- **Frameworks:** web frameworks and test libraries let you subclass their base classes and override hooks.
- **Plug-in designs:** any object with the expected methods can be passed in, so new behaviour needs no changes to existing code.
- **Data containers:** `dataclasses` generate `__init__`, `__repr__`, and `__eq__` for record-like classes.

## Common mistakes

- **Forgetting `self`.** A method defined as `def deposit(amount)` fails when called on an instance because Python also passes the instance.
- **Not calling `super().__init__`.** The subclass then lacks the parent's attributes and raises `AttributeError` later.
- **Mutable class attributes.** `items = []` in the class body is shared by every instance; create it in `__init__` instead.
- **Inheriting just to reuse code.** If the subclass is not truly a kind of the parent, prefer composition.

## Revision notes

- `__init__` sets up a new instance; `self` is the instance.
- Instance attributes live on `self`; class attributes are shared.
- `__str__` controls printing; `__repr__` is for developers; `__eq__` defines `==`.
- `class Child(Parent)` inherits; `super()` reaches the parent's methods.
- Overriding replaces a parent method with one of the same name.
- Duck typing: any object with the needed methods works.

## Practice questions

:::question basic
What does `self` refer to inside a method, and why must it be the first parameter?
:::answer
`self` is the instance the method was called on. Python passes it automatically, so `obj.method(x)` becomes `Class.method(obj, x)`; the method must declare a parameter to receive it.
:::

:::question basic
What is the difference between an instance attribute and a class attribute?
:::answer
An instance attribute is assigned on `self`, usually in `__init__`, and each object has its own value. A class attribute is assigned in the class body and is shared by all instances unless an instance sets its own attribute with the same name.
:::

:::question intermediate
A subclass defines its own `__init__` but forgets to call `super().__init__(owner, balance)`. What goes wrong?
:::answer
The parent's initialiser never runs, so attributes such as `owner` and `balance` are never created on the instance. The first method that reads them raises `AttributeError`.
:::

:::question intermediate
Explain duck typing using a function `total_area(shapes)` that sums `s.area()`.
:::answer
The function never checks types; it only calls `area()`. Any object providing an `area` method works, whether it is a `Circle`, a `Rectangle`, or a class written later, and objects without that method fail only when the call is made. Behaviour, not ancestry, decides compatibility.
:::

:::question advanced
Why is `class Team: members = []` followed by `self.members.append(name)` in a method a bug, and how do you fix it?
:::answer
`members` is a class attribute, so one list is shared by every `Team`; adding a member to one team adds it to all of them. Create the list per instance in the initialiser: `def __init__(self): self.members = []`.
:::

## Further learning

- **Next:** *Try-Except Blocks & Custom Exceptions* shows how to define your own exception classes by inheriting from `Exception`.
- **Related:** *Closures & Decorators* introduces another way to attach behaviour to functions without classes.
