from cyan.tokens import T, Token
from cyan.utils import Pos
from cyan.exceptions import InvalidSyntaxError, InvalidCharacterError

car_tok_map = {
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

literals = ("true", "false", "none")
keywords = (
    "let", "and", "or", "not", "if", "then", "elif", "else", "while", "fun"
)


# Tokenizer/Lexer
class Tokenizer:
    def __init__(self, file_name, text: str):
        self.file_name = file_name
        self.text = text
        self.text_length = len(text)
        self.car = None
        self.pos: Pos = Pos(file_name, text, -1, 0, -1)
        self.advance()

    def advance(self):
        self.pos.advance(self.car == "\n")
        if self.pos.index >= self.text_length:
            self.car = None
            return
        self.car = self.text[self.pos.index]

    def parse(self) -> tuple:
        tokens = []

        while self.car is not None:
            if self.car.isnumeric():
                tokens.append(self.get_number())
                continue
            elif self.car.isalpha():
                tokens.append(self.get_identifier())
                continue
            elif self.car in car_tok_map:
                tokens.append(
                    Token(car_tok_map[self.car], pos_start=self.pos)
                )
            elif self.car in ("'", '"'):
                tokens.append(self.get_string())
            elif self.car == "*":
                tokens.append(self.get_mul_or_paw())
                continue
            elif self.car == "!":
                token, error = self.get_not_equals()
                if error:
                    return [], error
                tokens.append(token)
            elif self.car == "=":
                tokens.append(self.get_equals())
            elif self.car == "<":
                tokens.append(self.get_less_then())
            elif self.car == ">":
                tokens.append(self.get_greater_then())
            elif self.car.isspace():
                if self.car == "\n":
                    tokens.append(Token(T.NEWLINE, pos_start=self.pos))
            else:
                return [], InvalidCharacterError(
                    self.pos, f"Character {repr(self.car)} is invalid."
                )
            self.advance()

        tokens.append(Token(T.EOF, pos_start=self.pos))
        return tokens, None

    def get_number(self):
        num_str = ""
        dot_count = 0
        pos_start = self.pos.copy()

        while self.car is not None and (self.car.isnumeric() or self.car == "."):
            if self.car == ".":
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += "."
            else:
                num_str += self.car
            self.advance()

        if dot_count == 0:
            return Token(
                T.INT, int(num_str), pos_start=pos_start, pos_end=self.pos.copy()
            )
        else:
            return Token(
                T.FLOAT, float(num_str), pos_start=pos_start, pos_end=self.pos.copy()
            )

    def get_string(self):
        # self.car can be ' or "
        start_pos = self.pos.copy()
        content = ""
        quote_used = self.car
        self.advance()

        while self.car != quote_used:
            content += self.car
            self.advance()

        return Token(T.STRING, content, pos_start=start_pos, pos_end=self.pos.copy())

    def get_mul_or_paw(self):
        start_pos = self.pos.copy()
        self.advance()

        if self.car == "*":
            self.advance()
            tok = T.POW
        else:
            tok = T.MUL

        return Token(tok, pos_start=start_pos, pos_end=self.pos.copy())

    def get_not_equals(self):
        start_pos = self.pos.copy()
        self.advance()

        if self.car == "=":
            self.advance()
            return Token(T.NE, pos_start=start_pos, pos_end=self.pos.copy()), None

        self.advance()
        return None, InvalidSyntaxError(start_pos, self.pos.copy(), "Invalid Syntax")

    def get_equals(self):
        tok_type = T.EQ
        start_pos = self.pos.copy()
        self.advance()

        if self.car == "=":
            tok_type = T.EE
            self.advance()

        return Token(tok_type, pos_start=start_pos, pos_end=self.pos.copy())

    def get_less_then(self):
        pos_start = self.pos.copy()
        tok_type = T.LT
        self.advance()

        if self.car == "=":
            tok_type = T.LTE
            self.advance()

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

    def get_greater_then(self):
        pos_start = self.pos.copy()
        tok_type = T.GT
        self.advance()

        if self.car == "=":
            tok_type = T.GTE
            self.advance()

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

    def get_identifier(self):
        iden: str = ""
        pos_start = self.pos.copy()

        while self.car is not None and (self.car.isalnum() or self.car == "_"):
            iden += self.car
            self.advance()

        if iden in keywords:
            toke_type = T.KW
        elif iden in literals:
            toke_type = T.LITERAL
        else:
            toke_type = T.IDENTIFIER

        return Token(toke_type, iden, pos_start, self.pos.copy())


def tokenize(file_name, text: str):
    maker = Tokenizer(file_name, text)
    res = maker.parse()
    return res
