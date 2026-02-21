# Event Pool Refactor: Act-Based Categorization
## Implementation Plan

Generated: 2026-02-22
Objective: Refactor event pool registration system from floor-based to Act-based categorization

---

## EXECUTIVE SUMMARY

**Problem:** Events currently categorized by floor ranges ('early', 'mid', 'late', 'boss'), not matching Slay the Spire's Act-based system.

**Solution:** Replace floor-based pools with Act-based pools (1, 2, 3, shared) and update all event registrations.

**Impact:**
- 3 core files modified (event_pool.py, utils/random.py, rooms/event.py)
- 50+ event files updated with new `acts` parameter
- Maintains backward compatibility through migration
- Aligns with official StS event distribution

---

## CURRENT ARCHITECTURE

### Event Pool Structure
```python
# events/event_pool.py
class EventPool:
    def __init__(self):
        self._floor_pools: Dict[str, List[str]] = {
            'early': [],    # Floors 1-4
            'mid': [],      # Floors 5-10
            'late': [],     # Floors 11-15
            'boss': []      # Floor 16
        }

def register_event(event_id, floors='all', ...):
    # 'all' or 'early'/'mid'/'late'/'boss'
```

### Event Registration Pattern
```python
@register_event(
    event_id="big_fish",
    floors='early',  # ❌ Floor-based
    weight=100
)
class BigFishEvent(Event): ...
```

### Event Selection Flow
1. `EventRoom.init()` calls `get_random_events(floor, count, floors)`
2. `get_random_events()` calls `event_pool.get_available_events(floor)`
3. `get_available_events()` determines floor range and filters events
4. Returns weighted random selection from pool

---

## TARGET ARCHITECTURE

### Act-Based Pool Structure
```python
# events/event_pool.py
class EventPool:
    def __init__(self):
        self._act_pools: Dict[str, List[str]] = {
            1: [],      # Act 1 events
            2: [],      # Act 2 events
            3: [],      # Act 3 events
            'shared': [] # Common events (Acts 1-3)
        }

def register_event(event_id, acts='all', ...):
    # 'all' or [1, 2, 3] or [1, 2] or 'shared'
```

### New Event Registration Pattern
```python
@register_event(
    event_id="big_fish",
    acts=[1],  # ✅ Act-based
    weight=100
)
class BigFishEvent(Event): ...

@register_event(
    event_id="woman_in_blue",
    acts='shared',  # ✅ All Acts 1-3
    weight=100
)
class WomanInBlueEvent(Event): ...

@register_event(
    event_id="face_trader",
    acts=[1, 2],  # ✅ Multi-Act (Acts 1-2)
    weight=100
)
class FaceTraderEvent(Event): ...
```

### Act Selection Flow
1. `EventRoom.init()` calls `get_random_events(act, count, acts)`
2. `get_random_events()` calls `event_pool.get_available_events(act)`
3. `get_available_events()` filters events by current act
4. Returns weighted random selection from pool

---

## TASK BREAKDOWN

### Phase 1: Core Infrastructure (Sequential)

#### Task 1.1: Refactor EventPool Class
**File:** `events/event_pool.py`

**Changes:**
1. Replace `_floor_pools` with `_act_pools` in `__init__`
2. Update `EventMetadata` to store `acts` instead of `floors`
3. Update `register_event()` signature and logic:
   - Accept `acts` parameter (str 'all'/'shared' or List[int])
   - Handle multi-Act registration: `[1, 2]` adds to both Act 1 and Act 2 pools
   - `'all'` adds to Acts 1, 2, 3 (not 'shared' pool)
   - `'shared'` adds to 'shared' pool only
4. Update `get_available_events()` to use `act` parameter
5. Remove `_get_floor_range()` method
6. Update `_is_event_available()` for Act filtering
7. Keep `get_random_event()` signature but update to use act

**Dependencies:** None (foundational change)

**Validation:**
- Unit tests pass
- EventPool initializes with correct structure
- Register events with various `acts` values
- `get_available_events(act)` returns correct events

---

#### Task 1.2: Update @register_event Decorator
**File:** `events/event_pool.py`

