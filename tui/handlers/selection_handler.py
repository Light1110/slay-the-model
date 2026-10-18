# -*- coding: utf-8 -*-
"""
Selection handler - manages the selection panel for input-request integration.
"""
from typing import List, Optional, Any, TYPE_CHECKING

from localization import resolve_text
from utils.option import selection_error

if TYPE_CHECKING:
    from actions.display import InputRequestAction
    from utils.option import Option


class SelectionHandler:
    """Handles selection panel interactions."""
    
    def __init__(self, app):
        self._app = app
        self._current_action: Optional['InputRequestAction'] = None
        self._pending_result: int | List[int] | None = None
    
    def show_selection(self, select_action: 'InputRequestAction') -> int:
        """
        Display selection options from InputRequestAction.
        Returns selected index (called synchronously, actual selection happens async).
        """
        self._current_action = select_action
        
        title = resolve_text(select_action.request.title) or "Choose:"
        options = select_action.request.options
        
        self._app.show_selection(title, options, max_select=select_action.request.max_select, must_select=select_action.request.must_select)
        
        return 0
    
    def handle_input(self, key: str) -> bool:
        """Handle keyboard input. Returns True if input was consumed."""
        if key == "0" and self._current_action is not None and not self._current_action.request.must_select:
            self._pending_result = []
            return True
        if key.isdigit():
            idx = int(key) - 1
            return self.select_by_index(idx)
        return False
    
    def select_by_index(self, idx: int) -> bool:
        """Select option by index. Returns True if valid selection."""
        if self._current_action:
            request = self._current_action.request
            if selection_error(request.options, [idx], request.max_select, request.must_select) is not None:
                return False
            self._pending_result = idx
            return True
        return False
    
    def get_result(self) -> int | List[int] | None:
        """Get pending selection result."""
        return self._pending_result
    
    def clear(self):
        """Clear selection state."""
        self._current_action = None
        self._pending_result = None
        self._app.clear_selection()
