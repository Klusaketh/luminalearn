Digital logic is the study of circuits that work with two values, 0 and 1. Every processor, memory chip, and controller is built from a few kinds of logic gates, combined first into circuits that compute a result from their current inputs and then into circuits that remember state. This subject explains how simple gates become adders, multiplexers, registers, counters, and the state machines that control hardware.

It starts with number systems: binary, octal, and hexadecimal conversion, two's complement, binary arithmetic, overflow, and codes such as BCD and Gray code. It then introduces Boolean algebra, De Morgan's laws, and canonical sum-of-products and product-of-sums forms, followed by logic gates, universal gates, and truth tables. Karnaugh maps show how to simplify a function to the fewest gates. The combinational modules design adders, multiplexers, decoders, encoders, and comparators. The sequential modules explain latches and flip-flops, timing, shift registers, synchronous counters, and finally Mealy and Moore finite state machines.

Each lesson works through truth tables, simplifications, and timing traces by hand, so you can check every step yourself.

## What you will learn
- Convert numbers between binary, octal, decimal, and hexadecimal, and use two's complement
- Perform binary arithmetic, detect overflow, and use codes such as BCD and Gray code
- Simplify Boolean expressions with algebraic laws, including De Morgan's laws
- Express functions in canonical sum-of-products and product-of-sums forms
- Build any function from NAND or NOR gates alone
- Minimise functions with Karnaugh maps, including don't-care conditions
- Design combinational circuits: adders, multiplexers, decoders, encoders, and comparators
- Explain latches and flip-flops and trace their behaviour over clock cycles
- Design shift registers, synchronous counters, and Mealy and Moore state machines

## Prerequisites
- School algebra
- No electronics background is required: circuits are treated as logical building blocks
- Some programming experience helps when relating gates to bitwise operators

## Glossary
- **Bit**: a binary digit, 0 or 1
- **Two's complement**: the standard binary representation of signed integers
- **Logic gate**: a circuit implementing a Boolean function such as AND, OR, or NOT
- **Truth table**: a table listing a function's output for every combination of inputs
- **Universal gate**: a gate type, NAND or NOR, from which every Boolean function can be built
- **Minterm**: a product term in which every variable appears exactly once
- **Karnaugh map**: a grid layout of a truth table that makes simplification visual
- **Combinational circuit**: a circuit whose outputs depend only on its current inputs
- **Sequential circuit**: a circuit whose outputs depend on its inputs and its stored state
- **Multiplexer**: a circuit that selects one of several inputs to pass to the output
- **Flip-flop**: an edge-triggered one-bit memory element
- **Clock**: a periodic signal that synchronises state changes in sequential circuits
- **Finite state machine**: a sequential system with a finite set of states and defined transitions

## Further reading
- M. Morris Mano and Michael D. Ciletti, *Digital Design* (Pearson)
- Charles H. Roth Jr. and Larry L. Kinney, *Fundamentals of Logic Design* (Cengage)
- David Money Harris and Sarah L. Harris, *Digital Design and Computer Architecture* (Morgan Kaufmann)
