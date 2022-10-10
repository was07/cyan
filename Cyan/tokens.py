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

    def __init__(self, type_, value=None, start_pos=None, end_pos=None):
        self.type_ = type_
        self.value = value

        if start_pos:
            self.start_pos = start_pos.copy()
            self.end_pos = start_pos.copy()
            self.end_pos.advance()

        if end_pos:
            self.end_pos = end_pos.copy()

    def __repr__(self) -> str:
        return self.type_ + ("" if self.value is None else ":" + str(self.value))

    def is_type(self, *token_name_s) -> bool:
        return self.type_ in token_name_s

    def is_equals(self, token_name, value) -> bool:
        return self.type_ == token_name and self.value == value
