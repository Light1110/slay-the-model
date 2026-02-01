def create_player(character=None):
    from player.player import Player
    player = Player()
    if character:
        player.character = character
    return player