## PLAYER

**OVERVIEW**
Player entity extending Creature with manager pattern for cards, status, and orbs.

## WHERE TO LOOK

| Task | Location | Notes |
|-------|-----------|--------|
| Player entity | player.py | Base stats, gold, energy, potions, relics |
| Card piles | card_manager.py | 5 piles in dict: deck, draw_pile, discard_pile, hand, exhaust_pile |
| Status changes | status_manager.py | Calm (+2 energy on leave), Divinity (+3 energy on enter) |
| Orb mechanics | orb_manager.py | FIFO evoke queue, passive triggers by timing |
| Player creation | player_factory.py | Minimal factory (6 lines) |

## CONVENTIONS

**Manager Initialization:** Player.__init__ creates 3 managers via dependency injection (deck, orb_slots, StatusType)

**Card Flow:** Reset on combat start → draw from draw_pile → discard on play → reshuffle when empty

**Energy Caps:** Gold and energy bounded (gold ≥ 0, 0 ≤ energy ≤ max_energy)

## ANTI-PATTERNS

- NEVER: status_manager.py:6-8 - Circular import workaround with get_game_state()
- NEVER: status_manager.py:35 - TODO comment for unimplemented stat updates
- NEVER: Direct game_state.player access in StatusManager (breaks encapsulation)
