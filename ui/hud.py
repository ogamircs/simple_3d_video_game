"""
HUD (Heads-Up Display)
Doom-style status bar at the bottom of the screen.
"""
import math
from ursina import Entity, Text, camera, color, invoke, destroy, time
from config import (
    UI_FONT_PRIMARY,
    UI_FONT_MONO,
    HUD_VALUE_TEXT_SCALE,
    HUD_LABEL_TEXT_SCALE,
    RuntimeSettings,
    GameState
)
from ui.crosshair import Crosshair
from ui.damage_indicator import DamageIndicator


class HUD(Entity):
    """Doom-style HUD with status bar at bottom."""

    def __init__(self, player, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)
        self.player = player
        self.ui_scale = RuntimeSettings.ui_scale()

        bar_y = -0.42  # Bottom of screen

        # Main status bar
        self.status_bar = Entity(
            parent=self,
            model='quad',
            color=color.brown,
            scale=(2, 0.14 * self.ui_scale),
            position=(0, bar_y),
            z=0.1
        )

        # Dark sections
        dark = color.dark_gray

        # AMMO section
        Entity(
            parent=self,
            model='quad',
            color=dark,
            scale=(0.26 * self.ui_scale, 0.11 * self.ui_scale),
            position=(-0.7, bar_y),
            z=0
        )

        # HEALTH section
        Entity(
            parent=self,
            model='quad',
            color=dark,
            scale=(0.30 * self.ui_scale, 0.11 * self.ui_scale),
            position=(-0.33, bar_y),
            z=0
        )

        # FACE section - show a simple face icon
        Entity(
            parent=self,
            model='quad',
            color=dark,
            scale=(0.13 * self.ui_scale, 0.11 * self.ui_scale),
            position=(0, bar_y),
            z=0
        )

        # Face image
        Entity(
            parent=self,
            model='quad',
            texture='assets/models/amir.png',
            scale=(0.09 * self.ui_scale, 0.09 * self.ui_scale),
            position=(0, bar_y),
            z=-0.1
        )

        # SCORE section
        Entity(
            parent=self,
            model='quad',
            color=dark,
            scale=(0.30 * self.ui_scale, 0.11 * self.ui_scale),
            position=(0.33, bar_y),
            z=0
        )

        # KILLS section
        Entity(
            parent=self,
            model='quad',
            color=dark,
            scale=(0.26 * self.ui_scale, 0.11 * self.ui_scale),
            position=(0.7, bar_y),
            z=0
        )

        # Text - red values (z=-1 to render in front of buttons)
        red = color.red
        gray = color.light_gray

        # AMMO
        self.ammo_text = Text(
            parent=self,
            text='50',
            position=(-0.75, bar_y + 0.015),
            origin=(0, 0),
            scale=HUD_VALUE_TEXT_SCALE * self.ui_scale,
            color=red,
            font=UI_FONT_MONO,
            z=-1
        )
        Text(
            parent=self,
            text='AMMO',
            position=(-0.75, bar_y - 0.03),
            origin=(0, 0),
            scale=HUD_LABEL_TEXT_SCALE * self.ui_scale,
            color=gray,
            font=UI_FONT_PRIMARY,
            z=-1
        )

        # HEALTH
        self.health_text = Text(
            parent=self,
            text='100%',
            position=(-0.38, bar_y + 0.015),
            origin=(0, 0),
            scale=HUD_VALUE_TEXT_SCALE * self.ui_scale,
            color=red,
            font=UI_FONT_MONO,
            z=-1
        )
        Text(
            parent=self,
            text='HEALTH',
            position=(-0.40, bar_y - 0.03),
            origin=(0, 0),
            scale=HUD_LABEL_TEXT_SCALE * self.ui_scale,
            color=gray,
            font=UI_FONT_PRIMARY,
            z=-1
        )

        # SCORE
        self.score_text = Text(
            parent=self,
            text='0',
            position=(0.28, bar_y + 0.015),
            origin=(0, 0),
            scale=HUD_VALUE_TEXT_SCALE * self.ui_scale,
            color=red,
            font=UI_FONT_MONO,
            z=-1
        )
        Text(
            parent=self,
            text='SCORE',
            position=(0.27, bar_y - 0.03),
            origin=(0, 0),
            scale=HUD_LABEL_TEXT_SCALE * self.ui_scale,
            color=gray,
            font=UI_FONT_PRIMARY,
            z=-1
        )

        # KILLS
        self.kills_text = Text(
            parent=self,
            text='0',
            position=(0.65, bar_y + 0.015),
            origin=(0, 0),
            scale=HUD_VALUE_TEXT_SCALE * self.ui_scale,
            color=red,
            font=UI_FONT_MONO,
            z=-1
        )
        Text(
            parent=self,
            text='KILLS',
            position=(0.64, bar_y - 0.03),
            origin=(0, 0),
            scale=HUD_LABEL_TEXT_SCALE * self.ui_scale,
            color=gray,
            font=UI_FONT_PRIMARY,
            z=-1
        )

        # Screen-space feedback
        self.crosshair = Crosshair(parent=self)
        self.crosshair.scale = self.ui_scale
        self.damage_indicator = DamageIndicator(parent=self)

        self.kills = 0
        self.event_timer = 0

        # Top HUD for wave/objective context.
        self.wave_text = Text(
            parent=self,
            text='WAVE 1/1',
            position=(-0.86, 0.46),
            origin=(0, 0),
            scale=0.85 * self.ui_scale,
            color=color.azure,
            font=UI_FONT_MONO,
            z=-1
        )
        self.objective_text = Text(
            parent=self,
            text='',
            position=(0, 0.46),
            origin=(0, 0),
            scale=0.78 * self.ui_scale,
            color=color.light_gray,
            font=UI_FONT_PRIMARY,
            z=-1
        )
        self.event_text = Text(
            parent=self,
            text='',
            position=(0, 0.38),
            origin=(0, 0),
            scale=0.85 * self.ui_scale,
            color=color.yellow,
            font=UI_FONT_PRIMARY,
            z=-1,
            enabled=False
        )

    def update(self):
        if not self.player:
            return

        health_pct = int(self.player.health_percentage * 100)
        self.health_text.text = f'{health_pct}%'

        weapon = self.player.current_weapon
        if weapon:
            self.ammo_text.text = f'{weapon.ammo_current}'

        import game_state
        if game_state.game:
            game = game_state.game
            self.score_text.text = f'{game.score}'
            self.kills = game.score // 10
            self.kills_text.text = f'{self.kills}'
            self.wave_text.text = f'WAVE {game.current_wave}/{game.max_waves}'

            if game.wave_in_progress:
                remaining = game.wave_enemies_remaining()
                self.objective_text.text = f'Enemies remaining: {remaining}'
            elif game.current_wave >= game.max_waves and game.state == GameState.VICTORY:
                self.objective_text.text = 'Objective complete'
            else:
                seconds = max(0, int(math.ceil(game.wave_break_timer)))
                self.objective_text.text = f'Next wave in {seconds}'

        self.damage_indicator.show_low_health_warning(self.player.health_percentage)

        if self.event_timer > 0:
            self.event_timer -= time.dt
            if self.event_timer <= 0:
                self.event_text.enabled = False

    def on_player_damaged(self, amount, source=None):
        self.health_text.color = color.rgb(255, 170, 170)
        self.damage_indicator.flash()
        invoke(self._reset_health_color, delay=0.12)

    def show_hit_marker(self):
        self.crosshair.show_hit()

    def show_event(self, message, duration=2.0):
        """Show a short event message near the top of the screen."""
        self.event_text.text = message
        self.event_text.enabled = True
        self.event_timer = duration

    def _reset_health_color(self):
        self.health_text.color = color.red

    def cleanup(self):
        destroy(self)
