import unittest
from unittest.mock import patch

import main
from config import GameState


class _MenuStub:
    def __init__(self):
        self.pause_shown = False
        self.game_over_shown = False
        self.hidden = False

    def show_pause(self):
        self.pause_shown = True

    def show_game_over(self, _score):
        self.game_over_shown = True

    def hide(self):
        self.hidden = True


class _HudStub:
    def __init__(self, *_args, **_kwargs):
        self.cleaned = False

    def cleanup(self):
        self.cleaned = True


class _PlayerStub:
    def __init__(self, *_args, **_kwargs):
        self.is_alive = True
        self.health = 100
        self.max_health = 100
        self._healed_total = 0
        self.current_weapon = type('W', (), {'ammo_current': 0, 'ammo_max': 20})()

    def heal(self, amount):
        self._healed_total += amount
        return amount

    @property
    def health_percentage(self):
        return self.health / self.max_health


class GameSmokeTests(unittest.TestCase):
    def test_pause_resume_flow(self):
        game = main.Game()
        game.menu = _MenuStub()
        game.state = GameState.PLAYING

        game.pause()
        self.assertEqual(game.state, GameState.PAUSED)
        self.assertTrue(game.menu.pause_shown)

        game.resume()
        self.assertEqual(game.state, GameState.PLAYING)
        self.assertTrue(game.menu.hidden)

    def test_game_over_state(self):
        game = main.Game()
        game.menu = _MenuStub()
        game.game_over()
        self.assertEqual(game.state, GameState.GAME_OVER)
        self.assertTrue(game.menu.game_over_shown)

    def test_restart_path_calls_cleanup_and_start(self):
        game = main.Game()
        game.player = object()
        game.enemies = [object(), object()]
        game.hud = _HudStub()

        old_destroy = main.destroy
        old_start = game.start_game
        started = {'value': False}
        try:
            main.destroy = lambda _entity: None
            game.start_game = lambda: started.__setitem__('value', True)
            game.restart()
        finally:
            main.destroy = old_destroy
            game.start_game = old_start

        self.assertTrue(game.hud.cleaned)
        self.assertTrue(started['value'])

    def test_wave_progression_values(self):
        game = main.Game()
        game.start_wave(2)
        self.assertEqual(game.current_wave, 2)
        self.assertGreater(game.wave_target_enemies, 0)
        self.assertTrue(game.wave_in_progress)

    def test_start_game_smoke(self):
        game = main.Game()
        game.menu = _MenuStub()

        with patch.object(main.Game, 'create_level', lambda _self: None), \
             patch('entities.player.Player', _PlayerStub), \
             patch('ui.hud.HUD', _HudStub), \
             patch.object(main.Game, 'apply_runtime_settings', lambda _self, rebuild_hud=False: None), \
             patch.object(main.Game, 'clear_enemies', lambda _self: None), \
             patch.object(main.Game, 'clear_pickups', lambda _self: None), \
             patch.object(main.Game, 'clear_hazards', lambda _self: None), \
             patch.object(main.Game, 'start_wave', lambda _self, _w: None):
            game.start_game()

        self.assertEqual(game.state, GameState.PLAYING)
        self.assertTrue(game.menu.hidden)


if __name__ == '__main__':
    unittest.main()
