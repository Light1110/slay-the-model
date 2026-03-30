"""Orb-related actions."""
from engine.runtime_api import add_action, add_actions

from actions.base import Action
from utils.registry import register


@register("action")
class OrbPassiveAction(Action):
    """Trigger an orb's passive effect

    Required:
        orb: Orb instance to trigger passive for

    Optional:
        None
    """
    def __init__(self, orb):
        self.orb = orb

    def execute(self) -> None:
        """Execute the orb's passive effect"""
        if not self.orb:
            return

        self.orb.on_passive()



@register("action")
class OrbEvokeAction(Action):
    """Trigger an orb's evoke effect

    Required:
        orb: Orb instance to evoke

    Optional:
        None
    """
    def __init__(self, orb):
        self.orb = orb

    def execute(self) -> None:
        """Execute the orb's evoke effect"""
        if not self.orb:
            return

        self.orb.on_evoke()



@register("action")
class EvokeOrbAction(Action):
    """Evoke an orb from player's orb slots

    Required:
        index (int): Orb index to evoke (default 0 for leftmost)

    Optional:
        times (int): Number of times to evoke (default 1)
    """
    def __init__(self, index: int = 0, times: int = 1):
        self.index = index
        self.times = times

    def execute(self) -> None:
        """Evoke the orb at the specified index"""
        from engine.game_state import game_state

        if not game_state.player or not hasattr(game_state.player, 'orb_manager'):
            return

        orb_manager = game_state.player.orb_manager
        orbs = list(orb_manager.orbs)

        # Validate index
        orb_index = self.index
        if orb_index < 0:
            orb_index = len(orbs) + orb_index
        if orb_index < 0 or orb_index >= len(orbs):
            return

        orb = orbs[orb_index]

        # Evoke the orb (remove it)
        actions = []
        for _ in range(self.times):
            evoke_action = OrbEvokeAction(orb=orb)
            actions.append(evoke_action)

        # Remove the orb from manager
        orb_manager.remove_orb(orb_index)

        if actions:
            add_actions(actions, to_front=True)
            return



@register("action")
class EvokeAllOrbsAction(Action):
    """Evoke all orbs from player's orb slots

    Required:
        None

    Optional:
        None
    """
    def __init__(self):
        pass

    def execute(self) -> None:
        """Evoke all orbs"""
        from engine.game_state import game_state

        if not game_state.player or not hasattr(game_state.player, 'orb_manager'):
            return

        orb_manager = game_state.player.orb_manager
        orbs = list(orb_manager.orbs)

        if not orbs:
            return

        # Create evoke actions for all orbs
        actions = []
        for orb in orbs:
            evoke_action = OrbEvokeAction(orb=orb)
            actions.append(evoke_action)

        # Clear all orbs from manager
        orb_manager.clear_all()

        if actions:
            add_actions(actions, to_front=True)
            return



@register("action")
class AddOrbAction(Action):
    """Add an orb to player's orb slots

    Required:
        orb: Orb instance to add

    Optional:
        None
    """
    def __init__(self, orb):
        self.orb = orb

    def execute(self) -> None:
        """Add the orb to player's orb manager"""
        from engine.game_state import game_state

        if not game_state.player or not hasattr(game_state.player, 'orb_manager'):
            return

        orb_manager = game_state.player.orb_manager

        # If max slots exceeded, evoke rightmost orb first
        if len(orb_manager.orbs) >= orb_manager.max_orb_slots:
            # Evoke the rightmost orb
            evoke_action = EvokeOrbAction(index=-1)
            evoke_action.execute()

        # Add the new orb
        orb_manager.add_orb(self.orb)
