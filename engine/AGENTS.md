# ENGINE MODULE KNOWLEDGE BASE

**Generated:** 2025-02-05
**Purpose:** Core game loop, global state, and combat management

## OVERVIEW
Core engine managing game flow, global state, and combat turn systems.

## STRUCTURE
```
engine/
├── game_flow.py       # Room iteration, win/death handling
├── game_state.py      # Singleton global state (player, map, config)
├── combat_state.py     # Turn counters, orb tracking
├── game_stats.py      # Neo blessing HP modifiers
└── combat.py          # Independent combat logic (room/event triggerable)
```

## WHERE TO LOOK

| Task | Location | Notes |
|-------|-----------|--------|
| Room loop | game_flow.py:42 | Iterates rooms, checks WIN/DEATH, manages Neo room |
| Global state | game_state.py | Singleton instance, contains player, map_manager, combat_state |
| Turn management | combat_state.py | per_combat/per_turn counters, orb_history, power_cards_played |
| Combat start | combat.py:43 | Triggered by CombatRoom or Events, independent action queue |
| Neo blessings | game_stats.py | Character-specific HP increase/decrease values |

## CONVENTIONS

**Architecture:**
- GameState/CombatState/GameStats are singletons (game_state/game_stats instances)
- Action queues are local to rooms/events (NOT in game_state anymore)
- Combat class independent from room system - can be triggered by CombatRoom or Events
- game_phase tracks current state: "room", "map", "menu", "game_over"

## ANTI-PATTERNS

**Critical:**
- game_flow.py:111 - TODO: Implement player selection or AI decision (currently selects first available)
- combat.py:102 - TODO: Turn logic placeholder - _build_turn_actions empty
- Combat._execute_actions - Player turn handling incomplete (enemy turn placeholder)
