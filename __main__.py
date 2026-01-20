from engine.game_flow import GameFlow

if __name__ == "__main__":
    try:
        game = GameFlow()
        game.start_game()
    except KeyboardInterrupt:
        from localization import t
        print(f"\n{t('ui.game_interrupted', default='Game interrupted by user.')}")
    except Exception as e:
        from localization import t
        print(f"\n{t('ui.game_error', default=f'Game error: {e}', error=e)}")
        import traceback
        traceback.print_exc()