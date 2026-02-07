"""
Menu-related utility functions for action selection.

This module provides helper functions for menu handling in the action system.
"""
from typing import List, TYPE_CHECKING
from utils.option import Option

if TYPE_CHECKING:
    from actions.base import Action


def add_menu_option_if_human(options: List['Option'], select_action: 'Action') -> List[Option]:
    """Add 'return to menu' option for human players.

    When playing in human mode, the user should have the option
    to return to the menu after making their selection. This function
    adds that option to the list.

    Args:
        options: List of display options
        select_action: The SelectAction instance (for reference)

    Returns:
        List of Option instances with 'return to menu' option added

    Note:
        This is a simplified version that doesn't fully implement
        the original menu system. For now, it just returns
        the options as-is.
    """
    # For now, just return options without modification
    # A full implementation would add a "return to menu" option here
    return options
