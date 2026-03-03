# Balancing Notes

## Targets
- Time-to-kill for base zombie at wave 1 should feel quick with accurate shots.
- Demon should be high-threat melee pressure but not one-shot the player.
- Imp should force movement with telegraphed ranged attacks.

## Current baseline
- `zombie`: medium health, low speed, melee.
- `demon`: high health/damage, high speed, burst-chase behavior.
- `imp`: lower health, ranged projectile with windup.

## Wave scaling
- Enemy count scales with wave: `BASE_ENEMIES_PER_WAVE + (wave-1)*ENEMIES_PER_WAVE_STEP`.
- Spawn interval shrinks per wave until `MIN_SPAWN_INTERVAL`.
- Enemy stat multipliers per wave in code:
  - damage: `+8%` per wave
  - speed: `+4%` per wave
  - health: `+12%` per wave

## Economy and sustain
- Score rewards every `SCORE_REWARD_STEP` points:
  - heal: `SCORE_REWARD_HEAL`
  - ammo: `SCORE_REWARD_AMMO`
- Pickups spawn by cooldown with cap (`PICKUP_MAX_ACTIVE`) and need-aware selection.

## Tuning checklist
- If early waves are too easy:
  - increase `ENEMIES_PER_WAVE_STEP`
  - reduce `PICKUP_SPAWN_COOLDOWN`
- If late waves are unfair:
  - reduce health scaling multiplier in `main.py`
  - increase `WAVE_BREAK_DURATION`
  - lower demon/imp spawn chance thresholds
