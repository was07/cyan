# for type hinting
from typing import Optional
from cyan.utils import Pos


class T:
    __slots__ = ()
    INT = "INT"
    FLOAT = "FLOAT"
    STRING = "STRING"

    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    POW = "POW"

    EQ = "EQ"    # =
    EE = "EE"    # ==
    NE = "NE"    # !=
    LT = "LT"    # <
    GT = "GT"    # >
    LTE = "LTE"  # <=
    GTE = "GTE"  # >=

    L_PAREN = "L_PAREN"    # (
    R_PAREN = "R_PAREN"    # )
    L_CPAREN = "L_CPAREN"  # {
    R_CPAREN = "R_CPAREN"  # }

    LITERAL = "LITERAL"
    IDENTIFIER = "IDENTIFIER"
    KW = "KW"

    COLON = "COLON"            # :
    SEMI_COLON = "SEMI_COLON"  # ;
    COMMA = "COMMA"            # ,
    NEWLINE = "NEWLINE"        # \n
    EOF = "EOF"


class Token:
    __slots__ = ("start_pos", "end_pos", "type_", "value")
    start_pos: Optional[Pos]
    end_pos: Optional[Pos]

    def __init__(self, tok_type, value=None, start_pos: Optional[Pos]=None, end_pos: Optional[Pos]=None):
        self.tok_type = tok_type
        self.value = value

        if start_pos is not None:
            self.start_pos = start_pos.copy()
            self.end_pos = start_pos.copy()
            self.end_pos.advance()

        if end_pos is not None:
            self.end_pos = end_pos.copy()

    def __repr__(self) -> str:
        if self.value is None:
            return self.tok_type
        else:
            return f"{self.tok_type}:{self.value}"

    def is_type(self, *tokens: tuple[T]) -> bool:
        return self.tok_type in tokens

    def is_equals(self, token_name, value) -> bool:
        return self.tok_type == token_name and self.value == value
