# PROJECT KNOWLEDGE BASE

**Generated:** 2025-02-05 02:05:00
**Commit:** 9106d4e
**Branch:** main

## OVERVIEW
Python-based Slay the Spire clone with room-based game loop, event system, and AI decision making support.

## STRUCTURE
```
./
├── actions/       # Command pattern system
├── rooms/        # Room implementations (combat, rest, shop, treasure)
├── player/       # Player state, cards, statuses, orbs
├── cards/         # Card base class with namespace system
├── map/           # Procedural map generation with weighted probabilities
├── events/         # Event pool and neo event
├── entities/       # Creature, collection
├── engine/         # GameFlow, GameState, CombatState
├── config/         # YAML-based game configuration
├── localization/   # i18n (en.yaml, zh.yaml)
├── tests/          # Mixed unittest/pytest
└── __main__.py    # Entry point
```

## WHERE TO LOOK

| Task | Location | Notes |
|-------|-----------|--------|
| Game loop | engine/game_flow.py | Iterates over rooms, manages win/death |
| Global state | engine/game_state.py | Singleton with config, map, combat, player |
| Map system | map/map_manager.py | 700 lines, complex display/JSON rendering |
| Card system | cards/base.py | Namespace support, base/temp/combat values |
| Room base | rooms/base.py | Action queue per room |
| Event pool | events/event_pool.py | Weighted selection, neo blessing |
| AI interface | ai/ai_interface.py | MockAIDecisionEngine for testing |
| Configuration | config/game_config.py | YAML loader, duplicate debug keys |
| Localization | localization/__init__.py | set_language(), t() function |

## CODE MAP
(LSP not available - basedpyright not installed)

## CONVENTIONS

**Critical Deviations:**
- No dependency management (no requirements.txt, pyproject.toml)
- Mixed test frameworks: unittest vs pytest
- Namespace packages without __init__.py (cards, orbs, relics, potions, utils, config)
- Root __main__.py entry point (unconventional for distribution)
- Duplicate "debug" in config/game_config.yaml and game_config.py

**Module Boundaries:**
- actions/, events/, map/, rooms/, player/, entities/ - proper packages
- engine/, ai/ - no __init__.py (namespace packages)

**Anti-Patterns (THIS PROJECT):**
- NEVER: events/neo_event.py:20 - Neo event special, not random
- ALWAYS: rooms/shop.py:176 - Rightmost relic is shop relic

## COMMANDS
```bash
# Run game
python __main__.py

# Run tests
python tests/test_*.py      # Individual test
pytest tests/                 # All tests
```

## NOTES
- No requirements.txt - dependencies must be installed manually
- Action queues: Each room manages its own (not in game_state anymore)
- Cards use 3-tier value system: base, combat, temp (for buffs)
- Map generation: Based on Slay the Spire algorithm with bad luck protection
- Unknown rooms (??): Resolve to Monster/Treasure/Shop/Event with relic modifiers
