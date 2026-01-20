from engine.game_state import game_state
from actions import (
    action_queue,
    DisplayTextAction,
)
from utils.registry import get_registered
import random
import time

# Import rooms to register them
import rooms


class GameFlow:
    """Action-based game flow using action queue loop"""

    def __init__(self):
        pass

    def start_game(self):
        """Initialize the game using actions"""
        # Add initial setup actions to queue
        setup_actions = [
            DisplayTextAction(text_key="ui.game_welcome"),
            DisplayTextAction(text_key="ui.game_awaken"),
            DisplayTextAction(text_key="ui.seed_display", seed=game_state.config.seed),
            DisplayTextAction(text_key="ui.character_display", character=game_state.config.character),
        ]
        action_queue.add_actions(setup_actions)
        # Start with neo room
        neo_room_class = get_registered("room", "NeoRewardRoom")
        neo_room = neo_room_class()
        game_state.current_room = neo_room
        neo_room.enter_room()

        while True:
            assert not action_queue.is_empty()

            # Execute next action in queue
            result = action_queue.execute_next()

            # Check game end conditions
            if result == "game_over":
                from localization import t
                print(f"\n💀 {t('ui.game_over', default='Game Over! You have fallen in the Spire. 💀')}")
                break
            elif result == "game_won":
                from localization import t
                print(f"\n🎉 {t('ui.game_won', default='Congratulations! You have conquered the Spire! 🎉')}")
                break

            # If result is a list of actions, add them to queue
            elif isinstance(result, list):
                action_queue.add_actions(result)