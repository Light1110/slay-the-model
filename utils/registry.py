"""
Unified registry for all game components.
"""

from typing import Dict, Any, Callable, Type
import importlib


_REGISTRY = {}


def register(category: str):
    """
    Unified decorator to register any component type.

    Usage:
        @register("room")
        class MyRoom(Room):
            pass

        @register("event")
        def my_event(event):
            pass

        @register("action")
        class MyAction(Action):
            pass
    """
    def decorator(obj: Any):
        if category not in _REGISTRY:
            _REGISTRY[category] = {}

        if hasattr(obj, '__name__'):  # Class or function
            name = getattr(obj, '__name__', None)
        else:
            name = str(obj)

        if name:
            _REGISTRY[category][name] = obj

        return obj
    return decorator


def get_registered(category: str, name: str = None):
    """Get registered item(s) from a category."""
    if category not in _REGISTRY:
        return None if name else {}

    if name:
        return _REGISTRY[category].get(name)
    return _REGISTRY[category]


def list_registered(category: str):
    """List all registered items in a category."""
    if category not in _REGISTRY:
        return []
    return list(_REGISTRY[category].keys())