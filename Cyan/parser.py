from typing import Optional

from cyan.tokens import T
from cyan.exceptions import InvalidSyntaxError
import cyan.ast as ast
from cyan.tokens import Token

__all__ = ("ParseResult", "Parser", "parse_ast")


class ParseResult:
    __slots__ = (
        "error",
        "node",
        "last_registered_advance_count",
        "advancements",
        "to_reverse_count",
    )

    def __init__(self):
        self.error = None
        self.node = None
        self.last_registered_advance_count = 0
        self.advancements = 0
        self.to_reverse_count = 0

    def register_advancement(self):
        self.last_registered_advance_count = 1
        self.advancements += 1

    def register_adv(self):
        self.advancements += 1
        pass

    def register(self, res) -> ast.Node:
        self.advancements += res.advancements
        if res.error:
            self.error = res.error
        return res.node

    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advancements
            return None
        return self.register(res)

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if error is not None or self.advancements == 0:
            self.error = error
        return self


class Parser:
    __slots__ = ("tokens", "crr_idx", "crr_tok")

    def __init__(self, tokens):
        self.tokens = tokens
        self.crr_idx = -1
        self.crr_tok: Optional[Token] = None
        self.advance()  # self.cur_tok will be set up in this call

    def advance(self):
        self.crr_idx += 1
        if self.crr_idx < len(self.tokens):
            self.crr_tok: Token = self.tokens[self.crr_idx]
        return self.crr_tok

    def reverse(self, amount=1):
        self.crr_idx -= amount
        self.update_current_tok()
        return self.crr_tok

    def update_current_tok(self):
        if self.crr_idx >= 0 and self.crr_idx < len(self.tokens):
            self.crr_tok = self.tokens[self.crr_idx]

    def next_tok(self):
        if self.crr_idx + 1 < len(self.tokens):
            return self.tokens[self.crr_idx + 1]

    def parse(self):
        res = self.statements()
        if res.error is None and (not self.crr_tok.is_type(T.EOF, T.NEWLINE)):
            from cyan.utils import Printer

            Printer.debug_p(self.crr_tok)
            res.failure(
                InvalidSyntaxError(
                    self.crr_tok.start_pos, self.crr_tok.end_pos, "Invalid Syntax"
                ).set_ecode("p")
            )
            return res
        return res

    def statements(self):
        res = ParseResult()
        pos_start = self.crr_tok.start_pos.copy()
        statements = []

        while self.crr_tok.is_type(T.NEWLINE, T.SEMI_COLON):
            res.register_adv()
            self.advance()

        statement = res.register(self.expr())
        if res.error:
            return res
        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0
            while self.crr_tok.is_type(T.NEWLINE, T.SEMI_COLON):
                res.register_adv()
                self.advance()
                newline_count += 1
            if not newline_count:
                more_statements = False

            if not more_statements:
                break
            statement = res.try_register(self.expr())

            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)

        return res.success(
            ast.StatementsNode(statements, pos_start, self.crr_tok.end_pos)
        )

    def expr(self):
        res = ParseResult()

        if self.crr_tok.is_equals(T.KW, "let"):
            res.register_adv()
            self.advance()

            if not self.crr_tok.is_type(T.IDENTIFIER):
                return res.failure(
                    InvalidSyntaxError(
                        self.crr_tok.start_pos,
                        self.crr_tok.end_pos,
                        "Expected identifier",
                    )
                )

            var_name = self.crr_tok
            res.register_adv()
            self.advance()

            if not self.crr_tok.is_type(T.EQ):
                return res.failure(
                    InvalidSyntaxError(
                        self.crr_tok.start_pos, self.crr_tok.end_pos, "Expected '='"
                    )
                )

            res.register_adv()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res

            return res.success(ast.VarAssignNode(var_name, expr))

        node = res.register(
            self.bin_oper(self.comp_expr, ((T.KW, "and"), (T.KW, "or")))
        )
        if res.error:
            return res

        if res.error:
            return res.failure(
                InvalidSyntaxError(
                    self.crr_tok.start_pos,
                    self.crr_tok.end_pos,
                    "Expected Expression: let, int, float, identifier, '+', '-' or '('",
                ).set_ecode("xp")
            )

        return res.success(node)

    def call(self):
        res = ParseResult()

        atom = res.register(self.atom())
        if res.error:
            return res

        if self.crr_tok.is_type(T.L_PAREN):
            args = []
            res.register_adv()
            self.advance()

            if not self.crr_tok.is_type(T.R_PAREN):
                arg = res.register(self.expr())
                if res.error:
                    return res
                args.append(arg)

                while self.crr_tok.is_type(T.COMMA):
                    res.register_adv()
                    self.advance()

                    arg = res.register(self.expr())
                    if res.error:
                        return res
                    args.append(arg)

                    if self.crr_tok.is_type(T.R_PAREN):
                        break
                    elif not self.crr_tok.is_type(T.COMMA):
                        return res.failure(
                            InvalidSyntaxError(
                                self.crr_tok.start_pos,
                                self.crr_tok.end_pos,
                                "Expected ',' or ')'",
                            )
                        )

                if not self.crr_tok.is_type(T.R_PAREN):
                    return res.failure(
                        InvalidSyntaxError(
                            self.crr_tok.start_pos, self.crr_tok.end_pos, "Expected ')'"
                        )
                    )
            pos_end = self.crr_tok.end_pos.copy()
            res.register_adv()
            self.advance()

            return res.success(
                ast.FuncCallNode(atom, args).set_pos(atom.start_pos, pos_end)
            )
        return res.success(atom)

    def atom(self):
        res = ParseResult()
        tok = self.crr_tok

        if tok.is_type(T.INT, T.FLOAT):
            res.register_adv()
            self.advance()
            return res.success(ast.NumberNode(tok))

        elif tok.is_type(T.LITERAL):
            res.register_adv()
            self.advance()
            return res.success(ast.LiteralNode(tok))

        elif tok.is_type(T.L_PAREN):
            res.register_adv()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.crr_tok.is_type(T.R_PAREN):
                res.register_adv()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(
                    InvalidSyntaxError(
                        self.crr_tok.start_pos, self.crr_tok.end_pos, "Expected ')'"
                    )
                )

        elif tok.is_type(T.IDENTIFIER):
            res.register_adv()
            self.advance()
            return res.success(ast.VarAccessNode(tok))

        elif tok.is_type(T.STRING):
            res.register_adv()
            self.advance()
            return res.success(ast.StringNode(tok))

        elif tok.is_equals(T.KW, "if"):
            node = res.register(self.if_expr())

            return res.success(node)

        elif tok.is_equals(T.KW, "fun"):
            node = res.register(self.func_def())

            return res.success(node)

        elif tok.is_equals(T.KW, "while"):
            node = res.register(self.while_expr())

            return res.success(node)

        return res.failure(
            InvalidSyntaxError(
                tok.start_pos,
                tok.end_pos,
                "Expected Value: identifier, int, float, '+', '-' or '('",
            )
        )

    def factor(self):
        res = ParseResult()
        tok = self.crr_tok

        if tok.is_type(T.PLUS, T.MINUS):
            res.register_adv()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(ast.UnaryOpNode(tok, factor))

        return self.power()

    def term(self):
        return self.bin_oper(self.factor, (T.MUL, T.DIV))

    def power(self):
        return self.bin_oper(self.call, (T.POW,), self.factor)

    def arith_expr(self):
        return self.bin_oper(self.term, (T.PLUS, T.MINUS))

    def comp_expr(self):
        res = ParseResult()
        if self.crr_tok.is_equals(T.KW, "not"):
            op_tok = self.crr_tok
            res.register_adv()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error:
                return res

            return res.success(ast.UnaryOpNode(op_tok, node))

        node = res.register(
            self.bin_oper(self.arith_expr, (T.EE, T.NE, T.LT, T.GT, T.LTE, T.GTE))
        )

        if res.error:
            return res

        return res.success(node)

    def bin_oper(self, func_left, operators, func_right=None):
        if func_right is None:
            func_right = func_left

        res = ParseResult()

        left = res.register(func_left())
        if res.error:
            return res

        while (
            self.crr_tok.is_type(*operators)
            or (self.crr_tok.type_, self.crr_tok.value) in operators
        ):
            op_tok = self.crr_tok
            res.register_adv()
            self.advance()
            right = res.register(func_right())
            if res.error:
                return res

            left = ast.BinOpNode(left, op_tok, right)

        return res.success(left)

    def if_expr(self):
        # self.cur_tok is KW:if
        res = ParseResult()
        res.register_adv()
        self.advance()

        cond = res.register(self.comp_expr())
        if res.error:
            return res

        if not self.crr_tok.is_equals(T.KW, "then"):
            return res.failure(
                InvalidSyntaxError(
                    self.crr_tok.start_pos, self.crr_tok.end_pos, "Expected 'then'"
                )
            )
        res.register_adv()
        self.advance()

        expr = res.register(self.expr())
        if res.error:
            return res

        if not self.crr_tok.is_equals(T.KW, "else"):
            return res.failure(
                InvalidSyntaxError(
                    self.crr_tok.start_pos, self.crr_tok.end_pos, "Expected 'else'"
                )
            )

        res.register_adv()
        self.advance()

        else_expr = res.register(self.expr())
        if res.error:
            return res

        return res.success(ast.IfBlockNode((cond, expr), else_expr))

    def func_def(self):
        # self.cur_tok is KW:fun
        res = ParseResult()
        res.register_adv()
        name = ""
        pos_start = self.crr_tok.start_pos
        res.register_adv()
        self.advance()

        if self.crr_tok.is_type(T.IDENTIFIER):
            name = self.crr_tok.value
            res.register_adv()
            self.advance()

        if not self.crr_tok.is_type(T.L_PAREN):
            return res.failure(
                InvalidSyntaxError(
                    self.crr_tok.start_pos,
                    self.crr_tok.end_pos,
                    "Expected '('" if name else "Expected Identifier or '('",
                )
            )
        res.register_adv()
        self.advance()

        parameters = []
        if self.crr_tok.is_type(T.IDENTIFIER):
            parameters.append(self.crr_tok)
            res.register_adv()
            self.advance()

            while self.crr_tok.is_type(T.COMMA):
                res.register_adv()
                self.advance()

                if self.crr_tok.is_type(T.IDENTIFIER):
                    parameters.append(self.crr_tok)
                    res.register_adv()
                    self.advance()
                elif self.crr_tok.is_type(T.R_PAREN):
                    break
                else:
                    return res.failure(
                        InvalidSyntaxError(
                            self.crr_tok.start_pos,
                            self.crr_tok.end_pos,
                            "Expected ',' or ')'",
                        )
                    )

        if not self.crr_tok.is_type(T.R_PAREN):
            return res.failure(
                InvalidSyntaxError(
                    self.crr_tok.start_pos, self.crr_tok.end_pos, "Invalid Syntax"
                ).set_ecode("fd")
            )

        res.register_adv()
        self.advance()

        if not self.crr_tok.is_type(T.L_CPAREN):
            return res.failure(
                InvalidSyntaxError(
                    self.crr_tok.start_pos, self.crr_tok.end_pos, "Expected '{'"
                )
            )
        res.register_adv()
        self.advance()

        statements = res.register(self.statements())
        if res.error:
            return res

        if not self.crr_tok.is_type(T.R_CPAREN):
            return res.failure(
                InvalidSyntaxError(
                    self.crr_tok.start_pos, self.crr_tok.end_pos, "Expected '}'"
                )
            )

        res.register_adv()
        self.advance()

        return res.success(
            ast.FuncDefNode(name, parameters, statements).set_pos(
                pos_start, statements.end_pos
            )
        )

    def while_expr(self):
        # self.cur_tok is KW:while
        res = ParseResult()
        res.register_adv()
        p_start = self.crr_tok.start_pos.copy()
        self.advance()

        cond = res.register(self.comp_expr())
        if res.error:
            return res

        if not self.crr_tok.is_type(T.L_CPAREN):
            return res.failure(
                InvalidSyntaxError(
                    self.crr_tok.start_pos, self.crr_tok.end_pos, "Expected '{'"
                )
            )
        res.register_adv()
        self.advance()

        statements = res.register(self.statements())
        if res.error:
            return res

        if not self.crr_tok.is_type(T.R_CPAREN):
            return res.failure(
                InvalidSyntaxError(
                    self.crr_tok.start_pos, self.crr_tok.end_pos, "Expected '}'"
                )
            )
        p_end = self.crr_tok.end_pos.copy()

        res.register_adv()
        self.advance()

        return res.success(
            ast.WhileNode(cond, statements).set_pos(cond.start_pos, p_end)
        )


def parse_ast(tokens):
    parser = Parser(tokens)
    res = parser.parse()
    return res.node, res.error
