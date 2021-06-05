# SBTV

SBTV stands for either "Still Better Than Verilog" or "Still Better Than VHDL" depending on who you ask.
It is intended to be a hardware description language (HDL) analog to esoteric languages like Brainfuck, and was created out of boredom on a Saturday.

An SBTV program describes a single hardware cycle. Input is read as an arbitrarily long string of individual bits, and transformed by successive lines.
Each line must accept the exact number of operands that the previous line generates.
Output is generated according to the out commands in the code and must not contain any multi-bit values.

## Language Specification

Whitespace is ignored, and any other character not in this set will cause the rest of the line to be interpreted as a comment.

### Routing Commands

| Character | Function                                  |
| --------- | --------                                  |
| `v`       | Concatenates two values                   |
| `x`       | Swaps two values                          |
| `<`       | Splits the MSB off a value to the left    |
| `>`       | Splits LSB off a value to the right       |
| `\|`      | Takes one value and outputs it unmodified |
| `-`       | Takes one value and discards it           |
| `:`       | Duplicates one value                      |

### I/O Commands

| Character | Function                                  |
| --------- | --------                                  |
| `i`       | Reads the next input bit                  |
| `o`       | Outputs to the next output bit            |
| `1`       | Constant 1                                |
| `0`       | Constant 0                                |

### Logical Operations

According to the well known DeMorgan laws, any logic function can be implemented using only NAND gates. It was therefore deemed unnecessary to add other logic operations

| Character | Function                                  |
| --------- | --------                                  |
| `&`       | Performs a bit-wise NAND of two operands  |

### Memory Operations

There is a memory list which can be used both for implementing registers and for routing signals across long distances, depending on whether the read is performed before or after the write. Note that there is no way of accessing specific elements of the list, they are always accessed in the order they were inserted.

| Character | Function                                       |
| --------- | --------                                       |
| `w`       | Adds  all bits of one value to the memory list |
| `r`       | Reads one bit from the memory list             |

## Usage

### Simulation

The interpreter can be called using

```
./sbtv.py sim <program file> <inputs>
```

Where program file is the path to the program file and inputs is a space separated list of input vectors. For example the command

```
./sbtv.py test/xor.sb 00 01 10 11
```

Will print the corresponding outputs, i.e.:

```
0 1 1 0
```

### VHDL generation

To compile a file to VHDL, simply use

```
./sbtv.py compile <program file>
```

## Examples

### D-Flipflop

```
ir
wo
```

### 1-Bit Multiplexer

```
iii // inputs a, b, s,
||:
|x|
|:||
|&||
&&
&
o
```

### XOR gate

```
i i
: :
|&|
|:|
& &
 &
 o
```

### Full Adder
```
i  i // inputs a, b
:  :
| x |
:: &
|&||
|:|| i // input c
& &| :
 &  x| // a xor b, c, a nand b, c
 : |||
| x x
: :& |
|&| &
|:| |
& & |
 &  |
 o  o
```