**Changes:**
1. Update decorator signature:
   ```python
   def register_event(
       event_id: str,
       acts: Any = 'all',  # str 'all'/'shared' or List[int]
       weight: int = 100,
       requires_condition: Optional[Callable[[], bool]] = None,
       is_unique: bool = False
   ):
   ```

**Dependencies:** Task 1.1 complete

**Validation:**
- Decorator accepts both str and List[int]
- Decorator passes correct arguments to `event_pool.register_event()`

---

### Phase 2: Integration Updates (Parallel)

#### Task 2.1: Update utils/random.py
**File:** `utils/random.py`

**Changes:**
1. Update `get_random_events()` signature:
   ```python
   def get_random_events(act: int = 1, count: int = 1, acts: Optional[Any] = None) -> List[Any]:
       """
       Get random events from event pool based on criteria.

       args:
           act (int): Current act number for filtering (1-3).
           count (int): Number of events to return (default: 1).
           acts (Optional[Any]): Act filter (1, 2, 3, 'shared', 'all', or [1,2]).

       returns:
           List[Any]: List of event instances matching criteria.
       """
   ```

2. Replace floor-based filtering with Act-based:
   ```python
   available_metadata = event_pool.get_available_events(act)

   if acts and acts != 'all':
       available_metadata = [
           m for m in available_metadata
           if m.acts == acts or m.acts == 'all' or
              (isinstance(m.acts, list) and act in m.acts)
       ]
   ```

**Dependencies:** Task 1.1 complete

**Validation:**
- Function accepts `act` parameter
- Function filters events correctly by act
- Function handles `'shared'` and multi-Act events

---

#### Task 2.2: Update EventRoom
**File:** `rooms/event.py`

**Changes:**
1. Update `init()` method:
   ```python
   def init(self):
       from engine.game_state import game_state
       import events

       # Get random events based on current ACT
       event_count = self._get_event_count(game_state.current_act)
       act_filter = self._get_act_filter(game_state.current_act)

       # Get events from pool
       self.available_events = get_random_events(
           act=game_state.current_act,
           count=event_count,
           acts=act_filter
       )

       if not self.available_events:
           self._create_fallback_event()
   ```

2. Replace `_get_floor_range()` with `_get_act_filter()`:
   ```python
   def _get_act_filter(self, act: int) -> Any:
       """
       Get act filter for event filtering.

       Args:
           act: Current act number (1-3)

       Returns:
           Act filter (int 1-3 or None for all)
       """
       # Act 1: only Act 1 and shared events
       if act == 1:
           return None  # Will include Act 1 + shared
       # Act 2: Act 2, shared, and multi-Act [1,2]
       elif act == 2:
           return None  # Will include Act 2 + shared + [1,2]
       # Act 3: Act 3, shared, and multi-Act [2,3]
       elif act == 3:
           return None  # Will include Act 3 + shared + [2,3]
       return None
   ```

3. Update `_get_event_count()` to use act instead of floor:
   ```python
   def _get_event_count(self, act: int) -> int:
       """
       Determine how many events to offer based on act.

       Args:
           act: Current act number (1-3)

       Returns:
           Number of events to present
       """
       # Act 1: offer 1-2 events
       if act == 1:
           return 1
       # Act 2: offer 2-3 events
       elif act == 2:
           return 2
       # Act 3: offer 2-3 events
       else:
           return 2
   ```

**Dependencies:** Task 1.1 complete, Task 2.1 complete

**Validation:**
- EventRoom uses `game_state.current_act`
- Events are filtered correctly by act
- Fallback event created when no events available

---

### Phase 3: Event Registration Updates (Parallel)

#### Task 3.1: Update Common Events (Shared)
**Files:** 14 event files

**Events:** `a_note_for_yourself`, `bonfire_spirits`, `duplicator`, `divine_fountain`, `golden_shrine`, `lab`, `match_and_keep`, `ominous_forge`, `purifier`, `transmogrifier`, `upgrade_shrine`, `we_meet_again`, `wheel_of_change`, `woman_in_blue`

**Pattern:**
```python
@register_event(
    event_id="woman_in_blue",
    acts='shared',  # ✅ Changed from 'mid'
    weight=100
)
class WomanInBlueEvent(Event): ...
```

**Dependencies:** Task 1.2 complete

