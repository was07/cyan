from typing import Optional, Self
from cyan.utils import Pos
from cyan.exceptions import RTError


class Object:
    type_name: str
    start_pos: Optional[Pos]
    end_pos: Optional[Pos]
    ctx: Optional["Context"]

    def __init__(self, name="Object"):
        self.type_name = name
        self.start_pos = None
        self.end_pos = None
        self.ctx = None

    def __str__(self) -> str:
        return f"<object-of-type-{self.type_name}>"

    def __repr__(self) -> str:
        return self.__str__()

    def set_pos(self, pos_start=None, pos_end=None) -> Self:
        self.start_pos = pos_start
        self.end_pos = pos_end
        return self

    def set_context(self, context=None) -> Self:
        self.ctx = context
        return self

    def is_truthy(self):
        return Bool(True)

    # arithmetic operations
    def operate_plus(self, other):
        return None, self.not_supported("+ operator", other)

    def operate_minus(self, other):
        return None, self.not_supported("- operator", other)

    def operate_mul(self, other):
        return None, self.not_supported("* operator", other)

    def operate_div(self, other):
        return None, self.not_supported("/ operator", other)

    def operate_pow(self, other):
        return None, self.not_supported("^ operator", other)

    # boolean operations
    def compare_eq(self, other):
        return None, self.not_supported("== operator", other)

    def compare_ne(self, other):
        return None, self.not_supported("!= operator", other)

    def compare_gt(self, other):
        return None, self.not_supported("> operator", other)

    def compare_lt(self, other):
        return None, self.not_supported("< operator", other)

    def compare_gte(self, other):
        return None, self.not_supported(">= operator", other)

    def compare_lte(self, other):
        return None, self.not_supported("<= operator", other)

    # logical operations
    def logic_and(self, other):
        return None, self.not_supported("'and' logic", other)

    def logic_or(self, other):
        return None, self.not_supported("'or' logic", other)

    def logic_not(self):
        return None, self.not_supported("'not' logic", self)

    def not_supported(self, what_is_not_supported, other=None):
        return RTError(
            self.start_pos,
            self.end_pos,
            f"{self.type_name} does not support {what_is_not_supported} with {other.type_name}",
            self.ctx,
        )


class NoneObj(Object):
    def __init__(self):
        super().__init__("NoneObj")

    def __str__(self):
        return "none"

    def is_truthy(self):
        return Bool(False)

    @staticmethod
    def copy():
        return NoneObj()


class Bool(Object):
    def __init__(self, value):
        Object.__init__(self, "Bool")
        self.value = bool(value)
        self.pos_start = None
        self.pos_end = None
        self.context = None

    def __str__(self):
        return "true" if self.value else "false"

    def __bool__(self):
        return self.value

    @staticmethod
    def converter(obj: Object):
        return RTResult().success(
            Bool(obj.is_truthy())
        )

    def is_truthy(self):
        return Bool(self.value)

    def copy(self):
        return (
            Bool(self.value)
            .set_pos(self.pos_start, self.pos_end)
            .set_context(self.context)
        )

    # converters
    def to_number(self):
        return RTResult().success(
            Number(int(self.value))
        )

    # logical operators
    def logic_and(self, other):
        return Bool(self.value and other.value).set_context(self.context), None

    def logic_or(self, other):
        return Bool(self.value or other.value).set_context(self.context), None

    def logic_not(self):
        return Bool(not self.value).set_context(self.context), None


