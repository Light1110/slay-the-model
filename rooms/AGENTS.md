# PROJECT KNOWLEDGE BASE - ROOMS MODULE

**Generated:** 2026-02-05 03:05:00
**Commit:** 8593596
**Branch:** main

## OVERVIEW
Room implementations with independent action queues and lifecycle management.

## STRUCTURE
```
rooms/
├── base.py            # Room base class (action queue, lifecycle)
├── rest.py             # RestRoom (heal, upgrade, recall)
├── shop.py             # ShopRoom (buy items, card removal)
├── treasure.py          # TreasureRoom (chest types, boss chest)
├── combat.py           # CombatRoom (wraps Combat)
├── neo.py              # Neo-specific room
└── __init__.py         # Module initialization
```

## WHERE TO LOOK

| Task | Location | Notes |
|-------|-----------|--------|
| Room lifecycle | rooms/base.py:57-100 | init() → enter() → leave() |
| Action queue | rooms/base.py:22-65 | Each room has independent ActionQueue |
| Rest room | rooms/rest.py:156 lines | heal, upgrade, recall options |
| Shop room | rooms/shop.py:234 lines | buy cards/relics/potions, card removal |
| Treasure room | rooms/treasure.py:112 lines | small/medium/large/boss chests |
| Combat room | rooms/combat.py:50 lines | Wraps Combat.start() |
| Unknown room | rooms/base.py:102-211 | Resolves at enter() to actual room/event |

## CODE MAP

### Base Room Class
```python
# rooms/base.py (213 lines)
class Room(Localizable):
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.action_queue = ActionQueue()  # Each room owns its queue
        
    def init(self):
        """Setup before player enters"""
        pass
        
    def enter(self) -> str:
        """Main room logic loop, returns "DEATH"|"WIN"|None"""
        while not self.should_leave:
            # Build menu/options
            # Execute actions
            result = self.execute_actions()
            # Check for game end
            if result in ("DEATH", "WIN"):
                return result
            # Rebuild menu if not leaving
            if not self.should_leave:
                self.action_queue.clear()
        return None
        
    def leave(self):
        """Cleanup when player exits"""
        self.action_queue.clear()
        game_state.event_stack.clear()
        self.should_leave = False
        
    def execute_actions(self) -> str:
        """Execute all actions in queue"""
        while not self.should_leave and not self.action_queue.is_empty():
            result = self.action_queue.execute_next()
            # Actions can return Actions/lists to add to queue
            if result is not None:
                if isinstance(result, list):
                    self.action_queue.add_actions(result, to_front=True)
                elif isinstance(result, Action):
                    self.action_queue.add_action(result, to_front=True)
                elif result in ("DEATH", "WIN"):
                    return result
        return None
        
    def add_map_selection_action(self):
        """Add map selection action to queue"""
        self.action_queue.add_action(SelectMapNodeAction())
```

### Room Implementations

**RestRoom** (rooms/rest.py:156 lines):
- init(): Handle EternalFeather (heal on enter)
- enter(): Rest/smith/recall/skip options loop
- _build_rest_menu(): Create Option list with RestOption
- leave(): Handle AncientTeaSet (add energy next turn)
- Options: Rest (heal 30% HP), Smith (upgrade card), Skip
- Special relic options: Girya (lift), PeacePipe (remove card), Shovel (dig relic)
- Relic checks: CoffeeDripper, FusionHammer prevent options

**ShopRoom** (rooms/shop.py:234 lines):
- init(): Generate shop items (5 colored cards, 2 colorless, 3 potions, 3 relics)
- enter(): Purchase loop, card removal option
- _generate_items(): Create ShopItem objects with pricing
- _build_shop_menu(): Create purchase options + card removal
- Card pricing: Base 50/75/150 with variance, discount support
- Card removal: Base 75 (50 with SmilingMask, 50% with MembershipCard)
- One random card gets 50% discount
- Rightmost relic (index 2) is always SHOP rarity

**TreasureRoom** (rooms/treasure.py:112 lines):
- init(): Determine chest type (small 50%, medium 33%, large 17%)
- enter(): Open chest or leave loop
- _build_treasure_menu(): Create menu options
- Chest types: small, medium, large (gold OR relic), boss (3 relics to choose)
- Boss chest: Triggers relic selection screen

**UnknownRoom** (rooms/base.py:102-211 lines):
- init(): Resolve to actual room type or event
- _resolve_room_type(): MapManager._resolve_unknown_type(floor)
- _create_event(): Create random event from pool
- _create_room(): MapManager._create_room_instance(room_type)
- enter(): Execute event or enter actual room

**CombatRoom** (rooms/combat.py:50 lines):
- enter(): Wrap Combat.start() and return result
- No init() or leave() override

## CONVENTIONS

**Room Lifecycle:**
1. init() - Setup before player enters (generate items, enemies, set flags)
2. enter() - Main room logic loop with action queue execution
3. leave() - Cleanup (clear action queue, reset flags)

**Action Queue:**
- Each room maintains its own ActionQueue (not shared)
- execute_actions() helper runs queue until should_leave=True or empty
- Actions can return Actions/lists to add to front of queue (deferred execution)

**Room Types:**
```python
RoomType enum (utils/types.py):
    MONSTER = "Monster"
    ELITE = "Elite"  
    REST_SITE = "Rest Site"
    MERCHANT = "Merchant"
    UNKNOWN = "Unknown"
    TREASURE = "Treasure"
    BOSS = "Boss"
    EVENT = "Event"
```

**Anti-Patterns (THIS PROJECT):**
- NEVER: rooms/shop.py:176 - Rightmost relic is shop relic (this is the rule)
- NEVER: Duplicate action queue logic - Each room has independent ActionQueue
- NEVER: Direct room.enter() calls in GameFlow - Map handles transitions
- NEVER: rooms/rest.py:28 - EternalFeather special case in init()
- ALWAYS: rooms/base.py:80-95 - execute_actions() helper with action queue handling

## COMMANDS
```bash
# Run game (room-based game loop)
python __main__.py

# Run tests
pytest tests/test_rooms.py -v              # Room tests (Rest, Shop, Treasure)
pytest tests/test_rest_room.py -v          # RestRoom tests
pytest tests/test_treasure_room.py -v       # TreasureRoom tests  
pytest tests/test_shop_room.py -v          # ShopRoom tests
pytest tests/test_unknown_room.py -v        # UnknownRoom tests
```

## NOTES
- Room types are registered in utils/registry with @register("room")
- MapManager._create_room_instance() is responsible for creating room instances
- Each room manages its own action queue for isolation
- Action queue supports deferred execution: actions can return other actions to be added later
