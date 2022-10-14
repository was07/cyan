from __future__ import annotations
import time

# for type hinting
import cyan.ast as ast
from typing import Callable

from cyan.tokens import T
from cyan.utils import Printer
from cyan.parser import parse_ast
from cyan.tokenizer import tokenize
from cyan.exceptions import RTError
from cyan.types import (
    RTResult,
    Number,
    Bool,
    String,
    Function,
    BuiltInFunction,
    NoneObj,
    SymbolMap,
    Context,
)

__all__ = ("Interpreter", "build_in_out", "interpret", "run", "run_debug")


class Interpreter:
    def visit(self, node: ast.NodeSelf, ctx: Context) -> RTResult:
        method_name = f"visit_{type(node).__name__}"
        method: Callable[[ast.NodeSelf, Context], RTResult] = getattr(
            self, method_name, self.no_visit_method
        )
        return method(node, ctx)

    def no_visit_method(self, node, ctx: Context):
        Printer.internal_error(
            f"Interpreter: visit_{type(node).__name__} method is not defined"
        )
        exit()

    def visit_StatementsNode(self, node: ast.StatementsNode, ctx: Context):
        res = RTResult()
        nodes = []

        for statement in node.statements:
            nodes.append(res.register(self.visit(statement, ctx)))
            if res.error:
                return res

        if len(nodes) == 1:
            return res.success(nodes[0])
        return res
    
    @staticmethod
    def visit_PassNode(node: ast.PassNode, ctx: Context):
        return RTResult().success(NoneObj())

    @staticmethod
    def visit_NumberNode(node: ast.NumberNode, ctx: Context):
        return RTResult().success(
            Number(node.tok.value)
            .set_pos(node.start_pos, node.end_pos)
            .set_context(ctx)
        )

    @staticmethod
    def visit_LiteralNode(node: ast.LiteralNode, ctx: Context):
        res = RTResult()
        if node.tok.value == "true":
            return res.success(
                Bool(True).set_pos(node.start_pos, node.end_pos).set_context(ctx)
            )
        elif node.tok.value == "false":
            return res.success(
                Bool(False).set_pos(node.start_pos, node.end_pos).set_context(ctx)
            )
        elif node.tok.value == "none":
            return res.success(
                NoneObj().set_pos(node.start_pos, node.end_pos).set_context(ctx)
            )

    @staticmethod
    def visit_StringNode(node: ast.StringNode, ctx: Context):
        return RTResult().success(
            String(node.tok.value)
            .set_pos(node.start_pos, node.end_pos)
            .set_context(ctx)
        )

    @staticmethod
    def visit_VarAccessNode(node: ast.VarAccessNode, ctx: Context):
        res = RTResult()
        var_name = node.var_name.value
        value = ctx.symbol_map.get(var_name)

        if value is None:
            return res.failure(
                RTError(node.start_pos, node.end_pos, f"'{var_name}' not defined", ctx)
            )

        value = value.copy().set_pos(node.start_pos, node.end_pos)

        return res.success(value)

    def visit_VarAssignNode(self, node: ast.VarAssignNode, ctx: Context):
        res = RTResult()
        var_name = node.var_name.value

        value = res.register(self.visit(node.value, ctx))
        if res.error:
            return res

        ctx.symbol_map.set(var_name, value)
        return res.success(value)

    def visit_BinOpNode(self, node: ast.BinOpNode, ctx):
        res = RTResult()
        left = res.register(self.visit(node.left, ctx))
        if res.error:
            return res
        right = res.register(self.visit(node.right, ctx))
        if res.error:
            return res

        oper = node.oper
        result = None
        error = None

        if oper.is_type(T.PLUS):
            result, error = left.operate_plus(right)
        elif oper.is_type(T.MINUS):
            result, error = left.operate_minus(right)
        elif oper.is_type(T.MUL):
            result, error = left.operate_mul(right)
        elif oper.is_type(T.DIV):
            result, error = left.operate_div(right)
        elif oper.is_type(T.POW):
            result, error = left.operate_pow(right)
        elif oper.is_type(T.EE):
            result, error = left.compare_eq(right)
        elif oper.is_type(T.NE):
            result, error = left.compare_ne(right)
        elif oper.is_type(T.LT):
            result, error = left.compare_lt(right)
        elif oper.is_type(T.GT):
            result, error = left.compare_gt(right)
        elif oper.is_type(T.LTE):
            result, error = left.compare_lte(right)
        elif oper.is_type(T.GTE):
            result, error = left.compare_gte(right)
        elif oper.is_equals(T.KW, "and"):
            result, error = left.logic_and(right)
        elif oper.is_equals(T.KW, "or"):
            result, error = left.logic_or(right)

        if error:
            return res.failure(error.set_pos(node.start_pos, node.end_pos))
        else:
            return res.success(result.set_pos(node.start_pos, node.end_pos))

    def visit_UnaryOpNode(self, node: ast.UnaryOpNode, ctx: Context):
        res = RTResult()
        number = res.register(self.visit(node.node, ctx))
        if res.error:
            return res

        error = None

        if node.oper.is_type(T.MINUS):
            number, error = number.operate_mul(Number(-1))
        elif node.oper.is_equals(T.KW, "not"):
            number, error = number.logic_not()

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.start_pos, node.end_pos))

    def visit_IfBlockNode(self, node: ast.IfBlockNode, ctx: Context):
        res = RTResult()
        cond = res.register(self.visit(node.case[0], ctx))
        if res.error:
            return res
        if cond.is_truthy():
            value = res.register(self.visit(node.case[1], ctx))
        else:
            value = res.register(self.visit(node.else_expr, ctx))

        if res.error:
            return res
        return res.success(value)

    def visit_WhileNode(self, node: ast.WhileNode, ctx: Context):
        res = RTResult()
        cond = res.register(self.visit(node.condition, ctx))
        if res.error:
            return res

        while cond.is_truthy():
            value = res.register(self.visit(node.body, ctx))
            if res.error:
                return res
            cond = res.register(self.visit(node.condition, ctx))
            if res.error:
                return res

        return res.success(NoneObj())

    @staticmethod
    def visit_FuncDefNode(node: ast.FuncDefNode, ctx: Context):
        res = RTResult()

        func = (
            Function(node.name, node.parameters, node.body)
            .set_pos(node.start_pos, node.end_pos)
            .set_context(ctx)
        )
        ctx.symbol_map.set(node.name, func)

        return res.success(func)

    def visit_FuncCallNode(self, node: ast.FuncCallNode, ctx: Context):
        res = RTResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, ctx))
        if res.error:
            return res
        value_to_call = value_to_call.copy().set_pos(node.start_pos, node.end_pos)

        for arg_node in node.arguments:
            args.append(res.register(self.visit(arg_node, ctx)))
            if res.error:
                return res

        value_to_call: Function
        return_value = res.register(
            # value_to_call.execute(args),
            self.call_function(value_to_call, args)
        )

        if res.error:
            res.error.set_pos(node.start_pos, node.end_pos)
            return res

        return res.success(return_value)

    def call_function(self, fn: Function | BuiltInFunction, args) -> RTResult:
        res = RTResult()

        context = Context(
            fn.name,
            fn.ctx,
            fn.start_pos,
            SymbolMap(getattr(fn.ctx, "symbol_map", None)),
        )

        if fn.n_params != len(args) and fn.n_params != float("inf"):
            return res.failure(
                RTError(
                    fn.start_pos,
                    fn.end_pos,
                    ("Too many" if len(args) > fn.n_params else "Not enough")
                    + f" ({len(args)}) arguments given into {fn.name}, takes {fn.n_params}",
                    context,
                )
            )

        if isinstance(fn, BuiltInFunction):
            # If function is a builtin
            value = res.register(fn.function(*args))
            if res.error:
                return res

            return res.success(value)

        # setting parameters to given values
        for i in range(fn.n_params):
            parameter = fn.params[i]
            arg = args[i]
            context.symbol_map.set(parameter.value, arg)

        value = res.register(self.visit(fn.body, context))
        if res.error:
            return res
        else:
            return res.success(value)


