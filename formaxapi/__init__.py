"""
framework - Class-based routing with dynamic Pydantic model generation for FastAPI.

Routes defined inside the class with @route decorator.
Typed input via UserRoute.schema() — request body auto-validated.
SelfDerivedModel for bulk operations — derive schemas from own fields.
"""

from .core import (
    FieldConfig, Chain, RouteField, FieldInfo, SelfDerivedModel,
    RouteBase, ModelFactory, RouteMetaclass,
    route, route_factory,
)

__all__ = [
    'FieldConfig', 'Chain', 'RouteField', 'FieldInfo', 'SelfDerivedModel',
    'RouteBase', 'ModelFactory', 'RouteMetaclass',
    'route', 'route_factory',
]
