# AI TOOLS MODULE

## Overview
AI helper functions for map data extraction and formatting for decision making.

## Structure
```
ai_tools/
├── map_tools.py   # Map formatting tools (100 lines)
└── __init__.py      # Namespace package
```

## Core Components

### `map_tools.py` (100 lines)
**Main Functions:**
- `get_map_context_for_ai(map_manager) -> Dict` - Complete AI context
- `format_map_ascii(map_manager) -> str` - ASCII map representation
- `format_map_json(map_manager) -> Dict` - Structured JSON data

**Map Context Structure (returned by get_map_context_for_ai):**
- `current_floor`: Current floor number (int)
- `current_position`: Current position index (int)
- `map_ascii`: ASCII string representation
- `map_json`: Structured JSON data
- `available_moves`: List of available next moves with metadata

**JSON Map Structure:**
- `structure`: List of floors, each floor is list of nodes
- `total_floors`: Total number of floors (int)
- Each node: position, room_type, visited (bool), connections_up (list)

## Where to Look

| Task | Location | Notes |
|-------|-----------|--------|
| Get AI context | `get_map_context_for_ai()` | Returns complete dict |
| ASCII map | `format_map_ascii()` | Human-readable string |
| JSON map | `format_map_json()` | Machine-readable dict |
| Move options | `available_moves` list | Has risk/reward levels |

## Conventions

**AI Integration:**
- Use `get_map_context_for_ai()` for complete context
- Pass context to `ai.AIDecisionEngine.make_map_decision()`
- ASCII map for visual understanding, JSON for structured data
- Risk/reward levels help AI evaluate moves

## Anti-Patterns

**NEVER:**
- Construct map context manually - use helper functions
- Ignore `visited` status - only unvisited nodes matter for moves
- Assume floor/position are always valid - check bounds

**ALWAYS:**
- Use `get_map_context_for_ai()` for complete context
- Pass `map_manager` instance, not raw data
- Handle empty `available_moves` gracefully

## Code Map

```python
# Get complete map context for AI
context = get_map_context_for_ai(game_state.map_manager)

# Visualize (for debugging or LLM understanding)
print(context["map_ascii"])

# Inspect available moves
for move in context["available_moves"]:
    print(f"Move {move['index']}: {move['room_type']}")
    print(f"  Risk: {move['risk_level']}, Reward: {move['reward_level']}")

# Pass to AI
choice = ai_engine.make_map_decision(context)
```