def build_in_out(*values):
    if len(values) != 1:
        Printer.output(" ".join(map(str, values)))
    else:
        Printer.output(str(values[0]))
    Printer.output("\n")
    return RTResult().success(NoneObj())


def build_in_inp():
    inp = String(input())
    return RTResult().success(inp)


def interpret(node: ast.Node, context: Context) -> RTResult:
    interpreter = Interpreter()
    return interpreter.visit(node, context)


def run(filename: str, code: str):
    tokens, error = tokenize(filename, code)

    if error is not None:
        return None, error

    node, parse_error = parse_ast(tokens)

    if parse_error is not None:
        return None, parse_error

    context = Context("<module>", symbol_map=GLOBAL_SYMBOL_MAP)
    res = interpret(node, context)

    if res.error:
        return None, res.error
    else:
        return res.value, None


def run_debug(filename: str, code: str):
    start_t = time.perf_counter()
    t1 = start_t
    tokens, error = tokenize(filename, code)
    t2 = time.perf_counter()

    Printer.time(f"Tokenized {round(t2 - t1, 5)}s")
    Printer.debug("TOKENS: ", *tokens)

    if error is not None:
        return None, error

    t1 = time.perf_counter()
    node, parse_error = parse_ast(tokens)
    t2 = time.perf_counter()

    Printer.time(f"Parsed {round(t2 - t1, 5)}s")
    Printer.debug("NODE: ", node)

    if parse_error is not None:
        return None, parse_error

    t1 = time.perf_counter()
    context = Context("<module>", symbol_map=GLOBAL_SYMBOL_MAP)
    res = interpret(node, context)
    t2 = time.perf_counter()

    Printer.time(f"Run time {round(t2 - t1, 5)}s, Total {round(t2 - start_t, 5)}s")

    if res.error:
        return None, res.error
    else:
        return res.value, None


GLOBAL_SYMBOL_MAP = SymbolMap()
GLOBAL_SYMBOL_MAP.set("out", BuiltInFunction("out", build_in_out, float("inf")))
GLOBAL_SYMBOL_MAP.set("inp", BuiltInFunction("inp", build_in_inp, 0))
GLOBAL_SYMBOL_MAP.set("Bool", BuiltInFunction("Bool", Bool.converter, 1))
GLOBAL_SYMBOL_MAP.set("Num", BuiltInFunction("Num", Number.converter, 1))
GLOBAL_SYMBOL_MAP.set("Str", BuiltInFunction("Str", String.converter, 1))
