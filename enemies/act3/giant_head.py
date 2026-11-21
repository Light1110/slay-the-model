"""
Giant Head - Act 3 Elite enemy
Counts down until "It Is Time" attack.
"""
from engine.random_streams import get_rng


from enemies.base import Enemy
from enemies.act3.giant_head_intentions import (
    CountIntention,
    GlareIntention,
    ItIsTimeIntention,
)
from utils.types import EnemyType


class GiantHead(Enemy):
    """Giant Head - Elite enemy that counts down to devastating attacks."""

    enemy_type = EnemyType.ELITE
    select_intention_after_enemy_turn = True

    def __init__(self):
        super().__init__(hp_range=(500, 500)) # todo: 520 a8
        
        # Register intentions
        self.add_intention(CountIntention(self))
        self.add_intention(GlareIntention(self))
        self.add_intention(ItIsTimeIntention(self))
        
        # Internal state
        self._turn_count = 0
        self._selected_after_turn = -1
        self._it_is_time_count = 0

    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on turn count.
        
        Giant Head pattern:
        - First 4 turns: 50/50 chance of Count or Glare
        - Turn 5+: Always It Is Time
        """
        completed = len(self.history_intentions)
        if self._selected_after_turn == completed:
            return self.current_intention
        self._selected_after_turn = completed
        self._turn_count = completed + 1
        
        from engine.game_state import game_state

        roll = get_rng("ai").randint(0, 99)
        if self._turn_count >= (4 if game_state.ascension >= 18 else 5):
            move = "It Is Time"
        elif roll < 50:
            move = "Count" if self.history_intentions[-2:] == ["Glare", "Glare"] else "Glare"
        else:
            move = "Glare" if self.history_intentions[-2:] == ["Count", "Count"] else "Count"
        self.current_intention = self.intentions[move]
        return self.current_intention

    def on_combat_start(self, floor: int = 1):
        """Initialize combat state."""
        self._selected_after_turn = -1
        self._turn_count = 0
        self._it_is_time_count = 0
        super().on_combat_start(floor)
        # Giant Head starts with SlowPower
        from powers.definitions.slow import SlowPower
        self.add_power(SlowPower(owner=self))