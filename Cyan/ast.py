# for type hinting
from typing import Optional
from cyan.tokens import Token
from cyan.utils import Pos


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
        statements = ", ".join(repr(statement) for statement in self.statements)
        return f"Statements({statements})"


class NumberNode(Node):
    def __init__(self, tok):
        self.tok = tok
        super().set_pos(tok.start_pos, tok.end_pos)

    def __repr__(self):
        return str(self.tok)


class LiteralNode(Node):
    def __init__(self, tok):
        self.tok = tok
        super().set_pos(tok.start_pos, tok.end_pos)

    def __repr__(self):
        return self.tok.value


class StringNode(Node):
    def __init__(self, tok):
        self.tok = tok
        super().set_pos(tok.start_pos, tok.end_pos)


class BinOpNode(Node):
    def __init__(self, left, oper, right):
        self.left = left
        self.oper = oper
        self.right = right
        super().set_pos(left.start_pos, right.end_pos)

    def __repr__(self):
        return f"({self.left}, {self.oper}, {self.right})"


class UnaryOpNode(Node):
    def __init__(self, oper, node):
        self.oper = oper
        self.node = node
        super().set_pos(oper.start_pos, node.end_pos)

    def __repr__(self):
        return f"({self.oper}, {self.node})"


class VarAccessNode(Node):
    def __init__(self, var_name):
        self.var_name = var_name
        super().set_pos(var_name.start_pos, var_name.end_pos)

    def __repr__(self):
        return f"({self.var_name})"


class VarAssignNode(Node):
    def __init__(self, var_name, value):
        self.var_name = var_name
        self.value = value
        super().set_pos(var_name.start_pos, value.end_pos)

    def __repr__(self):
        return f"({self.var_name} = {self.value})"


class IfBlockNode(Node):
    def __init__(self, case: tuple, else_expr):
        self.case = case
        self.else_expr = else_expr
        super().set_pos(case[0].start_pos)

    def __repr__(self):
        return f"(if {self.case[0]} then {self.case[1]} else {self.else_expr})"


class WhileNode(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
        super().set_pos(condition.start_pos, body.end_pos)

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
