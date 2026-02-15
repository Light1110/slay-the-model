# Import all card packages to ensure they are registered at module load time
import cards.ironclad  # noqa: F401
import cards.colorless  # noqa: F401


def create_player(character=None):
    """Create a player with character-specific starting deck and stats."""
    from player.player import Player
    
    if character == "Ironclad":
        return _create_ironclad()
    else:
        # Default player
        player = Player()
        if character:
            player.character = character
        return player


def _create_ironclad():
    """Create Ironclad character with starting deck."""
    from player.player import Player
    from player.card_manager import CardManager
    from cards.ironclad.strike import Strike
    from cards.ironclad.defend import Defend
    from cards.ironclad.bash import Bash
    from cards.namespaces import get_namespace_for_character
    
    # Create base player
    player = Player()
    player.character = "Ironclad"
    player.namespace = get_namespace_for_character("Ironclad")
    player._max_hp = 80
    player.max_hp = 80
    player.hp = 80
    
    # Ironclad starting deck: 5 Strike, 4 Defend, 1 Bash
    starting_deck = []
    for _ in range(5):
        starting_deck.append(Strike())
    for _ in range(4):
        starting_deck.append(Defend())
    starting_deck.append(Bash())
    
    # Re-initialize card manager with the starting deck
    player.card_manager = CardManager(starting_deck)
    
    return player