**Validation:**
- All 14 events have `acts='shared'`
- Events appear in all Acts 1-3

---

#### Task 3.2: Update Semi-Common Events
**Files:** 2 event files

**Events:**
- `face_trader`: Acts 1 and 2
- `designer_in_spire`: Acts 2 and 3

**Pattern:**
```python
@register_event(
    event_id="face_trader",
    acts=[1, 2],  # ✅ Multi-Act
    weight=100
)
class FaceTraderEvent(Event): ...

@register_event(
    event_id="designer_in_spire",
    acts=[2, 3],  # ✅ Multi-Act
    weight=100
)
class DesignerInSpireEvent(Event): ...
```

**Dependencies:** Task 1.2 complete

**Validation:**
- `face_trader` appears in Acts 1 and 2 only
- `designer_in_spire` appears in Acts 2 and 3 only

---

#### Task 3.3: Update Act 1 Exclusive Events
**Files:** 11 event files

**Events:** `big_fish`, `dead_adventurer`, `golden_idol`, `hypnotizing_mushrooms`, `living_wall`, `scrap_ooze`, `shining_light`, `the_cleric`, `the_ssssserpent`, `wing_statue`, `world_of_goop`

**Pattern:**
```python
@register_event(
    event_id="big_fish",
    acts=[1],  # ✅ Changed from 'early'
    weight=100
)
class BigFishEvent(Event): ...
```

**Dependencies:** Task 1.2 complete

**Validation:**
- All 11 events have `acts=[1]`
- Events appear only in Act 1

---

#### Task 3.4: Update Act 2 Exclusive Events
**Files:** 16 event files

**Events:** `ancient_writing`, `augmenter`, `council_of_ghosts`, `cursed_tome`, `forgotten_altar`, `knowing_skull`, `masked_bandits`, `nloth`, `old_beggar`, `pleading_vagrant`, `the_colosseum`, `the_joust`, `the_library`, `the_mausoleum`, `the_nest`, `vampires`

**Pattern:**
```python
@register_event(
    event_id="ancient_writing",
    acts=[2],  # ✅ Changed from 'mid'
    weight=100
)
class AncientWritingEvent(Event): ...
```

**Dependencies:** Task 1.2 complete

**Validation:**
- All 16 events have `acts=[2]`
- Events appear only in Act 2

---

#### Task 3.5: Update Act 3 Exclusive Events
**Files:** 8 event files

**Events:** `falling`, `mind_bloom`, `mysterious_sphere`, `secret_portal`, `sensory_stone`, `the_moai_head`, `tomb_of_lord_red_mask`, `winding_halls`

**Pattern:**
```python
@register_event(
    event_id="falling",
    acts=[3],  # ✅ Changed from 'late'
    weight=100
)
class FallingEvent(Event): ...
```

**Dependencies:** Task 1.2 complete

**Validation:**
- All 8 events have `acts=[3]`
- Events appear only in Act 3

---

#### Task 3.6: Handle Legacy Events
**Files:** 2 event files

**Events:** `house_of_god`, `the_shrine`

**Action:**
- Review event implementations
- If unused/misnamed, comment out registration or mark as deprecated
- If should be in game, categorize appropriately

**Dependencies:** Task 1.2 complete

**Validation:**
- Legacy events handled appropriately
- No broken registrations

---

### Phase 4: Testing & Validation (Sequential)

#### Task 4.1: Update Event Tests
**Files:** `tests/test_events.py` (or equivalent)

**Changes:**
1. Update test fixtures to use `acts` parameter
2. Update test cases to use Act-based filtering
3. Add tests for multi-Act events
4. Add tests for 'shared' events

**Dependencies:** All Phase 1-3 tasks complete

**Validation:**
- All existing tests pass
- New tests verify Act-based behavior

---

#### Task 4.2: Integration Testing
**Files:** Manual testing, `run_game_test.py`

**Changes:**
1. Run automated game simulations
2. Verify events appear in correct Acts
3. Verify event selection weightings work
4. Verify multi-Act events appear in correct Acts
5. Verify unique events work across Acts

**Dependencies:** Task 4.1 complete

**Validation:**
- Events appear in correct Acts
- Weighted selection works
- Unique events work correctly
- No errors during gameplay

