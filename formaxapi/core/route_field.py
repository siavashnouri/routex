"""RouteField and FieldInfo."""

from __future__ import annotations
from typing import Any, Callable
from pydantic.fields import FieldInfo as PydanticFieldInfo
from .field_config import FieldConfig, _UNSET


# Pydantic FieldInfo attribute names (to separate from schema_configs)
_PYDANTIC_FIELD_ATTRS = frozenset(PydanticFieldInfo.__slots__)


class FieldInfo:
    __slots__ = ('name', 'annotation', 'default', 'default_factory', 'configs',
                 'db_field', 'alias', 'description', 'field_info_kwargs', 'metadata')

    def __init__(self, name, annotation, default=_UNSET, default_factory=None,
                 configs=None, db_field=None, alias=None, description=None,
                 field_info_kwargs=None, metadata=None):
        self.name = name
        self.annotation = annotation
        self.default = default
        self.default_factory = default_factory
        self.configs = configs or {}
        self.db_field = db_field or alias or name
        self.alias = alias
        self.description = description
        self.field_info_kwargs = field_info_kwargs or {}
        self.metadata = metadata

    def get_config(self, schema_type: str) -> FieldConfig | None:
        return self.configs.get(schema_type)

    def has_config(self, schema_type: str) -> bool:
        return schema_type in self.configs


class RouteField(PydanticFieldInfo):
    """Declarative field with per-schema configs.

    Inherits from Pydantic's FieldInfo, so it works in both RouteBase and BaseModel:

        # In RouteBase — schema configs work
        class UserRoute(RouteBase):
            title: str = RouteField(add=Add(), edit=Edit())

        # In BaseModel — Pydantic Field params work
        class MyModel(BaseModel):
            title: str = RouteField(alias="x", description="test")
    """

    def __init__(self, default: Any = _UNSET, *, default_factory: Callable | None = None,
                 alias: str | None = None, validation_alias: str | None = None,
                 serialization_alias: str | None = None,
                 description: str | None = None, title: str | None = None,
                 exclude: bool = False, frozen: bool = False,
                 deprecated: str | None = None,
                 json_schema_extra: dict | None = None,
                 validate_default: bool = False,
                 repr: bool = True,
                 **kwargs: Any):
        # Extract schema_configs (FieldConfig instances) from all kwargs
        self.schema_configs = {k: v for k, v in kwargs.items() if isinstance(v, FieldConfig)}

        # Build kwargs for Pydantic FieldInfo
        # These are the params Pydantic FieldInfo stores as direct attributes
        pydantic_kwargs = {}
        if default is not _UNSET:
            pydantic_kwargs['default'] = default
        if default_factory is not None:
            pydantic_kwargs['default_factory'] = default_factory
        if alias is not None:
            pydantic_kwargs['alias'] = alias
        if validation_alias is not None:
            pydantic_kwargs['validation_alias'] = validation_alias
        if serialization_alias is not None:
            pydantic_kwargs['serialization_alias'] = serialization_alias
        if description is not None:
            pydantic_kwargs['description'] = description
        if title is not None:
            pydantic_kwargs['title'] = title
        if exclude:
            pydantic_kwargs['exclude'] = exclude
        if frozen:
            pydantic_kwargs['frozen'] = frozen
        if deprecated is not None:
            pydantic_kwargs['deprecated'] = deprecated
        if json_schema_extra is not None:
            pydantic_kwargs['json_schema_extra'] = json_schema_extra
        if validate_default:
            pydantic_kwargs['validate_default'] = validate_default
        if not repr:
            pydantic_kwargs['repr'] = repr

        # Pass constraint kwargs (min_length, max_length, gt, ge, lt, le, pattern, etc.)
        # These are stored in metadata by Pydantic
        for k, v in kwargs.items():
            if k not in self.schema_configs and k not in pydantic_kwargs:
                pydantic_kwargs[k] = v

        super().__init__(**pydantic_kwargs)

    def to_field_info(self, name: str, annotation: type) -> FieldInfo:
        return FieldInfo(
            name=name, annotation=annotation,
            default=self.default, default_factory=self.default_factory,
            configs=self.schema_configs,
            alias=getattr(self, 'alias', None),
            description=getattr(self, 'description', None),
            field_info_kwargs=self._field_info_kwargs(),
            metadata=self._constraint_kwargs(),
        )

    def _field_info_kwargs(self) -> dict:
        kwargs = {}
        # Only include public FieldInfo attributes, skip internal ones
        _skip = {'_original_assignment', '_attributes_set', '_original_annotation',
                 '_qualifiers', '_complete', '_final', 'metadata'}
        for attr in _PYDANTIC_FIELD_ATTRS:
            if attr in _skip:
                continue
            val = getattr(self, attr, None)
            if val is not None and val is not False and val != []:
                kwargs[attr] = val
        return kwargs

    def _constraint_kwargs(self) -> dict:
        """Return constraint kwargs (max_length, min_length, gt, ge, lt, le, etc.) for Field()."""
        constraints = {}
        for item in (self.metadata or []):
            for attr in ('max_length', 'min_length', 'gt', 'ge', 'lt', 'le',
                         'multiple_of', 'pattern'):
                if hasattr(item, attr):
                    constraints[attr] = getattr(item, attr)
        return constraints
