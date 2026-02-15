from engine.game_flow import GameFlow
from engine.game_state import game_state
import os
import sys

# Import character cards to register them in the registry
# This must be done before any room tries to generate random cards
def _import_character_cards(character: str):
    """Import cards for the selected character to register them."""
    if character == "Ironclad":
        import cards.ironclad  # This triggers __init__.py which imports all Ironclad cards
    # Add other characters here as they are implemented


def _import_potions():
    """Import potions to register them in the registry."""
    import potions  # This triggers __init__.py which imports all potions


def _import_powers():
    """Import powers to register them in the registry."""
    from powers import definitions  # This triggers __init__.py which imports all powers


class TeeStream:
    """Duplicate writes to multiple streams."""
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()


def _setup_debug_logging():
    debug_config = game_state.config.get("debug", {})
    if isinstance(debug_config, bool):
        debug_enabled = debug_config
        log_path = "logs/debug.log"
    else:
        debug_enabled = debug_config.get("enable", False)
        log_path = debug_config.get("log_path", "logs/debug.log")
    
    if not debug_enabled:
        return None, None, None

    log_dir = os.path.dirname(log_path)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    log_file = open(log_path, "a", encoding="utf-8")

    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = TeeStream(sys.stdout, log_file)
    sys.stderr = TeeStream(sys.stderr, log_file)
    return log_file, original_stdout, original_stderr

if __name__ == "__main__":
    log_file, original_stdout, original_stderr = _setup_debug_logging()
    try:
        # Import character cards before starting game
        _import_character_cards(game_state.config.character)
        # Import potions to register them in the registry
        _import_potions()
        # Import powers to register them in the registry
        _import_powers()
        game = GameFlow()
        game.start_game(game_state)
    except KeyboardInterrupt:
        from localization import t
        print(f"\n{t('ui.game_interrupted', default='Game interrupted by user.')}")
    except Exception as e:
        from localization import t
        print(f"\n{t('ui.game_error', default=f'Game error: {e}', error=e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Restore original streams before closing log file
        if original_stdout:
            sys.stdout = original_stdout
        if original_stderr:
            sys.stderr = original_stderr
        if log_file:
            log_file.close()