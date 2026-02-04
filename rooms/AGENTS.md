# ROOMS

## OVERVIEW
Room implementations with independent action queues and lifecycle management.

## STRUCTURE
```
rooms/
├── base.py          # Room, UnknownRoom base classes
├── combat.py        # CombatRoom wraps Combat
├── rest.py          # RestRoom with heal/upgrade/recall
├── shop.py          # ShopRoom with ShopItem pricing
├── treasure.py      # TreasureRoom chest types
└── neo.py           # Neo-specific room
```

## WHERE TO LOOK

| Task | Location | Notes |
|-------|-----------|--------|
| Room lifecycle | base.py | init() → enter() → leave() |
| Action queue | base.py:22 | Each room owns ActionQueue |
| Room resolution | base.py:102-211 | UnknownRoom resolves at enter() |
| Combat execution | combat.py:50 | Wraps Combat.start() |
| Rest options | rest.py:87-152 | Rest/smith/relic options |
| Shop pricing | shop.py:116-190 | ShopItem, variance, discounts |
| Treasure chests | treasure.py:27-34 | small/medium/large/boss |

## CONVENTIONS

**Room Lifecycle:**
- init() - Setup before player enters (generate items, enemies)
- enter() - Main room logic loop, return "DEATH"/"WIN"/None
- leave() - Cleanup, clear action queue

**Action Queue:**
- Each room maintains its own ActionQueue (not shared)
- execute_actions() helper runs queue until empty or should_leave=True
- Actions can return Actions/ActionLists added to front of queue

**ShopRoom:**
- Rightmost relic (index 2) is always SHOP rarity
- Card removal service priced at 75 (75 with SmilingMask, 50 with MembershipCard)
- One random card gets 50% discount

**TreasureRoom:**
- Chest types: small (50%), medium (33%), large (17%)
- Boss chests trigger relic selection

## ANTI-PATTERNS

- NEVER: Duplicate _has_relic() in rest.py and shop.py → use utils module
- NEVER: Define LeaveTreasureAction in treasure.py → belongs in actions/
- NEVER: UnknownRoom enters without init() → resolution depends on init()
