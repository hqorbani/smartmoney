import importlib
import inspect
import pkgutil
from types import ModuleType
from typing import Type, TypeVar


T = TypeVar("T")


def discover(package_name: str, base_class: Type[T]) -> list[T]:
    """
    Discover and instantiate all subclasses of `base_class`
    inside the given package.

    Returned instances are sorted by `priority`.
    """

    package = importlib.import_module(package_name)

    discovered = []

    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):

        if is_pkg:
            continue

        module = importlib.import_module(
            f"{package_name}.{module_name}"
        )

        discovered.extend(
            _discover_module(
                module,
                base_class,
            )
        )

    discovered.sort(
        key=lambda obj: getattr(obj, "priority", 0)
    )

    return discovered


def _discover_module(
    module: ModuleType,
    base_class: Type[T],
) -> list[T]:

    instances = []

    for _, obj in inspect.getmembers(module, inspect.isclass):

        if obj is base_class:
            continue

        if not issubclass(obj, base_class):
            continue

        if inspect.isabstract(obj):
            continue

        instances.append(obj())

    return instances