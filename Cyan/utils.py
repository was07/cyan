import sys

__all__ = ("Pos", "pos_highlight", "Printer")


class Pos:
    __slots__ = ("index", "file_name", "file_text", "line_num", "char_num")

    def __init__(
        self,
        file_name: str,
        file_text: str,
        index: int,
        line_num: int,
        character_num: int,
    ):
        self.index = index
        self.file_name = file_name
        self.file_text = file_text
        self.line_num = line_num
        self.char_num = character_num

    def __repr__(self) -> str:
        return f"Pos(line {self.line_num}, char {self.char_num})"

    def advance(self, new_line=False) -> None:
        if new_line:
            self.char_num = 1
            self.line_num += 1
        else:
            self.char_num += 1
        self.index += 1

    def copy(self):
        return Pos(
            self.file_name, self.file_text, self.index, self.line_num, self.char_num
        )


def pos_highlight(text: str, pos_start: Pos, pos_end: Pos) -> str:
    result = ""

    # Calculate indices
    idx_start = max(text.rfind("\n", 0, pos_start.index), 0)
    idx_end = text.find("\n", idx_start + 1)
    if idx_end < 0:
        idx_end = len(text)

    # Generate each line
    line_count = pos_end.line_num - pos_start.line_num + 1

    for i in range(line_count):
        # Calculate line columns
        line = text[idx_start:idx_end]
        col_start = pos_start.char_num if i == 0 else 0
        col_end = pos_end.char_num if i == line_count - 1 else len(line) - 1

        # Append to result
        result += line + "\n"
        result += " " * col_start + "~" * (col_end - col_start)

        # Re-calculate indices
        idx_start = idx_end
        idx_end = text.find("\n", idx_start + 1)
        if idx_end < 0:
            idx_end = len(text)

    return result.replace("\t", "")


class _CLR:
    __slots__ = ()
    RESET = "\u001b[0m"
    DEBUG_CLR = "\u001b[30;1m"
    ERROR_CLR = "\u001b[31;1m"
    TIME_CLR = "\u001b[36m"
    SEPERATOR_CLR = ""


class Printer:
    __slots__ = ()

    @staticmethod
    def debug_p(*values) -> None:
        print(end=_CLR.DEBUG_CLR)
        print(*values)
        print(end=_CLR.RESET)

    @staticmethod
    def seperator_p() -> None:
        print(end=_CLR.SEPERATOR_CLR)

    @staticmethod
    def internal_error_p(*values) -> None:
        print(end=_CLR.ERROR_CLR)
        print(*values)
        print(end=_CLR.RESET)

    @staticmethod
    def output_p(text, end="") -> None:
        sys.stdout.write(text + end)
    
    @staticmethod
    def time_p(title):
        print(end=_CLR.TIME_CLR)
        print(title)
        print(end=_CLR.RESET)
