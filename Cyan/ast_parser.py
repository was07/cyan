from tokens import T

from utils import InvalidSyntaxError

# for type hinting
from typing import Optional
from tokens import Token
from utils import Pos


class Node:
    pos_start: Optional[Pos]
    pos_end: Optional[Pos]

    def set_pos(self, pos_start: Pos, pos_end: Optional[Pos] = None):
        self.pos_start = pos_start
        if pos_end is not None:
            self.pos_end = pos_end

        return self

    def __repr__(self):
        return type(self).__name__


class StatementsNode(Node):
    def __init__(self, statements, pos_start, pos_end):
        self.statements = statements
        super().set_pos(pos_start, pos_end)

    def __repr__(self):
        stmts = ", ".join(repr(statement) for statement in self.statements)
        return f"Statements({stmts})"


class NumberNode(Node):
    def __init__(self, tok):
        self.tok = tok
        super().set_pos(tok.pos_start, tok.pos_end)

    def __repr__(self):
        return str(self.tok)


class LiteralNode(Node):
    def __init__(self, tok):
        self.tok = tok
        super().set_pos(tok.pos_start, tok.pos_end)

    def __repr__(self):
        return self.tok.value


class StringNode(Node):
    def __init__(self, tok):
        self.tok = tok
        super().set_pos(tok.pos_start, tok.pos_end)


class BinOpNode(Node):
    def __init__(self, left, oper, right):
        self.left = left
        self.oper = oper
        self.right = right
        super().set_pos(left.pos_start, right.pos_end)

    def __repr__(self):
        return f"({self.left}, {self.oper}, {self.right})"


class UnaryOpNode(Node):
    def __init__(self, oper, node):
        self.oper = oper
        self.node = node
        super().set_pos(oper.pos_start, node.pos_end)

    def __repr__(self):
        return f"({self.oper}, {self.node})"


class VarAccessNode(Node):
    def __init__(self, var_name):
        self.var_name = var_name
        super().set_pos(var_name.pos_start, var_name.pos_end)

    def __repr__(self):
        return f"({self.var_name})"


class VarAssignNode(Node):
    def __init__(self, var_name, value):
        self.var_name = var_name
        self.value = value
        super().set_pos(var_name.pos_start, value.pos_end)

    def __repr__(self):
        return f"({self.var_name} = {self.value})"


class IfBlockNode(Node):
    def __init__(self, case: tuple, else_expr):
        self.case = case
        self.else_expr = else_expr
        super().set_pos(case[0].pos_start)

    def __repr__(self):
        return f"(if {self.case[0]} then {self.case[1]} else {self.else_expr})"


