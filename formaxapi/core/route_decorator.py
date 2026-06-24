"""route decorator and route_factory."""

from __future__ import annotations
from typing import Callable, Literal
from fastapi import APIRouter, status


class _RouteInfo:
    __slots__ = ('path', 'method', 'name', 'description', 'status_code', 'tags')

    def __init__(self, path, method, name, description, status_code, tags):
        self.path = path
        self.method = method
        self.name = name
        self.description = description
        self.status_code = status_code
        self.tags = tags


def route(
    path: str,
    method: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH'] = 'GET',
    name: str | None = None,
    description: str | None = None,
    status_code: int = status.HTTP_200_OK,
    tags: list[str] | None = None,
) -> Callable:
    """Decorator to mark a method as a route endpoint."""
    def decorator(func: Callable) -> Callable:
        func._route_info = _RouteInfo(
            path=path, method=method,
            name=name or func.__name__,
            description=description,
            status_code=status_code,
            tags=tags or [],
        )
        return func
    return decorator


def route_factory(*route_classes: type) -> APIRouter:
    """Collect all @route methods from Route classes into a FastAPI APIRouter."""
    router = APIRouter()

    for cls in route_classes:
        default_tags = [getattr(cls, '_route_group', None) or cls.__name__]

        for attr_name in dir(cls):
            attr = getattr(cls, attr_name, None)
            if attr is None:
                continue

            func = getattr(attr, '__func__', attr)
            info = getattr(func, '_route_info', None)
            if info is None:
                continue

            tags = info.tags if info.tags else default_tags

            router.add_api_route(
                path=info.path,
                endpoint=attr,
                methods=[info.method],
                name=info.name,
                description=info.description,
                status_code=info.status_code,
                tags=tags,
            )

    return router
