# PROJECT KNOWLEDGE BASE - PLAYER MODULE

**Generated:** 2026-02-05 03:05:00
**Commit:** 8593596
**Branch:** main

## OVERVIEW
Player state management with HP, energy, cards, relics, orbs, and potions.

## STRUCTURE
```
player/
├── player.py          # Main Player class
├── card_manager.py     # Card management (deck, draw pile, hand, discard, exhaust)
└── __init__.py         # Module initialization
```

## WHERE TO LOOK

| Task | Location | Notes |
|-------|-----------|--------|
| Player state | player/player.py | HP, energy, gold, max_hp, relics, orbs |
| Card management | player/card_manager.py | Deck manipulation, drawing, upgrading |
| Energy system | player/player.py: Energy resets each turn, max_energy determines actions |
| Status effects | player/player.py | Powers, potions, orbs modify state |

## CODE MAP

### Player Class (player/player.py: 200 lines)
```python
class Player:
    def __init__(self, character: str = "ironclad"):
        # Core stats
        self.max_hp = 70
        self.current_hp = self.max_hp
        self.max_energy = 3
        self.current_energy = self.max_energy
        self.gold = 99
        self.floor = 0
        self.act = 1
        
        # Collections
        self.relics = []
        self.orbs = []
        self.potions = []
        self.cards = {}  # Keyed by card type namespace
        
        # Managers
        self.card_manager = CardManager(self)
        
        # Character-specific setup
        self._setup_character()
    
    def _setup_character(self):
        """Initialize character-specific starting deck and stats"""
        character = self.character.lower()
        
        if character == "ironclad":
            self.max_hp = 80
            self.current_hp = 80
            self.max_energy = 3
            self.gold = 99
            self.cards["Attack"] = ["Strike"] * 4 + ["Bash"] * 4 + ["Defend"] * 4
        # Add other character setups here
    
    def take_damage(self, amount: int):
        """Take damage (reduce HP)"""
        self.current_hp = max(0, self.current_hp - amount)
        
    def heal(self, amount: int):
        """Heal (increase HP, capped at max_hp)"""
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        
    def add_energy(self, amount: int):
        """Add/subtract energy, capped at bounds"""
        self.current_energy = min(self.max_energy, max(0, self.current_energy + amount))
        self.current_energy = max(self.max_energy, self.current_energy + amount)
    
    def add_gold(self, amount: int):
        """Add gold (can be negative for purchases)"""
        self.gold += amount
```

### CardManager Class (player/card_manager.py: 300 lines)
```python
class CardManager:
    def __init__(self, player: Player):
        self.player = player
        
        # Card piles
        self.piles = {
            'deck': [],      # Draw pile
            'hand': [],      # Current playable cards
            'discard': [],   # Discarded this turn
            'exhaust': [],  # Removed from game
            'draw': [],      # Drawing pile (for future)
        }
    
    def get_pile(self, pile_name: str) -> List[Card]:
        """Get card pile by name"""
        return self.piles.get(pile_name, [])
    
    def add_to_pile(self, pile_name: str, card: Card):
        """Add card to specific pile"""
        if pile_name in self.piles:
            self.piles[pile_name].append(card)
    
    def remove_from_pile(self, pile_name: str, card: Card):
        """Remove card from specific pile"""
        if pile_name in self.piles and card in self.piles[pile_name]:
            self.piles[pile_name].remove(card)
    
    def draw_cards(self, count: int = 5):
        """Draw specified number of cards from deck to hand"""
        drawn = []
        for _ in range(count):
            if self.piles['deck']:
                card = self.piles['deck'].pop()
                self.piles['hand'].append(card)
                drawn.append(card)
        return drawn
```

### Energy System

```python
# Energy management (player/player.py)
- max_energy: Character-specific maximum (3 for ironclad)
- current_energy: Resets to max_energy each turn
- Negative energy allowed (can go below 0)
- add_energy() clamps at bounds [0, max_energy]
- Energy determines available card plays
```

### Card Piles

```python
# Standard card piles (card_manager.py)
'deck'      - Library of all cards, draw from here
'hand'       - Currently playable cards
'discard'    - Cards played this turn, go here at end of turn
'exhaust'    - Permanently removed from game
'draw'       - Future cards to be drawn
```

### Character-Specific Setup

```python
# _setup_character() in Player (player/player.py:180-190)
character == "ironclad":
    max_hp: 80
    max_energy: 3
    Starting deck: 5 Attacks, 5 Defends
    Gold: 99
```

## CONVENTIONS

**Player State:**
- Player is instantiated in GameState with character parameter
- All state is in single Player instance
- Game state accesses player via game_state.player

**Card Management:**
- CardManager is owned by Player instance
- Cards are objects (not strings) when in piles
- Piles are List[Card] for easy manipulation

**Energy System:**
- Energy resets to max_energy at start of each turn
- Cards have energy_cost that must be paid to play
- Can't play card if current_energy < energy_cost

**Character System:**
- Character parameter in Player.__init__ determines setup
- _setup_character() configures max_hp, max_energy, starting deck
- Characters have different starting stats and decks

**Anti-Patterns (THIS PROJECT):**
- NEVER: Direct card string access - use card.name
- NEVER: Bypass energy checks when playing cards
- NEVER: Modify energy without clamping at bounds [0, max_energy]
- NEVER: Add cards to deck without proper type/namespace

## COMMANDS
```bash
# Run game
python __main__.py

# Run tests
pytest tests/test_player.py -v              # Player state tests
```

## NOTES
- Character-specific decks loaded via character parameter
- Energy resets each combat turn (not player turn)
- Drawing uses deck → hand → play → discard flow
- Gold tracks currency for shops and events