class WhileNode(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
        super().set_pos(condition.pos_start, body.pos_end)

    def __repr__(self):
        return f"(while {self.condition} do {self.body})"


class FuncDefNode(Node):
    def __init__(self, name: str, parameters: list[Token], body: Node):
        self.name = name or "[lambda]"
        self.parameters = parameters
        self.body = body


class FuncCallNode(Node):
    def __init__(self, node_to_call: Node, arguments: list[Node]):
        self.node_to_call = node_to_call
        self.arguments = arguments

    def __repr__(self):
        return f"(FuncCall:{self.node_to_call})"


class ParseResult:
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

    def register(self, res) -> Node:
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
    def __init__(self, tokens):
        self.tokens = tokens
        self.cur_index = -1
        self.cur_tok: Optional[Token] = None
        self.advance()  # self.cur_tok will be set up in this call

    def advance(self):
        self.cur_index += 1
        if self.cur_index < len(self.tokens):
            self.cur_tok: Token = self.tokens[self.cur_index]
        return self.cur_tok

    def reverse(self, amount=1):
        self.cur_index -= amount
        self.update_current_tok()
        return self.cur_tok

    def update_current_tok(self):
        if self.cur_index >= 0 and self.cur_index < len(self.tokens):
            self.cur_tok = self.tokens[self.cur_index]

    def next_tok(self):
        if self.cur_index + 1 < len(self.tokens):
            return self.tokens[self.cur_index + 1]

    def parse(self):
        res = self.statements()
        if res.error is None and (not self.cur_tok.is_type(T.EOF, T.NEWLINE)):
            from Cyan.utils import Printer

            Printer.debug_p(self.cur_tok)
            res.failure(
                InvalidSyntaxError(
                    self.cur_tok.pos_start, self.cur_tok.pos_end, "Invalid Syntax"
                ).set_ecode("p")
            )
            return res
        return res

    def statements(self):
        res = ParseResult()
        pos_start = self.cur_tok.pos_start.copy()
        statements = []

        while self.cur_tok.is_type(T.NEWLINE, T.SEMI_COLON):
            res.register_adv()
            self.advance()

        statement = res.register(self.expr())
        if res.error:
            return res
        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0
            while self.cur_tok.is_type(T.NEWLINE, T.SEMI_COLON):
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

        return res.success(StatementsNode(statements, pos_start, self.cur_tok.pos_end))

    def expr(self):
        res = ParseResult()

        if self.cur_tok.is_equals(T.KW, "let"):
            res.register_adv()
            self.advance()

            if not self.cur_tok.is_type(T.IDENTIFIER):
                return res.failure(
                    InvalidSyntaxError(
                        self.cur_tok.pos_start,
                        self.cur_tok.pos_end,
                        "Expected identifier",
                    )
                )

            var_name = self.cur_tok
            res.register_adv()
            self.advance()

            if not self.cur_tok.is_type(T.EQ):
                return res.failure(
                    InvalidSyntaxError(
                        self.cur_tok.pos_start, self.cur_tok.pos_end, "Expected '='"
                    )
                )

            res.register_adv()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res

            return res.success(VarAssignNode(var_name, expr))

        node = res.register(
            self.bin_oper(self.comp_expr, ((T.KW, "and"), (T.KW, "or")))
        )
        if res.error:
            return res

        if res.error:
            return res.failure(
                InvalidSyntaxError(
                    self.cur_tok.pos_start,
                    self.cur_tok.pos_end,
                    "Expected Expression: let, int, float, identifier, '+', '-' or '('",
                ).set_ecode("xp")
            )

        return res.success(node)

    def call(self):
        res = ParseResult()

        atom = res.register(self.atom())
        if res.error:
            return res

        if self.cur_tok.is_type(T.L_PAREN):
            args = []
            res.register_adv()
            self.advance()

            if not self.cur_tok.is_type(T.R_PAREN):
                arg = res.register(self.expr())
                if res.error:
                    return res
                args.append(arg)

                while self.cur_tok.is_type(T.COMMA):
                    res.register_adv()
                    self.advance()

                    arg = res.register(self.expr())
                    if res.error:
                        return res
                    args.append(arg)

                    if self.cur_tok.is_type(T.R_PAREN):
                        break
                    elif not self.cur_tok.is_type(T.COMMA):
                        return res.failure(
                            InvalidSyntaxError(
                                self.cur_tok.pos_start,
                                self.cur_tok.pos_end,
                                "Expected ',' or ')'",
                            )
                        )

                if not self.cur_tok.is_type(T.R_PAREN):
                    return res.failure(
                        InvalidSyntaxError(
                            self.cur_tok.pos_start, self.cur_tok.pos_end, "Expected ')'"
                        )
                    )
            pos_end = self.cur_tok.pos_end.copy()
            res.register_adv()
            self.advance()

            return res.success(
                FuncCallNode(atom, args).set_pos(atom.pos_start, pos_end)
            )
        return res.success(atom)

    def atom(self):
        res = ParseResult()
        tok = self.cur_tok

        if tok.is_type(T.INT, T.FLOAT):
            res.register_adv()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.is_type(T.LITERAL):
            res.register_adv()
            self.advance()
            return res.success(LiteralNode(tok))

        elif tok.is_type(T.L_PAREN):
            res.register_adv()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.cur_tok.is_type(T.R_PAREN):
                res.register_adv()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(
                    InvalidSyntaxError(
                        self.cur_tok.pos_start, self.cur_tok.pos_end, "Expected ')'"
                    )
                )

        elif tok.is_type(T.IDENTIFIER):
            res.register_adv()
            self.advance()
            return res.success(VarAccessNode(tok))

        elif tok.is_type(T.STRING):
            res.register_adv()
            self.advance()
            return res.success(StringNode(tok))

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
                tok.pos_start,
                tok.pos_end,
                "Expected Value: identifier, int, float, '+', '-' or '('",
            )
        )

    def factor(self):
        res = ParseResult()
        tok = self.cur_tok

        if tok.is_type(T.PLUS, T.MINUS):
            res.register_adv()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def term(self):
        return self.bin_oper(self.factor, (T.MUL, T.DIV))

    def power(self):
        return self.bin_oper(self.call, (T.POW,), self.factor)

    def arith_expr(self):
        return self.bin_oper(self.term, (T.PLUS, T.MINUS))

    def comp_expr(self):
        res = ParseResult()
        if self.cur_tok.is_equals(T.KW, "not"):
            op_tok = self.cur_tok
            res.register_adv()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error:
                return res

            return res.success(UnaryOpNode(op_tok, node))
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
            self.cur_tok.is_type(*operators)
            or (self.cur_tok.type_, self.cur_tok.value) in operators
        ):
            op_tok = self.cur_tok
            res.register_adv()
            self.advance()
            right = res.register(func_right())
            if res.error:
                return res

            left = BinOpNode(left, op_tok, right)

        return res.success(left)

    def if_expr(self):
        # self.cur_tok is KW:if
        res = ParseResult()
        res.register_adv()
        self.advance()

        cond = res.register(self.comp_expr())
        if res.error:
            return res

        if not self.cur_tok.is_equals(T.KW, "then"):
            return res.failure(
                InvalidSyntaxError(
                    self.cur_tok.pos_start, self.cur_tok.pos_end, "Expected 'then'"
                )
            )
        res.register_adv()
        self.advance()

        expr = res.register(self.expr())
        if res.error:
            return res

        if not self.cur_tok.is_equals(T.KW, "else"):
            return res.failure(
                InvalidSyntaxError(
                    self.cur_tok.pos_start, self.cur_tok.pos_end, "Expected 'else'"
                )
            )

        res.register_adv()
        self.advance()

        else_expr = res.register(self.expr())
        if res.error:
            return res

        return res.success(IfBlockNode((cond, expr), else_expr))

    def func_def(self):
        # self.cur_tok is KW:fun
        res = ParseResult()
        res.register_adv()
        name = ""
        pos_start = self.cur_tok.pos_start
        res.register_adv()
        self.advance()

        if self.cur_tok.is_type(T.IDENTIFIER):
            name = self.cur_tok.value
            res.register_adv()
            self.advance()

        if not self.cur_tok.is_type(T.L_PAREN):
            return res.failure(
                InvalidSyntaxError(
                    self.cur_tok.pos_start,
                    self.cur_tok.pos_end,
                    "Expected '('" if name else "Expected Identifier or '('",
                )
            )
        res.register_adv()
        self.advance()

        parameters = []
        if self.cur_tok.is_type(T.IDENTIFIER):
            parameters.append(self.cur_tok)
            res.register_adv()
            self.advance()

            while self.cur_tok.is_type(T.COMMA):
                res.register_adv()
                self.advance()

                if self.cur_tok.is_type(T.IDENTIFIER):
                    parameters.append(self.cur_tok)
                    res.register_adv()
                    self.advance()
                elif self.cur_tok.is_type(T.R_PAREN):
                    break
                else:
                    return res.failure(
                        InvalidSyntaxError(
                            self.cur_tok.pos_start,
                            self.cur_tok.pos_end,
                            "Expected ',' or ')'",
                        )
                    )

        if not self.cur_tok.is_type(T.R_PAREN):
            return res.failure(
                InvalidSyntaxError(
                    self.cur_tok.pos_start, self.cur_tok.pos_end, "Invalid Syntax"
                ).set_ecode("fd")
            )

        res.register_adv()
        self.advance()

        if not self.cur_tok.is_type(T.L_CPAREN):
            return res.failure(
                InvalidSyntaxError(
                    self.cur_tok.pos_start, self.cur_tok.pos_end, "Expected '{'"
                )
            )
        res.register_adv()
        self.advance()

        statements = res.register(self.statements())
        if res.error:
            return res

        if not self.cur_tok.is_type(T.R_CPAREN):
            return res.failure(
                InvalidSyntaxError(
                    self.cur_tok.pos_start, self.cur_tok.pos_end, "Expected '}'"
                )
            )

        res.register_adv()
        self.advance()

        return res.success(
            FuncDefNode(name, parameters, statements).set_pos(
                pos_start, statements.pos_end
            )
        )

    def while_expr(self):
        # self.cur_tok is KW:while
        res = ParseResult()
        res.register_adv()
        p_start = self.cur_tok.pos_start.copy()
        self.advance()

        cond = res.register(self.comp_expr())
        if res.error:
            return res

        if not self.cur_tok.is_type(T.L_CPAREN):
            return res.failure(
                InvalidSyntaxError(
                    self.cur_tok.pos_start, self.cur_tok.pos_end, "Expected '{'"
                )
            )
        res.register_adv()
        self.advance()

        statements = res.register(self.statements())
        if res.error:
            return res

        if not self.cur_tok.is_type(T.R_CPAREN):
            return res.failure(
                InvalidSyntaxError(
                    self.cur_tok.pos_start, self.cur_tok.pos_end, "Expected '}'"
                )
            )
        p_end = self.cur_tok.pos_end.copy()

        res.register_adv()
        self.advance()

        return res.success(WhileNode(cond, statements).set_pos(cond.pos_start, p_end))


def make_ast(tokens):
    parser = Parser(tokens)
    res = parser.parse()
    return res.node, res.error
