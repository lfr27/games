# Space Shooter

A Python/pygame space shooter built as a learning project.

## Run & Build

```
python main.py
pyinstaller build.bat   # builds dist/main.exe
```

## Controls

| Key | Action |
|-----|--------|
| Arrow keys | Move |
| Space | Shoot |
| P | Pause |
| R | Restart after game over |

---

## Game Structure

- **8 levels**, each with two phases:
  1. **Survive** — endure a timed enemy wave (default 45 s)
  2. **Boss** — kill the boss to advance
- Lives lost only by being hit (enemies passing the bottom are harmless)
- Score accumulates across all levels; best score saved to `highscore.txt`

---

## Enemy Types

| Type | Size | HP | Speed | Points | Notes |
|------|------|----|-------|--------|-------|
| Normal | 80×40 | 1 | 1× | 10 | Straight down |
| Fast | 50×25 | 1 | 1.6× | 15 | Straight down |
| Tough | 100×50 | 3 | 0.6× | 30 | Moves diagonally, bounces off walls |
| Boss | 180×70 | scales | scales | 150 + 200 bonus | Unique pattern per level |

**Worm formations** — from level 3 onwards, every ~20 s a diagonal chain of 6 fast enemies sweeps across the screen.

### Spawn mix per level

| Level | Normal | Fast | Tough |
|-------|--------|------|-------|
| 1 | 100% | — | — |
| 2 | 65% | 35% | — |
| 3 | 40% | 35% | 25% |
| 4 | 20% | 35% | 45% |
| 5 | 20% | 55% | 25% |
| 6 | 10% | 55% | 35% |
| 7 | — | 50% | 50% |
| 8 | — | 40% | 60% |

---

## Boss Patterns

| Level | Pattern | Movement | Shooting |
|-------|---------|----------|----------|
| 1 | **Sweep** | Side-to-side at fixed height | 3-bullet fixed spread |
| 2 | **Sweep** | Same, but faster | 3-bullet fixed spread |
| 3 | **Sine** | Sweeps horizontally while rising and falling in a sine wave | 3-bullet fixed spread |
| 4 | **Dive** | Sweeps, then locks onto player position and charges; retreats back up | 3-bullet fixed spread |
| 5 | **Aimed** | Simple horizontal sweep | 3 bullets fired directly at player |
| 6 | **Figure-8** | Traces a figure-8 across the full screen width | 3-bullet fixed spread |
| 7 | **Teleport** | Slow horizontal drift; jumps to a random position every 1.5 s | 3 aimed bullets |
| 8 | **Rage** | Changes pattern as HP drops: Sweep → Sine → Dive | Fixed spread → 3 aimed → 5 aimed |

### Boss scaling per level

| Stat | Level 1 | Level 4 | Level 8 |
|------|---------|---------|---------|
| HP | 15 | 39 | 60 |
| Speed | 2.0 | 2.9 | 4.1 |
| Shoot cooldown | 80 frames | 65 frames | 45 frames |

---

## Power-ups

All drop from enemies randomly. Only one token of each type on screen at a time.

| Token | Color | Source | Effect |
|-------|-------|--------|--------|
| **3x** (Spread) | Cyan square | Normal / Fast / Tough | Triple shot for 10 s |
| **SH** (Shield) | Orange circle | Tough | Force field for 7 s — blocks all hits |
| **1UP** (Life) | Green circle | Tough | +1 life (unlimited per game) |

---

## Tuning Constants (`main.py`)

| Constant | Default | Purpose |
|----------|---------|---------|
| `SURVIVE_FRAMES` | `45 * 60` | Seconds per survive phase (`15 * 60` for testing) |
| `MAX_LEVEL` | `8` | Number of levels |
| `POWERUP_DURATION` | `600` | Spread shot duration (frames) |
| `SHIELD_DURATION` | `420` | Shield duration (frames) |
| `WORM_INTERVAL` | `1200` | Frames between worm formations |
| `WORM_SIZE` | `6` | Enemies per worm |
| `BOSS_CLEAR_BONUS` | `200` | Score bonus for killing boss |
| `SURVIVE_BONUS` | `50` | Score bonus for surviving the wave |

---

## Asset Files

| File | Purpose |
|------|---------|
| `assets/player.png` | Player ship sprite |
| `assets/enemy.png` | Normal enemy sprite (also fallback for missing variants) |
| `assets/enemy_fast.png` | Fast enemy sprite (50×25 canvas) |
| `assets/enemy_tough.png` | Tough enemy sprite (100×50 canvas) |
| `assets/enemy_boss.png` | Boss sprite (180×70 canvas) |
| `assets/background.png` | Scrolling starfield |
| `assets/music.wav` | Background music (loops) |
| `assets/shoot.wav` | Player shoot sound |
| `assets/explosion.wav` | Explosion sound |
| `highscore.txt` | Auto-created; stores best score |
