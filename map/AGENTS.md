# MAP SYSTEM

**Generated:** 2025-02-05 02:05:00
**Commit:** 9106d4e
**Branch:** main

## OVERVIEW
Procedural map generation and navigation system implementing Slay the Spire's algorithm with weighted room types, bad luck protection, and line crossing prevention.

## WHERE TO LOOK

| Task | Location | Notes |
|-------|-----------|--------|
| Map generation | map_manager.py | 700 lines, weighted selection, floor structure, connections |
| Node representation | map_node.py | Floor, position, room_type, connections_up |
| Map state | map_data.py | 2D array [floor][position], current position |
| Weighted room types | map_manager.py:28-34 | ROOM_TYPE_WEIGHTS - Monster:53, Elite:8, Rest:12, Merchant:5, Unknown:22 |
| Bad luck protection | map_manager.py:52-58 | unknown_room_visits counter increases non-chosen type probabilities |
| Line crossing prevention | map_manager.py:141-173 | min_allowed_position ensures left→right connections only |
| Unknown room resolution | map_manager.py:629-699 | Tiny Chest/Juzu Bracelet/Ssserpent Head modifiers, relic checks |

## CONVENTIONS
- **2D array access:** nodes[floor][position] (0-based)
- **Fixed floors:** 0=Monster(easy), 8=Treasure, 14=Rest, 15=Boss, 16=empty
- **Connection direction:** nodes store connections_up (to next floor only)
- **Room instances:** Created on-demand in move_to_node(), not stored in nodes
- **Relic checks:** _normalize_relic_name() supports idstr/name/class name formats

## ANTI-PATTERNS
- NEVER: Modify ROOM_TYPE_WEIGHTS after initialization
- NEVER: Connect nodes crossing lines (violates min_allowed_position invariant)
- NEVER: Skip unknown_room_visits tracking (breaks bad luck protection)
- NEVER: Store Room instances in MapNode (created dynamically)