class Number(Object):
    def __init__(self, value):
        super().__init__("Number")
        self.value = value

        self.pos_start = None
        self.pos_end = None
        self.context = None

    def __str__(self):
        return str(self.value)

    def __bool__(self):
        return bool(self.value)

    @staticmethod
    def converter(obj: Object = None):
        if obj is None:
            obj = Number(0)
        if isinstance(obj, Number):
            return RTResult().success(Number(obj.value))
        if hasattr(obj, "to_Number"):
            return obj.to_Number()
        else:
            return RTResult().failure(
                RTError(
                    obj.start_pos,
                    obj.end_pos,
                    f"Cannot convert {obj.type_name} to Number",
                    obj.ctx,
                )
            )

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_truthy(self):
        return Bool(bool(self.value))

    # arithmetic operations
    def operate_plus(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return Object.operate_plus(self, other)  # makes not supported error

    def operate_minus(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return Object.operate_minus(self, other)  # makes not supported error

    def operate_mul(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return Object.operate_mul(self, other)  # makes not supported error

    def operate_div(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end, "Division by Zero", self.context
                )
            return Number(self.value / other.value).set_context(self.context), None
        else:
            return Object.operate_div(self, other)  # makes not supported error

    def operate_pow(self, other):
        if isinstance(other, Number):
            return Number(self.value**other.value).set_context(self.context), None
        else:
            return Object.operate_pow(self, other)  # makes not supported error

    # boolean operations
    def compare_eq(self, other):
        if isinstance(other, Number):
            return Bool(self.value == other.value).set_context(self.context), None
        else:
            return Object.compare_eq(self, other)  # makes not supported error

    def compare_ne(self, other):
        if isinstance(other, Number):
            return Bool(self.value != other.value).set_context(self.context), None
        else:
            return Object.compare_ne(self, other)  # makes not supported error

    def compare_gt(self, other):
        if isinstance(other, Number):
            return Bool(self.value > other.value).set_context(self.context), None
        else:
            return Object.compare_gt(self, other)  # makes not supported error

    def compare_lt(self, other):
        if isinstance(other, Number):
            return Bool(self.value < other.value).set_context(self.context), None
        else:
            return Object.compare_lt(self, other)  # makes not supported error

    def compare_gte(self, other):
        if isinstance(other, Number):
            return Bool(self.value >= other.value).set_context(self.context), None
        else:
            return Object.compare_gte(self, other)  # makes not supported error

    def compare_lte(self, other):
        if isinstance(other, Number):
            return Bool(self.value <= other.value).set_context(self.context), None
        else:
            return Object.compare_lte(self, other)  # makes not supported error

    # logical operations
    def logic_and(self, other):
        if isinstance(other, Number):
            return Bool(int(self.value and other.value)).set_context(self.context), None
        else:
            return Object.logic_and(self, other)  # makes not supported error

    def logic_or(self, other):
        if isinstance(other, Number):
            return Bool(int(self.value or other.value)).set_context(self.context), None
        else:
            return Object.logic_or(self, other)  # makes not supported error

    def logic_not(self):
        return Bool(int(not self.value)).set_context(self.context), None


class String(Object):
    def __init__(self, value: str):
        super().__init__("String")
        self.value = value

    def __repr__(self):
        return f"'{self.value}'"

    def __str__(self):
        return str(self.value)

    @staticmethod
    def converter(obj: Object = None):
        res = RTResult()
        if obj is None:
            return res.success(String(""))
        elif isinstance(obj, String):
            return res.success(String(obj.value))
        else:
            return res.success(String(obj))

    def copy(self):
        return (
            String(self.value)
            .set_pos(self.start_pos, self.end_pos)
            .set_context(self.ctx)
        )

    def is_truthy(self):
        return Bool(self.value)

    # converters
    def to_number(self):
        self.value: str
        num_value = None
        try:
            num_value = int(self.value)
        except ValueError:
            try:
                num_value = float(self.value)
            except ValueError:
                return RTResult().failure(
                    RTError(
                        self.start_pos,
                        self.end_pos,
                        f"Cannot convert to Number: {self.value}",
                        self.ctx,
                    )
                )

        return RTResult().success(
            Number(num_value)
        )

    # arithmetic operations
    def operate_plus(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.ctx), None
        else:
            return Object.operate_plus(self, other)

    # boolean operations
    def compare_eq(self, other):
        return Bool(self.value == other.value).set_context(self.ctx), None

    def compare_ne(self, other):
        return Bool(self.value != other.value).set_context(self.ctx), None


class Function(Object):
    def __init__(self, name, parameters, body):
        Object.__init__(self)
        self.type_name = "Function"
        self.name = name
        self.params = parameters
        self.n_params = len(parameters)
        self.body = body

    def __str__(self):
        return f"<Function {self.name}>"

    def copy(self):
        copy = Function(self.name, self.params, self.body)
        copy.set_context(self.ctx)
        copy.set_pos(self.start_pos, self.end_pos)
        return copy


class BuiltInFunction(Object):
    def __init__(self, name: str, function: Function):
        Object.__init__(self)
        self.type_name = "BuiltInFunction"
        self.name = name
        self.function = function  # a function that has to return RTResult object

    def __str__(self):
        return f"<Built-in Function {self.name}>"

    def copy(self):
        copy = BuiltInFunction(self.name, self.function)
        copy.set_context(self.ctx)
        copy.set_pos(self.start_pos, self.end_pos)
        return copy

    def execute(self, args: list):
        res = RTResult()

        value = res.register(self.function(*args))
        if res.error:
            return res

        return res.success(value)


class RTResult:
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, res):
        if res.error:
            self.error = res.error
        return res.value

    def success(self, value):
        self.value = value
        return self

    def failure(self, error: RTError):
        self.error = error
        return self


class Context:
    def __init__(
        self, display_name, parent=None, parent_entry_pos=None, symbol_map=None
    ):
        self.display_name: str = display_name
        self.parent: Context = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_map: SymbolMap = symbol_map


class SymbolMap:
    def __init__(self, parent=None):
        self.symbol_map = {}
        self.parent = parent

    def get(self, var_name):
        value = self.symbol_map.get(var_name, None)
        if value is None and self.parent:
            return self.parent.get(var_name)
        return value

    def set(self, var_name, value):
        self.symbol_map[var_name] = value

    def remove(self, var_name):
        del self.symbol_map[var_name]
