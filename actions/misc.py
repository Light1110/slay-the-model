"""
Miscellaneous actions
"""
from actions.base import Action, ActionLevel
from utils.registry import register

@register("action")
class MoveToPositionAction(Action):
    """Move to a new position"""
    def execute(self):
        from engine.game_state import game_state
        position = self.kwargs.get('position')
        if position:
            game_state.move_to_position(position)
        game_state.current_floor += 1

@register("action")
class GenerateMapAction(Action):
    """Generate a new map and update global state"""
    def execute(self):
        from engine.game_state import game_state
        game_state.generate_initial_map()
        from localization import t
        print(t("ui.map_generated", default="Map generated for new act!"))

@register("action")
class GainRelicAction(Action):
    """Gain a random relic"""
    def execute(self):
        from engine.game_state import game_state
        from relics.base import create_relic
        import random

        if not game_state.player:
            return None

        # todo: store relics in a database
        available_relics = [
            "Burning Blood", "Ring of the Snake", "Cracked Core", "Akabeko", "Anchor",
            "Ancient Tea Set", "Art of War", "Bag of Marbles", "Bag of Preparation",
            "Blood Vial", "Bronze Scales", "Champion Belt", "Charon's Ashes",
            "Centennial Puzzle", "Ceramic Fish", "Dream Catcher", "Happy Flower"
        ]

        relic_name = random.choice(available_relics)
        relic = create_relic(relic_name)
        if relic:
            game_state.player.relics.append(relic)
            from localization import t
            print(t("ui.received_relic", default=f"Received relic: {relic.name}!", name=relic.name))
            return relic
        return None

@register("action")
class StartEventAction(Action):
    """Action to start an event - inserted to queue head"""
    def execute(self):
        from engine.game_state import game_state
        current_event = game_state.current_event
        if current_event:
            current_event.start_event()