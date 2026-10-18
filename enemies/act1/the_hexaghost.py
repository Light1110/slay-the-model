"""
The Hexaghost - Act 1 Final Boss
Complex attack pattern with Burn cards.
"""
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act1.the_hexaghost_intentions import (
    ActivateIntention,
    DividerIntention,
    SearIntention,
    TackleIntention,
    InflameIntention,
    InfernoIntention
)


class TheHexaghost(Enemy):
    """The Hexaghost - Act 1 Final Boss with complex attack pattern."""
    
    enemy_type = EnemyType.BOSS
    
    def __init__(self):
        from engine.game_state import game_state

        ascension = getattr(game_state, "ascension", 0)
        super().__init__(
            hp_range=(264, 264) if ascension >= 9 else (250, 250)
        )
        
        # Register intentions
        self.add_intention(ActivateIntention(self))
        self.add_intention(DividerIntention(self))
        self.add_intention(SearIntention(self))
        self.add_intention(TackleIntention(self))
        self.add_intention(InflameIntention(self))
        self.add_intention(InfernoIntention(self))
        
        self._used_inferno = False

    def determine_next_intention(self, floor: int = 1):
        """Select from executed actions; querying an intent never advances it."""
        completed_turns = len(self.history_intentions)
        if completed_turns == 0:
            return self.intentions["activate"]
        if completed_turns == 1:
            return self.intentions["divider"]
        pattern = ("sear", "tackle", "sear", "inflame", "tackle", "sear", "inferno")
        return self.intentions[pattern[(completed_turns - 2) % len(pattern)]]
