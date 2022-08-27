# Cyan Programming Language
![cyan1-cover](https://user-images.githubusercontent.com/93242673/186955621-f0f9f58d-fdbc-40eb-8e32-ba558f3d2dd4.png)


**Status**: Unstable

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
python Cyan
```
It will start the Cyan shell.

To run a file, use `python Cyan filename.cy`

To see other options, use `python Cyan --help`

## Example Code

```py
Cyan 1.0.0 shell on win32
>>> 7 ** 2
49
>>> fun square(i): i ** 2
<Function square>
>>> square(4)
16
>>> let a = 2
2
>>> if a != 2 then 100 else 200
200
>>> print(a)
2   
None
>>> while a < 5 {let a = a + 1}
None
```
