# TESTS

**Generated:** 2025-02-05 02:05:00
**Commit:** 9106d4e
**Branch:** main

## OVERVIEW
Mixed framework test suite covering event pool registration, map generation algorithms, room creation, and unknown room mechanics with relic modifiers.

## WHERE TO LOOK

| Task | Location | Notes |
|-------|-----------|--------|
| Event pool registration | test_event_pool.py | unittest, floor filtering, unique events, decorator |
| Map generation/selection | test_map_system.py, test_map_selection.py | Custom main(), distribution testing, AI context |
| Room instantiation | test_rooms.py | pytest, Rest/Shop/Treasure rooms, chest probabilities |
| Unknown room mechanics | test_unknown_rooms.py | Relic modifiers (Tiny Chest, Juzu Bracelet) |
| Core map data | test_map_core.py | MapNode, MapData without Room dependencies |
| No-crossing logic | test_no_crossing.py | Branch path collision detection |

## CONVENTIONS

**Framework Mix:**
- test_event_pool.py: unittest.TestCase setUp/tearDown pattern
- test_rooms.py: pytest with class-based TestX groups
- Map tests (test_map_*.py): Custom main() with sys.exit() and print debugging

**Mock Patterns:**
- MockEvent: Event with trigger() returning None
- MockAIDecisionEngine: Simulates AI strategies (first/last/random/least_risk/highest_reward)

**Running Tests:**
```bash
pytest tests/test_rooms.py -v        # pytest files
python tests/test_event_pool.py      # unittest files
python tests/test_map_system.py      # custom main() scripts
```

## ANTI-PATTERNS

- test_map_selection_simple.py, test_map_standalone.py: Empty/placeholder files without test cases
- Property-based testing: Not using hypothesis despite complex map probabilities
- MockAIDecisionEngine: Single file import path varies (ai.ai_interface vs from ai_tools)
