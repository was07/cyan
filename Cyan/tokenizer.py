from cyan.tokens import T, Token
from cyan.utils import Pos
from cyan.exceptions import InvalidSyntaxError, InvalidCharacterError

__all__ = ("Tokenizer", "tokenize")

CHAR_TOKEN_MAP: dict[str, str] = {
    "+": T.PLUS,
    "-": T.MINUS,
    "/": T.DIV,
    "(": T.L_PAREN,
    ")": T.R_PAREN,
    "{": T.L_CPAREN,
    "}": T.R_CPAREN,
    ":": T.COLON,
    ";": T.SEMI_COLON,
    ",": T.COMMA,
}

LITERALS = frozenset(["true", "false", "none"])
KEYWORDS = frozenset(
    ["let", "and", "or", "not", "if", "then", "elif", "else", "while", "fun", "pass"]
)

TokenResult = tuple[Token, None] | tuple[None, InvalidSyntaxError]


# Tokenizer/Lexer
class Tokenizer:
    __slots__ = ("file_name", "text", "text_length", "char", "pos")

    def __init__(self, file_name: str, text: str):
        self.file_name: str = file_name
        self.text: str = text
        self.text_length: int = len(text)
        self.char: str | None = None
        self.pos = Pos(file_name, text, -1, 0, -1)
        self.advance()

    def advance(self) -> None:
        """Move to next token position"""
        self.pos.advance(self.char == "\n")
        if self.pos.idx >= self.text_length:
            self.char = None
            return

        self.char = self.text[self.pos.idx]

    def get_number(self) -> Token:
        num_str = ""
        dot_count = 0
        pos_start = self.pos.copy()

        while self.char is not None and self.char.isnumeric() or self.char == ".":
            if self.char == ".":
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += "."
            else:
                num_str += self.char
            self.advance()

        if dot_count == 0:
            return Token(
                T.INT, int(num_str), start_pos=pos_start, end_pos=self.pos.copy()
            )
        else:
            return Token(
                T.FLOAT, float(num_str), start_pos=pos_start, end_pos=self.pos.copy()
            )

    def get_string(self) -> Token:
        # self.char can be ' or "
        start_pos = self.pos.copy()
        content = ""
        quote_used = self.char
        self.advance()

        while self.char != quote_used:
            content += self.char
            self.advance()

        return Token(T.STRING, content, start_pos=start_pos, end_pos=self.pos.copy())

    def get_mul_or_paw(self) -> Token:
        start_pos = self.pos.copy()
        self.advance()

        if self.char == "*":
            self.advance()
            tok = T.POW
        else:
            tok = T.MUL

        return Token(tok, start_pos=start_pos, end_pos=self.pos.copy())

    def get_not_equals(self) -> TokenResult:
        start_pos = self.pos.copy()
        self.advance()

        if self.char == "=":
            self.advance()
            return Token(T.NE, start_pos=start_pos, end_pos=self.pos.copy()), None

        self.advance()
        return None, InvalidSyntaxError(start_pos, self.pos.copy(), "Invalid Syntax")

    def get_equals(self) -> Token:
        tok_type = T.EQ
        start_pos = self.pos.copy()
        self.advance()

        if self.char == "=":
            tok_type = T.EE
            self.advance()

        return Token(tok_type, start_pos=start_pos, end_pos=self.pos.copy())

    def get_less_then(self) -> Token:
        pos_start = self.pos.copy()
        tok_type = T.LT
        self.advance()

        if self.char == "=":
            tok_type = T.LTE
            self.advance()

        return Token(tok_type, start_pos=pos_start, end_pos=self.pos.copy())

    def get_greater_then(self) -> Token:
        pos_start = self.pos.copy()
        tok_type = T.GT
        self.advance()

        if self.char == "=":
            tok_type = T.GTE
            self.advance()

        return Token(tok_type, start_pos=pos_start, end_pos=self.pos.copy())

    def get_identifier(self) -> Token:
        ident: str = ""
        pos_start = self.pos.copy()

        while self.char is not None and (self.char.isalnum() or self.char == "_"):
            ident += self.char
            self.advance()

        if ident in KEYWORDS:
            toke_type = T.KW
        elif ident in LITERALS:
            toke_type = T.LITERAL
        else:
            toke_type = T.IDENTIFIER

        return Token(toke_type, ident, pos_start, self.pos.copy())

    def parse(self):
        """parse code"""
        tokens: list[Token] = []

        while self.char is not None:
            if self.char.isnumeric():
                tokens.append(self.get_number())
                continue
            elif self.char.isalpha():
                tokens.append(self.get_identifier())
                continue
            elif self.char in CHAR_TOKEN_MAP:
                tokens.append(Token(CHAR_TOKEN_MAP[self.char], start_pos=self.pos))
            elif self.char in ("'", '"'):
                tokens.append(self.get_string())
            elif self.char == "*":
                tokens.append(self.get_mul_or_paw())
                continue
            elif self.char == "!":
                token, error = self.get_not_equals()
                if error:
                    return [], error
                tokens.append(token)
            elif self.char == "=":
                tokens.append(self.get_equals())
            elif self.char == "<":
                tokens.append(self.get_less_then())
            elif self.char == ">":
                tokens.append(self.get_greater_then())
            elif self.char.isspace():
                if self.char == "\n":
                    tokens.append(Token(T.NEWLINE, start_pos=self.pos))
            elif self.char == "#":  # Comment getting ignored
                while self.char not in ("\n", None):
                    self.advance()
                continue
            else:
                return [], InvalidCharacterError(
                    self.pos, f"Character {repr(self.char)} is invalid."
                )
            self.advance()

        tokens.append(Token(T.EOF, start_pos=self.pos))
        return tokens, None


def tokenize(file_name: str, text: str):
    maker = Tokenizer(file_name, text)
    res = maker.parse()
    return res