---

## PARALLEL EXECUTION GRAPH

```
Phase 1 (Sequential)
├─ Task 1.1: Refactor EventPool Class
└─ Task 1.2: Update @register_event Decorator
       └─ Depends: 1.1

Phase 2 (Parallel - All depend on Phase 1)
├─ Task 2.1: Update utils/random.py
│   └─ Depends: 1.1
├─ Task 2.2: Update EventRoom
│   └─ Depends: 1.1, 2.1
└─ Task 3.x: Update Event Registrations (Parallel)
    ├─ Task 3.1: Common Events (14 files)
    │   └─ Depends: 1.2
    ├─ Task 3.2: Semi-Common Events (2 files)
    │   └─ Depends: 1.2
    ├─ Task 3.3: Act 1 Events (11 files)
    │   └─ Depends: 1.2
    ├─ Task 3.4: Act 2 Events (16 files)
    │   └─ Depends: 1.2
    ├─ Task 3.5: Act 3 Events (8 files)
    │   └─ Depends: 1.2
    └─ Task 3.6: Legacy Events (2 files)
        └─ Depends: 1.2

Phase 3 (Sequential - Depends on all Phase 2)
├─ Task 4.1: Update Event Tests
│   └─ Depends: All Phase 2 tasks
└─ Task 4.2: Integration Testing
    └─ Depends: 4.1
```

---

## EVENT CATEGORIZATION MATRIX

| Event ID | Current floors | New acts | Notes |
|----------|---------------|-----------|-------|
| **Common (Shared) - Acts 1-3** |
| a_note_for_yourself | 'all' | 'shared' | |
| bonfire_spirits | 'all' | 'shared' | |
| duplicator | 'all' | 'shared' | |
| divine_fountain | 'all' | 'shared' | |
| golden_shrine | 'all' | 'shared' | |
| lab | 'all' | 'shared' | |
| match_and_keep | 'all' | 'shared' | |
| ominous_forge | 'all' | 'shared' | |
| purifier | 'all' | 'shared' | |
| transmogrifier | 'all' | 'shared' | |
| upgrade_shrine | 'all' | 'shared' | |
| we_meet_again | 'all' | 'shared' | |
| wheel_of_change | 'all' | 'shared' | |
| woman_in_blue | 'mid' | 'shared' | Was mid, should be shared |
| **Semi-Common** |
| face_trader | 'early' | [1, 2] | Was early, should be Acts 1-2 |
| designer_in_spire | 'mid' | [2, 3] | Was mid, should be Acts 2-3 |
| **Act 1 Exclusive** |
| big_fish | 'early' | [1] | |
| dead_adventurer | 'early' | [1] | |
| golden_idol | 'early' | [1] | |
| hypnotizing_mushrooms | 'early' | [1] | |
| living_wall | 'early' | [1] | |
| scrap_ooze | 'early' | [1] | |
| shining_light | 'early' | [1] | |
| the_cleric | 'early' | [1] | |
| the_ssssserpent | 'early' | [1] | |
| wing_statue | 'early' | [1] | |
| world_of_goop | 'early' | [1] | |
| **Act 2 Exclusive** |
| ancient_writing | 'mid' | [2] | |
| augmenter | 'mid' | [2] | |
| council_of_ghosts | 'mid' | [2] | |
| cursed_tome | 'mid' | [2] | |
| forgotten_altar | 'mid' | [2] | |
| knowing_skull | 'mid' | [2] | |
| masked_bandits | 'mid' | [2] | |
| nloth | 'mid' | [2] | |
| old_beggar | 'mid' | [2] | |
| pleading_vagrant | 'mid' | [2] | |
| the_colosseum | 'mid' | [2] | |
| the_joust | 'mid' | [2] | |
| the_library | 'mid' | [2] | |
| the_mausoleum | 'mid' | [2] | |
| the_nest | 'mid' | [2] | |
| vampires | 'mid' | [2] | |
| **Act 3 Exclusive** |
| falling | 'late' | [3] | |
| mind_bloom | 'late' | [3] | |
| mysterious_sphere | 'late' | [3] | |
| secret_portal | 'late' | [3] | |
| sensory_stone | 'late' | [3] | |
| the_moai_head | 'late' | [3] | |
| tomb_of_lord_red_mask | 'late' | [3] | |
| winding_halls | 'late' | [3] | |
| **Legacy (Review)** |
| house_of_god | ??? | Review | |
| the_shrine | ??? | Review | |

