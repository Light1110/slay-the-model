"""Game over action."""

from actions.base import Action
from utils.result_types import GameStateResult


class GameOverAction(Action):
    """Action that ends the game with a death result."""
    
    def execute(self) -> GameStateResult:
        """End the game.
        
        Returns:
            GameStateResult with GAME_LOSE state
        """
        return GameStateResult("GAME_LOSE")
