"""SelfDerivedModel - Derive a field's schema from the route's own fields."""

from __future__ import annotations


class SelfDerivedModel:
    """Metadata for a field whose schema is derived from the route's own fields.

        class UserRoute(RouteBase):
            name: str = RouteField(add=Add(), edit=Edit())
            items: list = RouteField(
                bulk_add=BulkAddConfig(
                    default=SelfDerivedModel(schema='add', exclude_fields=['email'])
                )
            )
    """

    def __init__(self, schema: str, is_optional: bool = True, format: str = 'model',
                 include_fields: list[str] | None = None, exclude_fields: list[str] | None = None):
        self.schema = schema
        self.is_optional = is_optional
        self.format = format
        self.include_fields = include_fields
        self.exclude_fields = exclude_fields

    def __repr__(self):
        return f"SelfDerivedModel(schema={self.schema!r}, include={self.include_fields}, exclude={self.exclude_fields})"
