# PROJECT KNOWLEDGE BASE - TESTS MODULE

**Generated:** 2026-02-05 03:05:00
**Commit:** 8593596
**Branch:** main

## OVERVIEW
Mixed test framework with unittest and pytest patterns.

## STRUCTURE
```
tests/
├── test_event_pool.py       # Event pool registration and selection
├── test_map_system.py         # Map generation and structure
├── test_map_selection.py       # Room selection AI
├── test_map_core.py            # MapNode/MapData structure
├── test_no_crossing.py          # Path collision detection
├── test_rooms.py              # Room implementations (Rest, Shop, Treasure)
├── test_enemies.py             # Enemy implementations (5 enemies)
├── test_rest_room.py          # RestRoom basic tests
├── test_treasure_room.py       # TreasureRoom basic tests
├── test_shop_room.py          # ShopRoom basic tests
└── test_unknown_room.py         # UnknownRoom basic tests
```

## WHERE TO LOOK

| Task | Location | Notes |
|-------|-----------|--------|
| Event tests | test_event_pool.py | @register decorator, unique events |
| Map tests | test_map_system.py | Map generation, node connections |
| Room tests | test_rooms.py | Rest, Shop, Treasure room functionality |
| Enemy tests | test_enemies.py | Weak/elite/boss, damage calculation |
| Test framework | Mixed | unittest (setUp/tearDown) and pytest (class-based) |

## TEST FRAMEWORKS

### unittest Pattern

```python
# test_event_pool.py (lines 20-45)
class TestEventPool(unittest.TestCase):
    def setUp(self):
        from events.event_pool import event_pool
        self.event_pool = event_pool
        self.original_events = len(event_pool._event_registry.copy())
    
    def tearDown(self):
        from events.event_pool import event_pool
        event_pool._event_registry = self.original_events.copy()
```

### pytest Pattern

```python
# test_enemies.py (lines 16-47)
class TestEnemies(unittest.TestCase):
    def test_cultist_weak(self):
        enemy = Cultist()
        assert enemy.weak
        assert enemy.max_hp == 24
    
    # Pytest class-based tests
class TestRestRoomBasic:
    def test_rest_room_creation(self):
        rest_room = RestRoom()
        assert rest_room.room_type.value == "Rest Site"
```

### Custom Test Patterns

```python
# test_map_system.py (main() function)
def test_generate_small_map():
    map_manager = MapManager(seed=12345)
    map_manager.generate_map()
    # Check map structure
```

**MockAIDecisionEngine** (ai/ai_interface.py: 45 lines)
- Used in map selection tests
- Provides: first(), last(), random(), least_risk(), highest_reward() strategies

## CONVENTIONS

**Test Organization:**
- test_rooms.py: Multiple room tests in one file (Rest, Shop, Treasure)
- Separate test files for each complex component (test_enemies.py, test_rest_room.py, etc.)
- test_unknown_rooms.py contains tests for Tiny Chest and Juzu Bracelet relics (not working due to missing methods)

**Test Coverage:**
- Event pool: Registration, unique events, floor filtering
- Map system: Generation, path existence, room selection
- Rooms: Basic functionality without special relics
- Enemies: 5 implementations with modifiers

## ANTI-PATTERNS (THIS PROJECT)
- NEVER: Direct player state access in tests - create test instances
- NEVER: Mock game_state.player - use dependency injection
- NEVER: Test implementations in production modules (tests/ only)
- NEVER: Skip setUp/tearDown in unittest - proper setup/teardown

## COMMANDS
```bash
# Run all tests
pytest tests/ -v                             # All tests
pytest tests/test_event_pool.py -v          # Specific module tests
pytest tests/test_enemies.py -v              # Enemy tests
pytest tests/test_rooms.py -v                # Room tests
pytest tests/test_rest_room.py -v          # RestRoom tests
pytest tests/test_treasure_room.py -v       # TreasureRoom tests
pytest tests/test_shop_room.py -v          # ShopRoom tests
pytest tests/test_unknown_room.py -v        # UnknownRoom tests
```

## NOTES
- MockAIDecisionEngine provides test AI strategies for map selection
- pytest cache directory (.pytest_cache/) may affect test behavior
- Tests verify core functionality without complex scenarios
