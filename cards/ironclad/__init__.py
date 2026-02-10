"""
Ironclad card package - warrior class cards
All Ironclad cards are imported here for registration
"""

# All Ironclad cards (import individual card files)
from cards.ironclad import (
    Strike, Defend, Bash, Anger,
    IronWave, PommelStrike, HeavyBlade, Armaments, Flex,
    Clothesline, Inflame, BodySlam, Carnage,
    Bludgeon, LimitBreak, Pummel, Uppercut, Offering
)

__all__ = [
    # Starter
    'Strike', 'Defend', 'Bash', 'Anger',
    # Common
    'IronWave', 'PommelStrike', 'HeavyBlade', 'Armaments', 'Flex',
    # Uncommon
    'Clothesline', 'Inflame', 'BodySlam', 'Carnage',
    # Rare
    'Bludgeon', 'LimitBreak', 'Pummel', 'Uppercut', 'Offering',
]
