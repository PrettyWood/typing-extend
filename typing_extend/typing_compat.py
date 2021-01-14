"""
Module that handles differences between supported versions of Python
for some methods / classes of the `typing` module
"""
import sys
from typing import Any, Optional, Tuple, Type, Union, cast

__all__ = ("get_args", "get_origin", "is_typeddict", "TypedDict")

TypeLike = Union[Type[Any], Union[Any]]


def get_args(tp: TypeLike) -> Tuple[Any, ...]:
    try:
        from typing import get_args

        return get_args(tp)
    except ImportError:
        # Python 3.6 and 3.7
        return cast(Tuple[Any, ...], getattr(tp, "__args__", ()))


def get_origin(tp: TypeLike) -> Optional[TypeLike]:
    try:
        from typing import get_origin

        return get_origin(tp)
    except ImportError:
        # Python 3.7
        if sys.version_info[:2] == (3, 7):
            return getattr(tp, "__origin__", None)
        # Python 3.6
        else:
            assert sys.version_info[:2] == (3, 6)

            from typing import Dict, List, Set, Tuple, Type

            # In python 3.6, the origin of `List[str]` for example
            # is `List` and not `list`. We hence need an explicit mapping...
            typing_to_builtin_map = {
                Dict: dict,
                List: list,
                Set: set,
                Tuple: tuple,
                Type: type,
            }

            origin = getattr(tp, "__origin__", None)
            return typing_to_builtin_map.get(origin, origin)


def is_typeddict(tp: TypeLike) -> bool:
    try:
        from typing import is_typeddict  # type: ignore[attr-defined]

        return is_typeddict(tp)  # type: ignore[no-any-return]
    except ImportError:
        # Python 3.6 to Python 3.9
        from .utils import lenient_issubclass

        return lenient_issubclass(tp, dict) and hasattr(tp, "__annotations__")


if sys.version_info < (3, 9):
    # Even though `TypedDict` is already in python 3.8,
    # the class doesn't have `__required_keys__` and `__optional_keys__`,
    # which prevents a perfect support
    from typing_extensions import TypedDict
else:
    from typing import TypedDict
