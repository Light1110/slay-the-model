"""Bronze Orb - Minion summoned by Bronze Automaton."""
from engine.random_streams import get_rng
from engine.runtime_api import add_action, add_actions

from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act2.bronze_orb_intentions import Steal, SupportBeam, Beam


class BronzeOrb(Enemy):
    """Bronze Orb is a minion summoned only by the Bronze Automaton.
    
    This is a summoned minion and should not trigger on_fatal effects.
    """

    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True

    def __init__(self):
        super().__init__(hp_range=(52, 58), is_minion=True) # todo: 54-60 a7
        self.add_intention(Steal(self))
        self.add_intention(SupportBeam(self))
        self.add_intention(Beam(self))
        self._has_used_steal = False
        self.stolen_cards = []  # Track stolen cards to return on death

    def on_combat_start(self, floor: int):
        """Initialize combat state."""
        self._has_used_steal = False
        super().on_combat_start(floor)

    def determine_next_intention(self, floor: int):
        roll = get_rng("ai").randint(0, 99)
        history = self.history_intentions
        if not self._has_used_steal and roll >= 25:
            self._has_used_steal = True
            return self.intentions["Steal"]
        if roll >= 70 and history[-2:] != ["Support Beam", "Support Beam"]:
            return self.intentions["Support Beam"]
        return self.intentions["Support Beam" if history[-2:] == ["Beam", "Beam"] else "Beam"]

    def on_death(self):
        """Return stolen cards to player's draw pile."""
        from actions.card import AddCardAction
        actions = []
        for card in self.stolen_cards:
            actions.append(AddCardAction(card=card, dest_pile='hand'))
        from engine.game_state import game_state
        add_actions(actions)
        return