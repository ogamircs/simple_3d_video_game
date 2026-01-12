"""
HUD (Heads-Up Display)
Doom-style status bar at the bottom of the screen.
"""
from ursina import Entity, Text, camera, color, Button


class HUD(Entity):
    """Doom-style HUD with status bar at bottom."""

    def __init__(self, player, **kwargs):
        super().__init__(**kwargs)
        self.player = player

        bar_y = -0.42  # Bottom of screen

        # Main status bar - brown background using Button (proven to work with colors)
        self.status_bar = Button(
            parent=camera.ui,
            model='quad',
            color=color.brown,
            scale=(2, 0.14),
            position=(0, bar_y),
            z=0.1,
            highlight_color=color.brown,
            pressed_color=color.brown
        )

        # Dark sections
        dark = color.dark_gray

        # AMMO section
        Button(
            parent=camera.ui,
            model='quad',
            color=dark,
            scale=(0.26, 0.11),
            position=(-0.7, bar_y),
            z=0,
            highlight_color=dark,
            pressed_color=dark
        )

        # HEALTH section
        Button(
            parent=camera.ui,
            model='quad',
            color=dark,
            scale=(0.30, 0.11),
            position=(-0.33, bar_y),
            z=0,
            highlight_color=dark,
            pressed_color=dark
        )

        # FACE section - show a simple face icon
        Button(
            parent=camera.ui,
            model='quad',
            color=dark,
            scale=(0.13, 0.11),
            position=(0, bar_y),
            z=0,
            highlight_color=dark,
            pressed_color=dark
        )

        # Face image
        Entity(
            parent=camera.ui,
            model='quad',
            texture='assets/models/amir.png',
            scale=(0.09, 0.09),
            position=(0, bar_y),
            z=-0.1
        )

        # SCORE section
        Button(
            parent=camera.ui,
            model='quad',
            color=dark,
            scale=(0.30, 0.11),
            position=(0.33, bar_y),
            z=0,
            highlight_color=dark,
            pressed_color=dark
        )

        # KILLS section
        Button(
            parent=camera.ui,
            model='quad',
            color=dark,
            scale=(0.26, 0.11),
            position=(0.7, bar_y),
            z=0,
            highlight_color=dark,
            pressed_color=dark
        )

        # Text - red values (z=-1 to render in front of buttons)
        red = color.red
        gray = color.light_gray

        # AMMO
        self.ammo_text = Text(text='50', position=(-0.75, bar_y+0.015), scale=2, color=red, z=-1)
        Text(text='AMMO', position=(-0.75, bar_y-0.03), scale=0.8, color=gray, z=-1)

        # HEALTH
        self.health_text = Text(text='100%', position=(-0.38, bar_y+0.015), scale=2, color=red, z=-1)
        Text(text='HEALTH', position=(-0.40, bar_y-0.03), scale=0.8, color=gray, z=-1)

        # SCORE
        self.score_text = Text(text='0', position=(0.28, bar_y+0.015), scale=2, color=red, z=-1)
        Text(text='SCORE', position=(0.27, bar_y-0.03), scale=0.8, color=gray, z=-1)

        # KILLS
        self.kills_text = Text(text='0', position=(0.65, bar_y+0.015), scale=2, color=red, z=-1)
        Text(text='KILLS', position=(0.64, bar_y-0.03), scale=0.8, color=gray, z=-1)

        # Crosshair
        Entity(parent=camera.ui, model='quad', color=color.white, scale=(0.002, 0.02), position=(0,0), z=-1)
        Entity(parent=camera.ui, model='quad', color=color.white, scale=(0.02, 0.002), position=(0,0), z=-1)

        self.kills = 0

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
            self.score_text.text = f'{game_state.game.score}'
            self.kills = game_state.game.score // 10
            self.kills_text.text = f'{self.kills}'

    def on_player_damaged(self, amount, source=None):
        pass

    def show_hit_marker(self):
        pass

    def cleanup(self):
        pass
