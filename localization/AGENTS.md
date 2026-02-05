# LOCALIZATION MODULE

## Overview
Multi-language support system with YAML-based translations, dynamic key resolution, and runtime language switching.

## Structure
```
localization/
├── __init__.py     # Core localization engine
├── en.yaml          # English translations (13KB)
└── zh.yaml          # Chinese translations (14KB)
```

## Core Components

### `__init__.py` (119 lines)
**Main Functions:**
- `set_language(lang: str)` - Switch language at runtime
- `t(key: str, default=None, **kwargs) -> str` - Translate key with formatting
- `_load_all_translations()` - Load all *.yaml files on module import

**Key Classes:**
- `LocalStr(key, **kwargs)` - Localized string wrapper, defers resolution
- `ConcatLocalStr(left, right)` - Concatenates two localized strings
- `Localizable` - Mixin for cards/relics with `localize(field)` method

**Translation Structure:**
- YAML files support nested keys: `cards.name.Strike`
- `_flatten_dict()` converts nested YAML to dotted keys: `cards.name.Strike`
- Dynamic formatting: `t("cards.name", value=5)` formats `{value}` in translation

## Where to Look

| Task | Location | Notes |
|-------|-----------|--------|
| Set language | `set_language()` | Changes global `current_language` |
| Translate text | `t(key, **kwargs)` | Falls back to `default` or `key` if missing |
| Localized cards | `Localizable` mixin | Use `self.local("name")` for card names |
| Format translations | `t().format(**kwargs)` | Supports `{variable}` placeholders |

## Conventions

**Translation Keys:**
- Format: `{prefix}.{ClassName}.{field}`
- Example: `cards.Strike.name`, `relics.BurningBlood.description`
- Class-based resolution via `Localizable._get_localized_key()`

**Runtime Behavior:**
- All translations loaded on import from `localization/*.yaml`
- Missing keys return default or the key itself
- Formatting errors silently pass through

## Anti-Patterns

**NEVER:**
- Hardcode text directly in classes - use `Localizable`
- Assume English is always available - check translations dict
- Modify translations at runtime - they're read-only after load

**ALWAYS:**
- Use `Localizable` mixin for all game entities
- Use `t()` for dynamic UI text
- Check `has_local(field)` before displaying localized content

## Code Map

```
set_language("zh")        # Switch to Chinese
t("cards.name.Strike")      # Returns "打击"
LocalStr("cards.name.Strike").resolve()  # Deferred translation
card.local("description")   # Uses `cards.{ClassName}.description` key
```
