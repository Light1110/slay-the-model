# EVENTS MODULE

**Generated:** 2025-02-05 02:10:00
**Commit:** 9106d4e
**Branch:** main

## OVERVIEW
Weighted event pool system with floor-based filtering and unique event tracking for random Unknown Room encounters.

## WHERE TO LOOK

| Task | Location | Notes |
|-------|-----------|--------|
| Event registration | events/event_pool.py | @register_event decorator, global event_pool |
| Weighted selection | events/event_pool.py:124-147 | random.choices with weights array |
| Floor pools | events/event_pool.py:50-55 | early(1-4), mid(5-10), late(11-15), boss(16) |
| Base Event class | events/base_event.py:10-64 | Action queue per event, event_ended flag |
| Neo blessing | events/neo_event.py:17-22 | weight=0, special starting event |

## CONVENTIONS

- **Decorator pattern**: All events use @register_event() decorator for automatic registration
- **Action ownership**: Each event has its own ActionQueue (not shared with room)
- **Floor filtering**: Use 'early', 'mid', 'late', 'boss', or 'all' in decorator
- **Weight defaults**: Standard weight = 100, Neo event = 0 (never selected randomly)

## ANTI-PATTERNS

- **NEVER**: events/neo_event.py:20 - Neo event has weight=0, should not be in random pool
- **NEVER**: Trigger events manually without calling .end_event() - action queue may continue
- **ALWAYS**: Mark unique events used via event_pool.mark_event_used() after triggering
