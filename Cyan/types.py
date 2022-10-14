"""RTResult and all Cyan objects"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from cyan.exceptions import RTError

if TYPE_CHECKING:
    from typing import Optional, TypeVar, Any, TypeAlias, Callable
    from cyan.ast import Node
    from cyan.tokens import Token
    from cyan.utils import Pos

    ObjectSelf = TypeVar("ObjectSelf", bound="Object")
    OperationResult: TypeAlias = tuple[ObjectSelf, None]
    BooleanOperationResult: TypeAlias = tuple["Bool", None]

    OperationError: TypeAlias = tuple[None, RTError]


__all__ = (
    "RTResult",
    "Context",
    "SymbolMap",
    "NoneObj",
    "Bool",
    "Number",
    "String",
    "Function",
    "BuiltInFunction",
)


class RTResult:
    """Run-Time Result, used with Interpreter"""
    __slots__ = ("value", "error")

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


class Object:
    """Base class for Cyan objects"""
    value: Optional[Any] = None
    ctx: Optional[Context] = None
    start_pos: Optional[Pos] = None
    end_pos: Optional[Pos] = None

    def __init__(self, name="Object"):
        self.type_name: str = name

    def __str__(self) -> str:
        return f"<object-of-type-{self.type_name}>"

    __repr__ = __str__

    @classmethod
    def is_same_type(cls, other: Object) -> bool:
        """
        return whether the current type is the same as the other type
        """
        return isinstance(other, cls)

    def set_pos(
        self, pos_start: Optional[Pos] = None, pos_end: Optional[Pos] = None
    ) -> ObjectSelf:
        self.start_pos = pos_start
        self.end_pos = pos_end
        return self

    def set_context(self, context: Optional[Context] = None) -> ObjectSelf:
        self.ctx = context
        return self

    def copy(self) -> ObjectSelf:
        copy = self.__class__(self.value)
        copy.set_pos(self.start_pos, self.end_pos)
        copy.set_context(self.ctx)

        return copy

    def is_truthy(self) -> Bool:
        return Bool(True)

    # arithmetic operations
    def operate_plus(self, other) -> OperationResult | OperationError:
        return self.operation_not_supported("+ operator", other)

    def operate_minus(self, other) -> OperationResult | OperationError:
        return self.operation_not_supported("- operator", other)

    def operate_mul(self, other) -> OperationResult | OperationError:
        return self.operation_not_supported("* operator", other)

    def operate_div(self, other) -> OperationResult | OperationError:
        return self.operation_not_supported("/ operator", other)

    def operate_pow(self, other) -> OperationResult | OperationError:
        return self.operation_not_supported("^ operator", other)

    # boolean operations
    def compare_eq(self, other) -> BooleanOperationResult | OperationError:
        return self.operation_not_supported("== operator", other)

    def compare_ne(self, other) -> BooleanOperationResult | OperationError:
        return self.operation_not_supported("!= operator", other)

    def compare_gt(self, other) -> BooleanOperationResult | OperationError:
        return self.operation_not_supported("> operator", other)

    def compare_lt(self, other) -> BooleanOperationResult | OperationError:
        return self.operation_not_supported("< operator", other)

    def compare_gte(self, other) -> BooleanOperationResult | OperationError:
        return self.operation_not_supported(">= operator", other)

    def compare_lte(self, other) -> BooleanOperationResult | OperationError:
        return self.operation_not_supported("<= operator", other)

    # logical operations
    def logic_and(self, other) -> BooleanOperationResult | OperationError:
        return self.operation_not_supported("'and' logic", other)

    def logic_or(self, other) -> BooleanOperationResult | OperationError:
        return self.operation_not_supported("'or' logic", other)

    def logic_not(self) -> BooleanOperationResult | OperationError:
        return self.operation_not_supported("'not' logic", self)

    def operation_not_supported(self, operation: str, other: Object) -> OperationError:
        return None, RTError(
            self.start_pos,
            self.end_pos,
            f"{self.type_name} does not support {operation} with {other.type_name}",
            self.ctx,
        )


class NoneObj(Object):
    def __init__(self):
        super().__init__("NoneObj")

    def __str__(self) -> str:
        return "none"

    def is_truthy(self) -> Bool:
        return Bool(False)

    @staticmethod
    def copy() -> ObjectSelf:
        return NoneObj()


class Bool(Object):
    def __init__(self, value):
        super().__init__("Bool")
        self.value: bool = bool(value)

    def __str__(self) -> str:
        return "true" if self.value else "false"

    def __bool__(self) -> bool:
        return self.value

    @staticmethod
    def converter(obj: Object) -> RTResult:
        return RTResult().success(Bool(obj.is_truthy()))

    def is_truthy(self) -> Bool:
        return Bool(self.value)

    # converters
    def to_Number(self) -> RTResult:
        return RTResult().success(Number(int(self.value)))

    # logical operators
    def logic_and(self, other):
        return Bool(self.value and other.value).set_context(self.ctx), None

    def logic_or(self, other):
        return Bool(self.value or other.value).set_context(self.ctx), None

    def logic_not(self):
        return Bool(not self.value).set_context(self.ctx), None


class Number(Object):
    def __init__(self, value):
        super().__init__("Number")
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __bool__(self) -> bool:
        return bool(self.value)

    @staticmethod
    def converter(obj: Optional[Object] = None) -> RTResult:
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

    def is_truthy(self) -> Bool:
        return Bool(bool(self.value))

    # arithmetic operations
    def operate_plus(self, other: Number):
        if self.is_same_type(other):
            return Number(self.value + other.value).set_context(self.ctx), None
        else:
            return Object.operate_plus(self, other)  # makes not supported error

    def operate_minus(self, other: Number):
        if self.is_same_type(other):
            return Number(self.value - other.value).set_context(self.ctx), None
        else:
            return Object.operate_minus(self, other)  # makes not supported error

    def operate_mul(self, other: Number):
        if self.is_same_type(other):
            return Number(self.value * other.value).set_context(self.ctx), None
        else:
            return Object.operate_mul(self, other)  # makes not supported error

    def operate_div(self, other: Number):
        if self.is_same_type(other):
            if other.value == 0:
                return None, RTError(
                    other.start_pos, other.end_pos, "Division by Zero", self.ctx
                )
            return Number(self.value / other.value).set_context(self.ctx), None
        else:
            return Object.operate_div(self, other)  # makes not supported error

    def operate_pow(self, other: Number):
        if self.is_same_type(other):
            return Number(self.value**other.value).set_context(self.ctx), None
        else:
            return Object.operate_pow(self, other)  # makes not supported error

    # boolean operations
    def compare_eq(self, other: Number):
        if self.is_same_type(other):
            return Bool(self.value == other.value).set_context(self.ctx), None
        else:
            return Object.compare_eq(self, other)  # makes not supported error

    def compare_ne(self, other: Number):
        if self.is_same_type(other):
            return Bool(self.value != other.value).set_context(self.ctx), None
        else:
            return Object.compare_ne(self, other)  # makes not supported error

    def compare_gt(self, other: Number):
        if self.is_same_type(other):
            return Bool(self.value > other.value).set_context(self.ctx), None
        else:
            return Object.compare_gt(self, other)  # makes not supported error

    def compare_lt(self, other: Number):
        if self.is_same_type(other):
            return Bool(self.value < other.value).set_context(self.ctx), None
        else:
            return Object.compare_lt(self, other)  # makes not supported error

    def compare_gte(self, other: Number):
        if self.is_same_type(other):
            return Bool(self.value >= other.value).set_context(self.ctx), None
        else:
            return Object.compare_gte(self, other)  # makes not supported error

    def compare_lte(self, other: Number):
        if self.is_same_type(other):
            return Bool(self.value <= other.value).set_context(self.ctx), None
        else:
            return Object.compare_lte(self, other)  # makes not supported error

    # logical operations
    def logic_and(self, other: Number):
        if self.is_same_type(other):
            return Bool(int(self.value and other.value)).set_context(self.ctx), None
        else:
            return Object.logic_and(self, other)  # makes not supported error

    def logic_or(self, other: Number):
        if self.is_same_type(other):
            return Bool(int(self.value or other.value)).set_context(self.ctx), None
        else:
            return Object.logic_or(self, other)  # makes not supported error

    def logic_not(self):
        return Bool(int(not self.value)).set_context(self.ctx), None


class String(Object):
    def __init__(self, value: str):
        super().__init__("String")
        self.value = value

    def __repr__(self) -> str:
        return f"'{self.value}'"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    def converter(obj: Optional[Object] = None) -> RTResult:
        res = RTResult()

        if obj is None:
            value = ""
        elif isinstance(obj, String):
            value = obj.value
        else:
            value = obj

        return res.success(String(value))

    def is_truthy(self) -> Bool:
        return Bool(self.value)

    # converters
    def to_Number(self) -> RTResult:
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

        return RTResult().success(Number(num_value))

    # arithmetic operations
    def operate_plus(self, other: String):
        if self.is_same_type(other):
            return String(self.value + other.value).set_context(self.ctx), None
        else:
            return Object.operate_plus(self, other)

    # boolean operations
    def compare_eq(self, other: String):
        return Bool(self.value == other.value).set_context(self.ctx), None

    def compare_ne(self, other: String):
        return Bool(self.value != other.value).set_context(self.ctx), None


class Function(Object):
    """User-defined cyan function"""
    def __init__(self, name: str, parameters: list[Token], body: Node):
        super().__init__("Function")
        self.name = name
        self.params = parameters
        self.n_params = len(parameters)  # can be inf
        self.body = body

    def __str__(self) -> str:
        return f"<Function {self.name}>"

    def copy(self) -> ObjectSelf:
        return (
            Function(self.name, self.params, self.body)
            .set_context(self.ctx)
            .set_pos(self.start_pos, self.end_pos)
        )


class BuiltInFunction(Object):
    def __init__(
        self,
        name: str,
        function: Callable[[Object | tuple[Object]], RTResult],
        n_params: int,
    ):
        super().__init__("BuiltInFunction")
        self.name = name
        self.function = function  # a function that has to return RTResult object
        self.n_params = n_params  # can be inf

    def __str__(self) -> str:
        return f"<Built-in Function {self.name}>"

    def copy(self) -> ObjectSelf:
        return (
            BuiltInFunction(self.name, self.function, self.n_params)
            .set_context(self.ctx)
            .set_pos(self.start_pos, self.end_pos)
        )


@dataclass(slots=True, frozen=True)
class Context:
    """Stores info about different scopes in cyan code"""
    name: str
    parent: Optional[Context] = None
    parent_entry_pos: Optional[Pos] = None
    symbol_map: Optional[SymbolMap] = None


class SymbolMap:
    """Stores values of identifiers in cyan code"""
    __slots__ = ("symbol_map", "parent")

    def __init__(self, parent=None):
        self.symbol_map: dict[str, Any] = {}
        self.parent = parent

    def get(self, name: str):
        value = self.symbol_map.get(name, None)
        if value is None and self.parent:
            return self.parent.get(name)
        else:
            return value

    def set(self, name: str, value) -> None:
        """set value of an identifier"""
        self.symbol_map[name] = value

    def remove(self, name: str) -> None:
        """delete an identifers value"""
        del self.symbol_map[name]
