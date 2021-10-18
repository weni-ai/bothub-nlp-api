from fastapi import APIRouter
from typing import Any, Callable
from fastapi.types import DecoratedCallable


class CustomAPIRouter(APIRouter):
    """
    This is a fix for the trailing backslash problem of the api path routes
    Example: defining a 'v2/parse' route will enable 'v2/parse/' as well
    For reference: https://github.com/tiangolo/fastapi/issues/2060
    """
    def api_route(
        self, path: str, *, include_in_schema: bool = True, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        if path.endswith("/"):
            path = path[:-1]

        add_path = super().api_route(
            path, include_in_schema=include_in_schema, **kwargs
        )

        alternate_path = path + "/"
        add_alternate_path = super().api_route(
            alternate_path, include_in_schema=False, **kwargs
        )

        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            add_alternate_path(func)
            return add_path(func)

        return decorator
