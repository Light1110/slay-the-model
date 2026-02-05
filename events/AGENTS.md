# PROJECT KNOWLEDGE BASE - EVENTS MODULE

**Generated:** 2026-02-05 03:05:00
**Commit:** 8593596
**Branch:** main

## OVERVIEW
Event pool system with weighted selection and neo event support.

## STRUCTURE
```
events/
├── event_pool.py      # Main event pool with weighted random selection
├── neo_event.py         # Neo event special handling
├── base.py             # Base event class (not directly used)
└── __init__.py          # Module initialization
```

## WHERE TO LOOK

| Task | Location | Notes |
|-------|-----------|--------|
| Event pool | event_pool.py | Weighted event selection by floor, neo blessing |
| Event base | events/base.py | Base Event class (not used directly) |
| Neo event | neo_event.py | Special event handling (Neo reward) |
| Registration | All events | @register("event") decorator in event modules |
| Floor filtering | event_pool.py:115-140 | Events filtered by current_floor |

## CODE MAP

### Key Classes
```python
# Event pool manager (event_pool.py: 170 lines)
EventPool
    __init__(self)
    get_random_event(floor: int)
    mark_event_used(event_id: str)
    
# Event metadata (lines 12-22)
EventMetadata
    event_class: Event class
    event_id: str
    floor: int
    is_unique: bool
    is_neo: bool

# Neo event (neo_event.py: 67 lines)
NeoEvent(Event)
    trigger(self) -> Optional[Event]
```

### Event Registration Pattern
```python
@register("event")
class Event(Event):
    def trigger(self) -> Optional[Event]:
        ...
```

## CONVENTIONS

**Event Pool:**
- Weighted random selection based on floor number
- Unique events are marked and only appear once
- Events filtered by current_floor (min_floor/max_floor)
- Neo blessing grants bonus gold on first Neo event

**Neo Event:**
- Special event that can only appear once per run
- Rewards bonus gold (50% of total gold) when completed
- Marked as used in event pool via is_neo flag

**Floor Filtering:**
- Events have min_floor and max_floor properties
- Only events with min_floor <= current_floor <= max_floor are available
- Prevents impossible events from appearing too early

**Event Registration:**
- Use @register("event") decorator in event modules
- Store metadata in _event_registry dict (event_id, floor, is_unique, is_neo, event_class)

**Anti-Patterns (THIS PROJECT):**
- NEVER: events/neo_event.py:20 - Neo event special, not random
- ALWAYS: events/base.py - Abstract base class, don't instantiate directly

## COMMANDS
```bash
# Run game (includes events)
python __main__.py

# Run tests
pytest tests/test_event_pool.py -v      # Specific event tests
python tests/test_rooms.py -v             # Room tests (includes events)
```

## NOTES
- Event pool is initialized when GameState is created (game_state.event_pool = EventPool())
- Events trigger() method returns Optional[Event] - can return None if no follow-up
- Floor filtering prevents impossible events (e.g., combat too strong for floor 1)
- Neo blessing is a one-time reward that scales with total gold earned

## DEPENDENCIES
- engine/game_state (GameState singleton)
- utils/registry (@register decorator)
- utils/random (get_random_event helper)
- localization (t() function)
