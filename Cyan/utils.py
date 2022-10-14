"""Utilities.

Pos or position class, pos_highlight function and Printer"""
import sys
from dataclasses import dataclass

__all__ = ("Pos", "pos_highlight", "Printer")


@dataclass(slots=True)
class Pos:
    """Exact position in cyan code"""
    filename: str
    file_text: str
    idx: int
    line_num: int
    char_num: int

    def __repr__(self) -> str:
        return f"Pos(line {self.line_num}, char {self.char_num})"

    def advance(self, newline=False) -> None:
        if newline:
            self.char_num = 1
            self.line_num += 1
        else:
            self.char_num += 1
        self.idx += 1

    def copy(self):
        return Pos(
            self.filename, self.file_text, self.idx, self.line_num, self.char_num
        )


def pos_highlight(text: str, start_pos: Pos, end_pos: Pos) -> str:
    """Used in Errors for showing where the position in cyan code is"""
    result = ""

    # Calculate indices
    idx_start: int = max(text.rfind("\n", 0, start_pos.idx), 0)
    idx_end: int = text.find("\n", idx_start + 1)

    if idx_end < 0:
        idx_end = len(text)

    # Generate each line
    line_count: int = end_pos.line_num - start_pos.line_num + 1

    for i in range(line_count):
        # Calculate line columns
        line: str = text[idx_start:idx_end]
        col_start = start_pos.char_num if i == 0 else 0
        col_end = end_pos.char_num if i == line_count - 1 else len(line) - 1

        # Append to result
        result += f"{line}\n" + " " * col_start + "~" * (col_end - col_start)

        # Re-calculate indices
        idx_start = idx_end
        idx_end = text.find("\n", idx_start + 1)
        if idx_end < 0:
            idx_end = len(text)

    return result.replace("\t", "")


class _CLR:
    """Stores different indicator colors for Printer"""
    __slots__ = ()
    RESET = "\u001b[0m"
    DEBUG_CLR = "\u001b[30;1m"
    ERROR_CLR = "\u001b[31;1m"
    TIME_CLR = "\u001b[36m"
    SEPERATOR_CLR = ""


class Printer:
    """
    Manager for printing stuff.
    Indicates different types of prints with different console colors
    """
    __slots__ = ()

    @staticmethod
    def debug(*values) -> None:
        print(end=_CLR.DEBUG_CLR)
        print(*values)
        print(end=_CLR.RESET)

    @staticmethod
    def seperator() -> None:
        print(end=_CLR.SEPERATOR_CLR)

    @staticmethod
    def error(*values) -> None:
        print(end=_CLR.ERROR_CLR)
        print(*values)
        print(end=_CLR.RESET)

    @staticmethod
    def output(text, end="") -> None:
        sys.stdout.write(text + end)

    @staticmethod
    def time(title):
        print(end=_CLR.TIME_CLR)
        print(title)
        print(end=_CLR.RESET)