---

## RISK MITIGATION

### Risk 1: Breaking Existing Event Registrations
**Mitigation:** Maintain backward compatibility in `register_event()`
- Accept both old `floors` and new `acts` parameters
- If `floors` provided, auto-convert to `acts`:
  - 'early' → [1]
  - 'mid' → [2]
  - 'late' → [3]
  - 'boss' → [3] (boss floors in Act 3)
  - 'all' → 'shared'

### Risk 2: Event Distribution Changes
**Mitigation:**
- Document event distribution changes
- Run integration tests before/after
- Keep fallback event logic

### Risk 3: Multi-Act Event Complexity
**Mitigation:**
- Thoroughly test multi-Act events
- Verify events appear in correct Acts
- Test unique events across Acts

### Risk 4: Legacy Events Breaking
**Mitigation:**
- Review legacy events before updating
- If unused, comment out registration
- If needed, categorize appropriately

---

## SUCCESS CRITERIA

### Functional Requirements
- ✅ EventPool uses `_act_pools` with Acts 1, 2, 3, 'shared'
- ✅ `@register_event` accepts `acts` parameter
- ✅ `get_random_events()` uses Act-based filtering
- ✅ EventRoom uses `game_state.current_act`
- ✅ All 50+ events properly categorized by Act
- ✅ Multi-Act events ([1, 2], [2, 3]) work correctly
- ✅ Shared events ('shared') appear in all Acts 1-3
- ✅ Unique events work across Acts

### Non-Functional Requirements
- ✅ No breaking changes to existing game flow
- ✅ Event selection weightings maintained
- ✅ Fallback event logic preserved
- ✅ All existing tests pass
- ✅ New tests for Act-based behavior
- ✅ Integration tests pass

### Code Quality
- ✅ Follows Google Python Style Guide
- ✅ Type hints correct
- ✅ Docstrings updated
- ✅ No circular imports
- ✅ LSP diagnostics clean

---

## DELIVERABLES

1. **Refactored EventPool class** (`events/event_pool.py`)
   - `_act_pools` structure
   - Act-based filtering
   - Multi-Act support

2. **Updated @register_event decorator** (`events/event_pool.py`)
   - `acts` parameter
   - Backward compatibility

3. **Updated get_random_events() function** (`utils/random.py`)
   - Act-based selection
   - Multi-Act support

4. **Updated EventRoom class** (`rooms/event.py`)
   - Uses `current_act`
   - Act filtering

5. **Categorized events** (50+ event files)
   - Common (shared): 14 events
   - Semi-common: 2 events
   - Act 1: 11 events
   - Act 2: 16 events
   - Act 3: 8 events
   - Legacy: 2 events reviewed

6. **Updated tests** (`tests/test_events.py`)
   - Act-based test cases
   - Multi-Act event tests
   - Shared event tests

7. **Integration testing** (`run_game_test.py`)
   - Automated game simulations
   - Act verification

---

## ESTIMATED EFFORT

| Phase | Tasks | Effort |
|-------|--------|----------|
| Phase 1: Core Infrastructure | 2 tasks | 2 hours |
| Phase 2: Integration Updates | 2 tasks | 1 hour |
| Phase 3: Event Registrations | 6 tasks | 2 hours |
| Phase 4: Testing & Validation | 2 tasks | 1.5 hours |
| **Total** | **12 tasks** | **6.5 hours** |

---

## REFERENCE MATERIALS

### Slay the Spire Wiki
- Event distribution by Act
- Event IDs and requirements
- Multi-Act events list

### Current Codebase
- `events/event_pool.py` - Event pool implementation
- `utils/random.py` - Random selection functions
- `rooms/event.py` - Event room logic
- `events/__init__.py` - Event organization

### Game State
- `engine/game_state.py` - `current_act` and `floor_in_act`
- `FLOORS_PER_ACT = 18`
- `MAX_ACTS = 4`

---

**END OF IMPLEMENTATION PLAN**
