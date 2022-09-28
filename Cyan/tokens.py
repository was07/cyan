# for type hinting
from typing import Optional
from cyan.utils import Pos


class T:
    INT = "INT"
    FLOAT = "FLOAT"
    STRING = "STRING"

    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    POW = "POW"

    EE = "EE"  # ==
    NE = "NE"
    LT = "LT"
    GT = "GT"
    LTE = "LTE"
    GTE = "GTE"

    EQ = "EQ"  # =

    L_PAREN = "L_PAREN"
    R_PAREN = "R_PAREN"
    L_CPAREN = "L_CPAREN"
    R_CPAREN = "R_CPAREN"

    LITERAL = "LITERAL"
    IDENTIFIER = "IDENTIFIER"
    KW = "KW"

    COLON = "COLON"
    SEMI_COLON = "SEMI_COLON"
    COMMA = "COMMA"
    NEWLINE = "NEWLINE"
    EOF = "EOF"


class Token:
    pos_start: Optional[Pos]
    pos_end: Optional[Pos]

    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type_ = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end.copy()

    def __repr__(self):
        return self.type_ + ("" if self.value is None else ":" + str(self.value))

    def is_type(self, *token_name_s):
        return self.type_ in token_name_s

    def is_equals(self, token_name, value):
        return self.type_ == token_name and self.value == value
