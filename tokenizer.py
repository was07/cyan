from tokens import t
from tokens import Token

from utils import Pos, InvalidCharacterError, InvalidSyntaxError


car_tok_map = {
    '+': t.PLUS,
    '-': t.MINUS,
    '*': t.MUL,
    '/': t.DIV,
    '^': t.POW,
    '(': t.L_PAREN,
    ')': t.R_PAREN,
    ':': t.COLON,
    ',': t.COMMA
}

keywords = ('let', 'and', 'or', 'not', 'if', 'then', 'elif', 'else', 'fun')

literals = ('true', 'false')


# Tokenizer/Lexer
class Tokenizer:
    def __init__(self, file_name, text: str):
        self.file_name = file_name
        self.text = text
        self.text_length = len(text)
        self.car = None
        self.pos = Pos(file_name, text, -1, 0, -1)
        self.advance()
    
    def advance(self):
        self.pos.advance(self.car == '\n')
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
            if self.car.isalpha():
                tokens.append(self.get_identifier())
                continue
            elif self.car in car_tok_map:
                tokens.append(Token(car_tok_map[self.car], pos_start=self.pos))
            elif self.car == '!':
                token, error = self.get_not_equals()
                if error:
                    return [], error
                tokens.append(token)
            elif self.car == '=':
                tokens.append(self.get_equals())
            elif self.car == '<':
                tokens.append(self.get_less_then())
            elif self.car == '>':
                tokens.append(self.get_greater_then())
            elif self.car.isspace():
                if self.car == '\n':
                    tokens.append(Token(t.NEWLINE, pos_start=self.pos))
                pass
            else:
                return [], \
                       InvalidCharacterError(self.pos, f'Character {repr(self.car)} is invalid.')
            self.advance()
        
        tokens.append(Token(t.EOF, pos_start=self.pos))
        return tokens, None
    
    def get_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()
    
        while self.car is not None and (self.car.isnumeric() or self.car == '.'):
            if self.car == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.car
            self.advance()
    
        if dot_count == 0:
            return Token(t.INT, int(num_str), pos_start=pos_start, pos_end=self.pos.copy())
        else:
            return Token(t.FLOAT, float(num_str), pos_start=pos_start, pos_end=self.pos.copy())

    def get_not_equals(self):
        start_pos = self.pos.copy()
        self.advance()
    
        if self.car == '=':
            self.advance()
            return Token(t.NE, pos_start=start_pos, pos_end=self.pos.copy()), None
    
        self.advance()
        return None, InvalidSyntaxError(start_pos, self.pos.copy(), 'Invalid Syntax')

    def get_equals(self):
        tok_type = t.EQ
        start_pos = self.pos.copy()
        self.advance()
        
        if self.car == '=':
            tok_type = t.EE
            self.advance()
        
        return Token(tok_type, pos_start=start_pos, pos_end=self.pos.copy())
    
    def get_less_then(self):
        pos_start = self.pos.copy()
        tok_type = t.LT
        self.advance()
        
        if self.car == '=':
            tok_type = t.LTE
            self.advance()
        
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())
    
    def get_greater_then(self):
        pos_start = self.pos.copy()
        tok_type = t.GT
        self.advance()

        if self.car == '=':
            tok_type = t.GTE
            self.advance()

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

    def get_identifier(self):
        iden: str = ''
        pos_start = self.pos.copy()
        
        while self.car is not None and (self.car.isalnum() or self.car == '_'):
            iden += self.car
            self.advance()
        
        if iden in keywords:
            toke_type = t.KW
        elif iden in literals:
            toke_type = t.LITERAL
        else:
            toke_type = t.IDENTIFIER
        
        return Token(toke_type, iden, pos_start, self.pos.copy())


def tokenize(file_name, text: str):
    maker = Tokenizer(file_name, text)
    res = maker.parse()
    return res
