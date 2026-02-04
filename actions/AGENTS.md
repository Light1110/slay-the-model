# ACTIONS MODULE

**Generated:** 2025-02-05 02:05:00
**Commit:** 9106d4e
**Branch:** main

## OVERVIEW
Command pattern system implementing game actions via ActionQueue for deferred execution.

## WHERE TO LOOK

| Task | Location | Notes |
|-------|-----------|--------|
| Base classes | actions/base.py | Action, ActionQueue with add_actions(to_front), execute_next() |
| Card manipulation | actions/card.py | Choose actions return SelectAction for UI selection |
| Reward system | actions/reward.py | AddRelicAction, AddGoldAction, potion handling |
| Shop transactions | actions/shop.py | BuyItemAction with relic price modifiers |
| Treasure chests | actions/treasure.py | OpenChestAction, SkipTreasureAction |
| User interaction | actions/display.py | SelectAction auto-selects single option in AI mode |
| Map navigation | actions/map_selection.py | SelectMapNodeAction (AI/human modes) |

## CONVENTIONS
- Actions are @register("action") decorated classes
- Actions can return other actions/lists to be added to caller's queue (not execute directly)
- Choose*CardAction actions return SelectAction for UI flow
- Each room/event/combat maintains its own ActionQueue for isolation
- ActionQueue debug printing from game_state.config.debug

## ANTI-PATTERNS
- NO separate DamageAction/BlockAction/DrawAction/EnergyAction - combat handled via cards directly
- NO room enter() calls inside MoveToMapNodeAction - GameFlow main loop handles this
- NO direct player modification in MoveToMapNodeAction - only updates game_state
