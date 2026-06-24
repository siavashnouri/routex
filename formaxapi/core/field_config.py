"""FieldConfig - Base class for schema type configurations."""

from __future__ import annotations
from typing import Any, Callable


_UNSET = object()


class Chain:
    """Compose multiple functions to run sequentially on a field value."""

    def __init__(self, *funcs: Callable):
        self.funcs = funcs

    def __call__(self, v: Any) -> Any:
        result = v
        for func in self.funcs:
            result = func(result)
        return result


class FieldConfig:
    """Extend to define schema types."""

    required: bool = False
    default: Any = _UNSET
    default_factory: Callable | None = None
    alias: str | None = None
    description: str | None = None
    type_override: type | None = None
    exclude: bool = False
    frozen: bool = False
    apply_func: Callable | None = None
    before: bool = True  # True = before validators, False = after validators
    metadata: dict | None = None

    def __init__(self, **overrides):
        for key, value in overrides.items():
            if hasattr(self, key) or key in self.__class__.__dict__:
                setattr(self, key, value)

    def __repr__(self):
        attrs = {k: v for k, v in self.__dict__.items() if v is not _UNSET and v is not None and v is not False}
        return f"{self.__name__}({attrs})"

    @property
    def __name__(self):
        return self.__class__.__name__
