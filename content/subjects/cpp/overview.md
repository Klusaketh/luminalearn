C++ extends C with classes, templates, and a rich standard library while keeping C's speed and control over memory. It is used wherever performance matters: game engines, browsers, trading systems, robotics, compilers, and the core of machine learning frameworks. Modern C++, from C++11 onwards, adds features such as smart pointers, move semantics, and lambdas that make it far safer and more expressive than the C++ of the 1990s.

This subject teaches modern C++ from the start. It begins with syntax, streams, overloading, and references, then introduces the standard `vector` and `string` containers in place of raw arrays. It explains RAII, the idea that an object's lifetime manages a resource, and the smart pointers built on it. The core of the subject is object-oriented design: classes and constructors, copy control and move semantics with the rule of five, operator overloading, inheritance, and virtual functions with dynamic dispatch. It closes with templates and generic programming, the Standard Template Library's containers, iterators, and algorithms, exception safety, and file streams.

Throughout, the emphasis is on writing code that is correct by construction: resources that cannot leak and interfaces that are hard to misuse.

## What you will learn
- Write modern C++ programs using streams, references, and function overloading
- Use std::vector and std::string instead of raw arrays and C strings
- Manage resources with RAII and the smart pointers unique_ptr and shared_ptr
- Design classes with constructors, encapsulation, and the rule of five, including move semantics
- Overload operators so user-defined types behave naturally
- Build class hierarchies and explain how virtual functions and vtables implement run-time polymorphism
- Write function and class templates for generic code
- Choose STL containers and combine iterators, algorithms, and lambdas
- Write exception-safe code and handle files with modern file streams

## Prerequisites
- Programming experience in C or another language, including functions and loops
- Familiarity with pointers and memory is helpful; the C Programming subject covers both
- Access to a C++17 or later compiler such as GCC, Clang, or MSVC

## Glossary
- **Class**: a user-defined type that bundles data members with member functions
- **Constructor**: a special member function that initialises a new object
- **Destructor**: a special member function that runs when an object's lifetime ends
- **Reference**: an alias for an existing object, declared with &
- **RAII**: Resource Acquisition Is Initialization; tying a resource's lifetime to an object's lifetime
- **Smart pointer**: a class such as unique_ptr that owns heap memory and frees it automatically
- **Move semantics**: transferring a resource from one object to another instead of copying it
- **Rule of five**: if a class defines a destructor, copy or move operation, it usually needs all five
- **Virtual function**: a member function whose call is resolved at run time from the object's dynamic type
- **Vtable**: the per-class table of function pointers used to dispatch virtual calls
- **Template**: a blueprint from which the compiler generates functions or classes for given types
- **STL**: the Standard Template Library of containers, iterators, and algorithms
- **Iterator**: an object that walks through the elements of a container
- **Lambda**: an unnamed function object written inline

## Further reading
- Bjarne Stroustrup, *A Tour of C++* (Addison-Wesley)
- Bjarne Stroustrup, *Programming: Principles and Practice Using C++* (Addison-Wesley)
- Scott Meyers, *Effective Modern C++* (O'Reilly Media)
- Nicolai M. Josuttis, *The C++ Standard Library: A Tutorial and Reference* (Addison-Wesley)
