# Cyan Programming Language
![cyan1-cover](https://user-images.githubusercontent.com/93242673/186955621-f0f9f58d-fdbc-40eb-8e32-ba558f3d2dd4.png)

Cyan. A high-level, functional programming language with syntax focused on readability.

## Current features

- NoneType, String, Number and Boolean datatype
- variables
- binary and unary operations
- if/else expressions
- while loops
- functions
- lambda functions
- comments

## Usage

Pre-requiestes: `git` and `python3` (3.10 or above)

### Commands

Get Cyan in your machine with
```bash
git clone https://github.com/was07/Cyan
```
Start the Cyan shell with `python cyan`

To run a file, use `python cyan filename.cy`. To see other options, use `python cyan --help`

*For devs:* Add `-d` for developer mode.

## Example Code

Repl
```py
Cyan 1.1.0 shell on win32
>>> out("cy"+'an')
cyan
none
>>> fun square(n) {n ** 2}
<Function square>
>>> square(6)
36
>>> let a = 1
1
>>> while a < 5 {out(a); let a = a + 1}
1
2
3
4
none
>>>
```

Code
```py
let a = 1
while a <= 5 {  # this is a comment
    out(a)
    let a = a + 1
}
```
Output
```
1
2
3
4
5
```

## Docs (in progress)

### Datatypes available

| Data type | Converter   | Literal examples                             |
|-----------|-------------|--------------------------------------|
| String    | `Str()`     | `'ab'`, `"cd"`                       |
| Number    | `Num()`     | `1`, `2.45`, `1.` (`.1` is invalid)  |
| Boolean   | `Bool()`    | `true`, `false`                      |
| None      |             | `none`                               |

### Build-in Functions available

| Build-in Function | parameters | Usage                                                                                |
|-------------------|------------|--------------------------------------------------------------------------------------|
| `out()`           | values*    | make standard output. Joins all values with a single space, if there is more than one |
| `inp()`           |            | Takes standard input and returns `Str` object                                        |

### Functions

Functions are constructed with the `fun` keyword. They are also first-class objects, and can be passed as arguments to other functions.
```py
fun plus(a, b) {  # multiple parameters posible
    out(a + b)
}

plus(2, 3)
```

### If-Else Blocks

There are `if`, `then`, and `else` keywords to use to make a if-else block. They can be one or multi iner.

```py
if Num(inp()) > 0 then {  # multi-line example
    out('Positive')
} else {
    out('Negative')
}
```

```py
out(if Num(inp()) > 0 then 'Positive' else 'Negative')  # one_liner example
```

### While Loops

`while` makes while loops.

```py
out('Guess the number.')
let target = 3
while Num(inp()) != target {  # loop
    out('Try again.')
}
out('You got it.')
```

