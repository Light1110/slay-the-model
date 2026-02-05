# AI MODULE

## Overview
AI decision engine interface for autonomous gameplay with mock implementation for testing.

## Structure
```
ai/
├── ai_interface.py   # AI decision engine (174 lines)
└── __init__.py       # Namespace package
```

## Core Components

### `ai_interface.py` (174 lines)
**AIDecisionEngine (Base Class):**
- Interface for AI-based game decisions
- `make_map_decision(map_context: Dict) -> int` - Choose next map node
- Debug logging support

**Map Context Structure:**
- `current_floor`: Current floor number (int)
- `current_position`: Current position index (int)
- `map_ascii`: ASCII representation (string)
- `map_json`: Structured JSON data (dict)
- `available_moves`: List of available next moves
  - `index`: Position in list (0-based)
  - `floor`: Target floor number
  - `position`: Target position on floor
  - `room_type`: Room type (string enum)
  - `risk_level`: NONE/LOW/MEDIUM/HIGH/VERY_HIGH/RANDOM
  - `reward_level`: NONE/HEAL/SHOP/MEDIUM/HIGH/VERY_HIGH/RANDOM

**MockAIDecisionEngine (Test Implementation):**
- Simple heuristics for testing without LLM
- Strategies: "first", "last", "random", "least_risk", "highest_reward"
- Debug logging support

## Where to Look

| Task | Location | Notes |
|-------|-----------|--------|
| AI decision | `make_map_decision()` | Returns index of chosen move |
| Test AI | `MockAIDecisionEngine` | Use for unit tests |
| Get map data | `ai_tools.get_map_context_for_ai()` | Returns complete context |
| Debug mode | Pass `debug=True` | Prints detailed logs |

## Conventions

**AI Integration:**
- Subclass `AIDecisionEngine` for custom AI
- Implement `make_map_decision()` to choose map node
- Use `available_moves` list - return index (not position)
- Map context provided by `ai_tools.get_map_context_for_ai()`

**Mock Engine:**
- Use `MockAIDecisionEngine` for testing
- Strategies: "least_risk" for safe play, "highest_reward" for greed

## Anti-Patterns

**NEVER:**
- Return position directly - return index in `available_moves` list
- Ignore risk/reward levels - use them for decision making
- Assume `available_moves` is never empty - check length first

**ALWAYS:**
- Return index (0-based) from `make_map_decision()`
- Handle empty `available_moves` by raising ValueError
- Use debug logging for troubleshooting AI decisions

## Code Map

```python
# Create AI engine
ai = MockAIDecisionEngine(strategy="least_risk", debug=True)

# Get map context from game state
map_context = ai_tools.get_map_context_for_ai(game_state.map_manager)

# Make decision
choice_index = ai.make_map_decision(map_context)

# Apply decision
chosen_move = map_context["available_moves"][choice_index]
game_state.map_manager.move_to(chosen_move["floor"], chosen_move["position"])
```
