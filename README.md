# Doom-like FPS Game

A retro-style first-person shooter inspired by classic Doom, built with Python and the Ursina game engine.

## Features

- **Classic FPS Gameplay**: First-person shooter with WASD movement and mouse look
- **Doom-style HUD**: Status bar at the bottom showing AMMO, HEALTH, player face, SCORE, and KILLS
- **Shotgun with Recoil**: 3D shotgun model with realistic recoil animation
- **Enemy AI**: Zombies that chase and attack the player with state machine AI (IDLE, CHASE, ATTACK)
- **Combat System**: Hitscan shooting mechanics with hit effects
- **Enclosed Arena**: Walled level with pillars for cover

## Screenshots

The game features a Doom-style status bar HUD and first-person shotgun gameplay.

## Requirements

- Python 3.8+
- Ursina Engine

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/simple_3d_video_game.git
cd simple_3d_video_game
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Game

```bash
python main.py
```

## Controls

- **WASD**: Move
- **Mouse**: Look around
- **Left Click**: Shoot
- **ESC**: Pause/Menu

## Project Structure

```
simple_3d_video_game/
├── main.py              # Main entry point
├── config.py            # Game configuration
├── game_state.py        # Global game state
├── assets/
│   └── models/          # 3D models (shotgun, hand, zombie, etc.)
├── entities/
│   ├── player.py        # Player controller
│   ├── enemy.py         # Base enemy class
│   └── enemies/         # Enemy types (zombie)
├── weapons/
│   ├── base_weapon.py   # Base weapon class
│   └── pistol.py        # Shotgun weapon
├── ui/
│   ├── hud.py           # Doom-style HUD
│   └── menu.py          # Main menu
├── systems/
│   └── combat_system.py # Combat/damage system
└── world/               # Level/world generation
```

## License

MIT License
