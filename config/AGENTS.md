# CONFIG MODULE

## Overview
YAML-based game configuration with GameConfig class for settings management.

## Structure
```
config/
├── game_config.py     # GameConfig class (38 lines)
└── game_config.yaml  # Configuration file
```

## Core Components

### `game_config.py` (38 lines)
**GameConfig Class:**
- YAML loader with defaults
- Dict-like `get()` method for compatibility
- Settings: mode, language, seed, character, debug, debug_log_path

**Default Values:**
- `mode`: "human" (human play mode)
- `language`: "en" (English)
- `seed`: None (no seed set)
- `character`: "Ironclad"
- `debug`: False
- `debug_log_path`: "logs/debug.log"

### `game_config.yaml`
- YAML configuration file
- Loaded by `GameConfig.load(config_path)`
- Override defaults when present

## Where to Look

| Task | Location | Notes |
|-------|-----------|--------|
| Load config | `GameConfig.load("config/game_config.yaml")` | Returns GameConfig instance |
| Get setting | `config.mode` or `config.get("mode")` | Both methods work |
| Set seed | `config.seed = 42` | For reproducible runs |

## Conventions

**Configuration Flow:**
1. Create `game_config.yaml` to override defaults
2. Load via `GameConfig.load()` at game start
3. Use config attributes or `get()` method

**Dict Compatibility:**
- `config.get(key, default)` for backward compatibility
- Direct attribute access: `config.mode`, `config.language`

## Anti-Patterns

**NEVER:**
- Modify GameConfig defaults at runtime - use YAML instead
- Create multiple config instances - it's a singleton pattern
- Ignore return value of `load()` - it returns a new instance

**ALWAYS:**
- Store config in `game_state` or similar singleton
- Use YAML for user-facing settings
- Keep debug logging path configurable

## Code Map

```python
# Load configuration
config = GameConfig.load("config/game_config.yaml")

# Access settings
mode = config.mode               # "human" or "ai"
language = config.language         # "en" or "zh"
seed = config.seed               # None or int

# Dict-style access (for compatibility)
mode = config.get("mode", "human")
```
