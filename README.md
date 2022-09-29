# Cyan Programming Language
![cyan1-cover](https://user-images.githubusercontent.com/93242673/186955621-f0f9f58d-fdbc-40eb-8e32-ba558f3d2dd4.png)

## Current features

- variables
- binary and unary operations
- if/else expressions
- while loops
- functions
- lambda functions

## Usage

Pre-requiestes: `git` and `python3`

Commands:
```bash
git clone https://github.com/was07/Cyan
cd Cyan
python -m Cyan
```
It will start the Cyan shell.

To run a file, use `python -m Cyan filename.cy`

To see other options, use `python -m Cyan --help`

## Example Code

Repl
```py
Cyan 1.1.1 shell on win32
>>> "ab" + 'cd'
abcd
>>> 7 ** 2
49
>>> fun square(i) {i ** 2}
<Function square>
>>> square(4)
16
>>> let a = Bool(11)
true
>>> if a != 2 then 'no' else 'yes'
yes
>>> out(a)
2   
None
>>> while a < 5 {let a = a + 1}
None
```

Code
```py
let a = 1
while a <= 5 {
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

| Data type | Converter   | examples                             |
|-----------|-------------|--------------------------------------|
| String    | `Str()`     | `'ab'`, `"cd"`                       |
| Number    | `Num()`     | `1`, `2.45`, `1.` (`.1` is invalid)  |
| Boolean   | `Bool()`    | `true`, `false`                      |
| None      |             | `none`                               |

| Build-in Function | Usage                |
|-------------------|----------------------|
| `out()`           | make standard output |
