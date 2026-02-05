# PROJECT KNOWLEDGE BASE - ACTIONS MODULE

**Generated:** 2026-02-05 02:05:00
**Commit:** 8593596
**Branch:** main

## OVERVIEW
Command pattern system implementing game actions via ActionQueue for deferred execution.

## STRUCTURE
```
actions/
├── base.py          # Base Action and ActionQueue classes
├── card.py          # Choose actions (Choose*CardAction)
├── combat.py        # Combat-specific actions (DamagePlayerAction, BlockPlayerAction, etc.)
├── display.py        # UI actions (SelectAction, DisplayTextAction)
├── health.py         # Player HP actions (HealAction, LoseMaxHPAction)
├── map_selection.py # Map navigation (SelectMapNodeAction)
├── misc.py           # Miscellaneous actions
├── reward.py         # Reward actions (AddRelicAction, AddGoldAction, AddCardAction, etc.)
├── room.py          # Room lifecycle actions (LeaveRoomAction, TriggerRelicAction)
└── shop.py          # Shop-specific actions (BuyItemAction, CardRemovalAction, LeaveShopAction)
```

## WHERE TO LOOK

| Task | Location | Notes |
|-------|-----------|--------|
| Base classes | actions/base.py | Action, ActionQueue with add_actions(to_front), execute_next() |
| Card manipulation | actions/card.py | Choose actions return SelectAction for UI selection |
| Combat system | actions/combat.py | DamagePlayerAction, BlockPlayerAction, AddEtherealModifierAction |
| UI/Display | actions/display.py | SelectAction auto-selects single option in AI mode |
| Reward system | actions/reward.py | AddRelicAction, AddGoldAction, potion handling |
| Shop transactions | actions/shop.py | BuyItemAction with relic price modifiers |
| Treasure chests | actions/treasure.py | OpenChestAction, SkipTreasureAction |
| Room lifecycle | actions/room.py | LeaveRoomAction, TriggerRelicAction |
| Map navigation | actions/map_selection.py | SelectMapNodeAction (AI/human modes) |
| Health/Status | actions/health.py | HealAction, LoseMaxHPAction, max HP manipulation |

## CONVENTIONS
- All actions are @register("action") decorated classes
- Actions can return other Actions or lists of Actions, which will be added to caller's queue
- Choose*CardAction actions return SelectAction for UI flow
- Each room/event/combat maintains its own ActionQueue for isolation
- ActionQueue has debug printing from game_state.config.debug
- Actions use execute() method that returns None on success or a result value

## ANTI-PATTERNS
- NO separate DamageAction/BlockAction/DrawAction/EnergyAction - combat handled via cards directly
- NO room enter() calls inside MoveToMapNodeAction - GameFlow main loop handles this
- NO direct player modification in MoveToMapNodeAction - only updates game_state

## CODE MAP

### Key Classes
```python
# Base classes
Action
ActionQueue

# Command pattern actions
ChooseAddCardAction
ChooseRemoveCardAction
ChooseUpgradeCardAction

# Combat actions
DamagePlayerAction
BlockPlayerAction
AddEtherealModifierAction

# Reward/Shop actions
AddRelicAction
AddGoldAction
AddRandomPotionAction
BuyItemAction
CardRemovalAction

# UI/Display
SelectAction
DisplayTextAction

# Room/Map
LeaveRoomAction
TriggerRelicAction
SelectMapNodeAction
```

## COMMANDS
```bash
# Run game (uses actions system)
python __main__.py

# Run tests
pytest tests/                 # All tests
python tests/test_*.py      # Individual test
```

## NOTES
- 37 total action files implementing command pattern
- Choose*CardAction delegates to SelectAction for UI
- Each room/event/combat has independent ActionQueue
- Action execution is deferred: add to queue, then execute loop
