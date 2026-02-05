# PROJECT KNOWLEDGE BASE - MAP MODULE

**Generated:** 2026-02-05 03:05:00
**Commit:** 8593596
**Branch:** main

## OVERVIEW
Procedural map generation system based on Slay-the-Spire algorithm with bad luck protection.

## STRUCTURE
```
map/
├── map_manager.py      # Main map manager (700 lines, complex display/JSON)
├── base.py            # MapNode and MapData data structures
├── path_generator.py   # Path generation algorithm
└── __init__.py         # Module initialization
```

## WHERE TO LOOK

| Task | Location | Notes |
|-------|-----------|--------|
| Map generation | map_manager.py | Main controller, room creation, floor transition |
| Path algorithm | path_generator.py | Slay-the-Spire map generation logic |
| Map display | map_manager.py:400-540 | ASCII art and JSON rendering |
| Room creation | map_manager.py:110-210 | _create_room_instance() switch |
| Data structures | map/base.py | MapNode, MapData (coordinates, type, parent) |

## CODE MAP

### Key Classes
```python
# Map manager (map_manager.py: ~700 lines)
MapManager
    __init__(self, seed: int, act_id: int)
    generate_map(floor: int)
    _create_room_instance(room_type: RoomType) -> Room
    _resolve_unknown_type(floor: int) -> RoomType
    _get_available_moves(node: MapNode, visited: set) -> List[MapNode]
    _display_map() -> None
    _to_json() -> dict
    _to_ascii() -> None
    
# Map data structures (map/base.py: 80 lines)
MapNode
    x: int
    y: int
    room: Room  # or None
    edges: List[MapNode]
    children: List[MapNode]  # Optional
    depth: int
    
MapData
    nodes: List[MapNode]
    current_floor: int
    current_position: MapNode
    start_node: MapNode
    end_node: MapNode
```

### Map Generation Algorithm
```python
# path_generator.py (Slay-the-Spire algorithm)
generate_map_structure(...)
    # 10 paths to boss
    # Each path: 6-9 rooms
    # Ensures path exists: check_path_exists()
    # Bad luck protection: re-generate if impossible
```

### Room Type Distribution
```python
# Floor 1: 15 rooms
# Floor 2-3: 13-15 rooms
# Floor 4-15: 13-15 rooms
```

### Unknown Room Resolution
```python
# MapManager._resolve_unknown_type(floor: int) -> RoomType
# Unknown rooms (??) resolve based on floor and RNG:
# - Floor 1: 50% Monster, 25% Treasure, 25% Event, 0% Shop/Unknown
# - Floor 2-3: Weighted random selection
# - Floor 4+: All room types available
```

## CONVENTIONS

**Map Generation:**
- Slay-the-Spire map generation algorithm with bad luck protection
- Procedural generation based on seed (deterministic)
- Path ensures at least one viable route to boss
- Check path exists before creation (check_path_exists())

**Unknown Rooms:**
- Unknown rooms (??) in map resolve at enter() time
- Resolution depends on floor number and RNG
- Lower floors have fewer room types available
- Higher floors have all room types available
- Resolution logic in MapManager._resolve_unknown_type()

**Map Display:**
- Two rendering modes: ASCII art (_to_ascii) and JSON (_to_json)
- ASCII: Complex multi-line art showing room types and connections
- JSON: Full map structure for external tools
- Toggle via display_mode in config (not implemented yet)

**MapManager Integration:**
- GameState singleton contains MapManager instance
- MapManager generates rooms via _create_room_instance()
- Room types registered in utils/registry with @register("room")

**Anti-Patterns (THIS PROJECT):**
- ALWAYS: map/map_manager.py:400-540 - Dual map/ directories (map at root and in engine/)
- NEVER: map/map_manager.py:110-210 - Manually format complex ASCII art
- NEVER: Duplicate Room creation logic in GameFlow - MapManager handles it
- NEVER: Hardcode room counts - Use procedural generation
- ALWAYS: Unknown rooms resolve at enter() - not during map generation

## COMMANDS
```bash
# Run game (map generation included)
python __main__.py

# Run tests
pytest tests/test_map_system.py -v           # Map generation tests
pytest tests/test_map_selection.py -v         # Room selection logic
python tests/test_map_core.py -v               # MapNode/MapData structure
pytest tests/test_no_crossing.py -v            # Path collision detection
```

## NOTES
- Map generation uses fixed seed for reproducibility
- Path generation ensures there's always at least one way to reach boss
- Bad luck protection re-generates map segments if no valid path found
- Display mode not yet configurable (defaults to ASCII)
- MapManager is responsible for room creation, not GameFlow
