"""
Base action system
"""
from engine.game_state import game_state

from enum import Enum

class ActionLevel(Enum):
    NO_MESSAGE = 0
    HP_CHANGE = 1

class Action:
    """Base action class - executable game logic unit"""

    def __init__(self, **kwargs):
        # Remaining kwargs stored for action use
        self.level = ActionLevel.NO_MESSAGE
        self.kwargs = kwargs

    def execute(self):
        """Execute this action - to be overridden"""
        raise NotImplementedError

    def notify(self):
        """Notify listeners for this action."""
        try:
            if hasattr(game_state, 'notify_listeners'):
                game_state.notify_listeners(self)
        except Exception:
            pass

    def __str__(self):
        return f"{self.__class__.__name__}()"


class ActionQueue:
    """Queue of actions to execute in loop"""
    def __init__(self):
        self.queue = []

    def add_action(self, action, to_front=False):
        """Add action to queue - optionally to front"""
        if to_front:
            self.queue.insert(0, action)
        else:
            self.queue.append(action)

    def add_actions(self, actions, to_front=False):
        """Add multiple actions to queue - optionally to front"""
        if to_front:
            self.queue = actions + self.queue
        else:
            self.queue.extend(actions)

    def execute_next(self):
        """Execute next action in queue and notify listeners afterwards"""
        if self.queue:
            action = self.queue.pop(0)
            if game_state.config.debug:
                print(f"Executing action: {action}")
            result = action.execute()
            action.notify()
            return result
        return None

    def is_empty(self):
        """Check if queue is empty"""
        return len(self.queue) == 0

    def clear(self):
        """Clear the queue"""
        self.queue = []

    def peek_next(self):
        """Peek at next action without removing it"""
        if self.queue:
            return self.queue[0]
        return None


# Global action queue
action_queue = ActionQueue()