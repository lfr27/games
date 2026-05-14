# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the game

```
python main.py
```

Requires Python and Pygame installed (`pip install pygame`).

## Architecture

The entire game lives in a single file: `main.py`. There are no modules, classes, or build steps.

**Game loop structure** (all in `main.py`):
- Constants and asset setup at the top (screen, colors, fonts, platforms, goal)
- `reset_game()` returns all mutable game state as a tuple — this is the only "state management"
- Main `while running` loop handles: events → input → physics → enemy AI → collision → drawing

**State variables** (returned from `reset_game`):
- `player`, `enemy` — `pygame.Rect` objects used for both position and collision
- `velocity_y`, `on_ground` — simple gravity/jump state
- `won`, `dead` — game phase flags that pause logic and show overlay screens
- `score`, `score_timer` — time-based scoring (1 pt/sec) plus goal bonus (+100)

**Physics**: gravity accumulates into `velocity_y` each frame; platform collision snaps `player.bottom` to `platform.top` when falling, `player.top` to `platform.bottom` when rising.

**Enemy**: patrols between x=200 and x=500 on the floor by reversing `enemy_speed`.

## Controls

| Key | Action |
|-----|--------|
| Arrow Left / Right | Move |
| Space | Jump (only when `on_ground`) |
| R | Restart after win or death |
