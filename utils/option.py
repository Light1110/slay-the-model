from typing import TYPE_CHECKING

from localization import BaseLocalStr

if TYPE_CHECKING:
    from actions.base import Action


class Option:
    """One selectable option in an input request."""

    def __init__(self, name: BaseLocalStr | str, actions: list["Action"], enabled: bool = True):
        self.name = name
        self.actions = actions
        self.enabled = enabled
