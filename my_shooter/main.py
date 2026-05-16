import pygame
import random
import math
import os
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def score_file_path():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(os.path.dirname(sys.executable), "highscore.txt")
    return os.path.join(os.path.abspath("."), "highscore.txt")

def load_high_score():
    try:
        with open(score_file_path(), "r") as f:
            return int(f.read().strip())
    except Exception:
        return 0

def save_high_score(score):
    try:
        with open(score_file_path(), "w") as f:
            f.write(str(score))
    except Exception:
        pass

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load(resource_path("assets/music.wav"))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

shoot_sound     = pygame.mixer.Sound(resource_path("assets/shoot.wav"))
explosion_sound = pygame.mixer.Sound(resource_path("assets/explosion.wav"))
shoot_sound.set_volume(0.3)
explosion_sound.set_volume(0.5)

SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter")
canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
YELLOW = (255, 210, 0)
RED    = (255, 100, 0)
GREEN  = (50,  200, 50)
CYAN   = (0,   200, 255)
GRAY   = (150, 150, 150)
ORANGE = (255, 140, 0)

font       = pygame.font.SysFont(None, 60)
font_small = pygame.font.SysFont(None, 35)
font_tiny  = pygame.font.SysFont(None, 26)

player_img_src = pygame.image.load(resource_path("assets/player.png")).convert_alpha()
enemy_img_src  = pygame.image.load(resource_path("assets/enemy.png")).convert_alpha()
bg_img         = pygame.image.load(resource_path("assets/background.png")).convert()

bg_img      = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT * 2))
player_img  = pygame.transform.scale(player_img_src, (50, 50))
player_life = pygame.transform.scale(player_img_src, (30, 30))

def load_enemy_img(filename, fallback, size):
    path = resource_path(f"assets/{filename}")
    src  = pygame.image.load(path).convert_alpha() if os.path.exists(path) else fallback
    return pygame.transform.scale(src, size)

enemy_imgs = {
    "normal": load_enemy_img("enemy.png",       enemy_img_src, (80,  40)),
    "fast":   load_enemy_img("enemy_fast.png",  enemy_img_src, (50,  25)),
    "tough":  load_enemy_img("enemy_tough.png", enemy_img_src, (100, 50)),
    "boss":   load_enemy_img("enemy_boss.png",  enemy_img_src, (180, 70)),
}

ENEMY_CONFIG = {
    "normal": dict(w=80,  h=40,  hp=1,  spd=1.0, pts=10),
    "fast":   dict(w=50,  h=25,  hp=1,  spd=1.6, pts=15),
    "tough":  dict(w=100, h=50,  hp=3,  spd=0.6, pts=30),
    "boss":   dict(w=180, h=70,  hp=20, spd=0.0, pts=150),
}

WAVE_TYPES = {
    1: [("normal", 1.00)],
    2: [("normal", 0.65), ("fast",  0.35)],
    3: [("normal", 0.40), ("fast",  0.35), ("tough", 0.25)],
    4: [("normal", 0.20), ("fast",  0.35), ("tough", 0.45)],
    5: [("normal", 0.20), ("fast",  0.55), ("tough", 0.25)],
    6: [("normal", 0.10), ("fast",  0.55), ("tough", 0.35)],
    7: [("fast",   0.50), ("tough", 0.50)],
    8: [("fast",   0.40), ("tough", 0.60)],
}

bg_y         = 0
scroll_speed = 4
explosions   = []

INVINCIBILITY_DURATION = 120
POWERUP_DURATION       = 600   # 10 seconds
SHIELD_DURATION        = 420   # 7 seconds
SHAKE_DURATION         = 18
SHAKE_MAGNITUDE        = 7

MAX_LEVEL        = 8
SURVIVE_FRAMES   = 45 * 60   # 2700 frames = 45 seconds
SURVIVE_BONUS    = 50
BOSS_CLEAR_BONUS = 200
WORM_SIZE        = 6          # enemies per worm formation
WORM_INTERVAL    = 1200       # frames between worms (~20 s)

LEVEL_TINTS = [
    (  0,   0,   0,   0),   # level 1: no tint
    (  0,  60, 180,  90),   # level 2: deep blue
    (120,   0, 180,  90),   # level 3: purple
    (180,  70,   0,  90),   # level 4: amber
    (  0, 160,  80,  90),   # level 5: green
    (180,   0,   0, 100),   # level 6: red
    ( 90,   0, 160, 100),   # level 7: violet
    (  0, 130, 130, 100),   # level 8: teal
]

high_score = load_high_score()

# ------------------------------------------------------------------ factories
def make_enemy(etype, wave_speed_base, vx=0):
    cfg = ENEMY_CONFIG[etype]
    x   = random.randint(0, max(0, SCREEN_WIDTH - cfg["w"]))
    if etype == "tough" and vx == 0:
        vx = random.choice([-1, 1]) * (1.0 + wave_speed_base * 0.25)
    return {
        "rect":     pygame.Rect(x, -cfg["h"], cfg["w"], cfg["h"]),
        "hp":       cfg["hp"],
        "max_hp":   cfg["hp"],
        "type":     etype,
        "speed":    wave_speed_base * cfg["spd"],
        "vx":       vx,
        "flash":    0,
        "dir":      1,
        "shoot_cd": 60,
    }

BOSS_PATTERNS = {
    1: "sweep", 2: "sweep", 3: "sine", 4: "dive",
    5: "aimed", 6: "figure8", 7: "teleport", 8: "rage",
}

def make_boss(level):
    cfg          = ENEMY_CONFIG["boss"]
    x            = SCREEN_WIDTH // 2 - cfg["w"] // 2
    hp           = min(15 + (level - 1) * 8, 60)
    speed        = min(2.0 + (level - 1) * 0.3, 5.0)
    shoot_cd_max = max(35, 80 - (level - 1) * 5)
    return {
        "rect":         pygame.Rect(x, -cfg["h"], cfg["w"], cfg["h"]),
        "hp":           hp,
        "max_hp":       hp,
        "type":         "boss",
        "speed":        speed,
        "flash":        0,
        "dir":          1,
        "shoot_cd":     shoot_cd_max,
        "shoot_cd_max": shoot_cd_max,
        "pattern":      BOSS_PATTERNS.get(level, "rage"),
        "t":            0.0,    # oscillation time counter
        "dive_state":   "sweep",
        "dive_cd":      150,
        "dive_tx":      0,
        "dive_ty":      0,
        "teleport_cd":  90,
    }

def make_bullet(x, y, vx, vy):
    return {"rect": pygame.Rect(x, y, 8, 16), "vx": vx, "vy": vy}

# ------------------------------------------------------------------ reset
def reset_game():
    return {
        "player":        pygame.Rect(375, 500, 50, 50),
        "bullets":       [],
        "enemies":       [],
        "enemy_bullets": [],
        "powerups":      [],
        "score":         0,
        "lives":         3,
        "level":         1,
        "phase":         "survive",
        "level_timer":   SURVIVE_FRAMES,
        "spawn_timer":   0,
        "game_over":     False,
        "won":           False,
        "inv_timer":          0,
        "spread_timer":       0,
        "shield_timer":       0,
        "boss_spawned":       False,
        "extra_life_drops":   0,
        "worm_timer":         WORM_INTERVAL,
        "level_flash":        0,
    }

g = reset_game()

player_speed = 5
bullet_speed = 8
bullet_ready = True
shake_timer  = 0
started      = False
paused       = False
new_record   = False

clock = pygame.time.Clock()
FPS   = 60

running = True
while running:

    # ---------------------------------------------------------------- events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if not started:
                started = True
            elif event.key == pygame.K_p and not g["game_over"] and not g["won"]:
                paused = not paused
            elif event.key == pygame.K_r and (g["game_over"] or g["won"]):
                g           = reset_game()
                explosions.clear()
                shake_timer = 0
                paused      = False
                new_record  = False

    # --------------------------------------------------------- title screen
    if not started:
        canvas.blit(bg_img, (0, bg_y - SCREEN_HEIGHT))
        canvas.blit(bg_img, (0, bg_y))

        title = font.render("SPACE SHOOTER", True, YELLOW)
        canvas.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        if high_score > 0:
            hs = font_small.render(f"Best: {high_score}", True, YELLOW)
            canvas.blit(hs, (SCREEN_WIDTH // 2 - hs.get_width() // 2, 218))

        lines = [
            "Arrow keys — move          Space — shoot",
            "P — pause                  R — restart",
            "",
            "Cyan power-up:   spread shot (5s)",
            "Orange power-up: shield (4s, blocks all hits)",
            "Green power-up:  extra life",
            "",
            f"Survive each wave, then beat the BOSS! ({MAX_LEVEL} levels)",
        ]
        for i, line in enumerate(lines):
            surf = font_tiny.render(line, True, GRAY)
            canvas.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, 268 + i * 26))

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            prompt = font_small.render("Press any key to start", True, WHITE)
            canvas.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 490))

        screen.blit(canvas, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)
        bg_y = (bg_y + scroll_speed) % SCREEN_HEIGHT
        continue

    # --------------------------------------------------------- game logic
    if not paused and not g["game_over"] and not g["won"]:

        wave_spd_base      = 1 + (g["level"] * 0.5)
        spawn_delay        = max(20, 60 - (g["level"] * 8))
        enemy_shoot_chance = 0.002 + g["level"] * 0.001

        # Input
        keys = pygame.key.get_pressed()
        p = g["player"]
        if keys[pygame.K_LEFT]  and p.left   > 0:            p.x -= player_speed
        if keys[pygame.K_RIGHT] and p.right  < SCREEN_WIDTH:  p.x += player_speed
        if keys[pygame.K_UP]    and p.top    > 0:             p.y -= player_speed
        if keys[pygame.K_DOWN]  and p.bottom < SCREEN_HEIGHT: p.y += player_speed

        if keys[pygame.K_SPACE] and bullet_ready:
            g["bullets"].append(pygame.Rect(p.centerx - 5, p.top, 10, 20))
            if g["spread_timer"] > 0:
                g["bullets"].append(pygame.Rect(p.centerx - 20, p.top + 10, 10, 20))
                g["bullets"].append(pygame.Rect(p.centerx + 10, p.top + 10, 10, 20))
            bullet_ready = False
            shoot_sound.play()
        if not keys[pygame.K_SPACE]:
            bullet_ready = True

        # Timers
        if g["spread_timer"] > 0: g["spread_timer"] -= 1
        if g["shield_timer"] > 0: g["shield_timer"] -= 1
        if g["inv_timer"]    > 0: g["inv_timer"]    -= 1
        if g["level_flash"]  > 0: g["level_flash"]  -= 1
        if shake_timer       > 0: shake_timer        -= 1

        # Player bullets
        for bullet in g["bullets"][:]:
            bullet.y -= bullet_speed
            if bullet.bottom < 0:
                g["bullets"].remove(bullet)

        # Spawn — phase-aware
        if g["phase"] == "survive":
            g["level_timer"] -= 1
            g["spawn_timer"] += 1
            if g["spawn_timer"] >= spawn_delay:
                g["spawn_timer"] = 0
                lvl_key = min(g["level"], 8)
                types, weights = zip(*WAVE_TYPES[lvl_key])
                etype = random.choices(types, weights=weights)[0]
                g["enemies"].append(make_enemy(etype, wave_spd_base))

            # Worm formation (level 3+): diagonal chain of fast enemies
            if g["level"] >= 3:
                g["worm_timer"] -= 1
                if g["worm_timer"] <= 0:
                    g["worm_timer"] = WORM_INTERVAL
                    direction = random.choice([-1, 1])
                    cfg       = ENEMY_CONFIG["fast"]
                    step      = 38   # px between worm segments
                    start_x   = random.randint(100, SCREEN_WIDTH - 100)
                    for i in range(WORM_SIZE):
                        x = max(0, min(SCREEN_WIDTH - cfg["w"],
                                       start_x + direction * step * i))
                        y = -cfg["h"] - step * i
                        g["enemies"].append(make_enemy("fast", wave_spd_base, vx=0))
                        g["enemies"][-1]["rect"].x = x
                        g["enemies"][-1]["rect"].y = y

            if g["level_timer"] <= 0:
                g["score"]       += SURVIVE_BONUS
                g["phase"]        = "boss"
                g["boss_spawned"] = False
        elif g["phase"] == "boss" and not g["boss_spawned"]:
            g["enemies"].append(make_boss(g["level"]))
            g["boss_spawned"] = True

        # Move enemies
        for enemy in g["enemies"][:]:
            r = enemy["rect"]
            if enemy["type"] == "boss":
                pat = enemy["pattern"]

                # Rage boss: pick sub-pattern from HP thresholds
                if pat == "rage":
                    hp_pct = enemy["hp"] / enemy["max_hp"]
                    eff = "sweep" if hp_pct > 0.66 else ("sine" if hp_pct > 0.33 else "dive")
                else:
                    eff = pat

                # Entry from top — don't tick t until fully on screen
                entering = r.top < 80
                if entering:
                    r.y += 3
                else:
                    enemy["t"] += 0.03
                    t = enemy["t"]
                    if eff == "sweep":
                        r.x += enemy["speed"] * enemy["dir"]
                        if r.right >= SCREEN_WIDTH or r.left <= 0:
                            enemy["dir"] *= -1

                    elif eff == "sine":
                        r.x += enemy["speed"] * enemy["dir"]
                        if r.right >= SCREEN_WIDTH or r.left <= 0:
                            enemy["dir"] *= -1
                        r.y = int(90 + 70 * math.sin(t * 1.5))

                    elif eff == "aimed":
                        r.x += enemy["speed"] * enemy["dir"]
                        if r.right >= SCREEN_WIDTH or r.left <= 0:
                            enemy["dir"] *= -1

                    elif eff == "figure8":
                        amp_x = SCREEN_WIDTH // 2 - r.w // 2 - 30
                        r.x   = int(SCREEN_WIDTH // 2 - r.w // 2 + amp_x * math.sin(t))
                        r.y   = int(100 + 80 * math.sin(2 * t))

                    elif eff == "teleport":
                        r.x += enemy["speed"] * 0.5 * enemy["dir"]
                        if r.right >= SCREEN_WIDTH or r.left <= 0:
                            enemy["dir"] *= -1
                        enemy["teleport_cd"] -= 1
                        if enemy["teleport_cd"] <= 0:
                            enemy["teleport_cd"] = 90
                            r.x = random.randint(20, SCREEN_WIDTH - r.w - 20)
                            r.y = random.randint(40, 200)

                    elif eff == "dive":
                        if enemy["dive_state"] == "sweep":
                            r.x += enemy["speed"] * enemy["dir"]
                            if r.right >= SCREEN_WIDTH or r.left <= 0:
                                enemy["dir"] *= -1
                            enemy["dive_cd"] -= 1
                            if enemy["dive_cd"] <= 0:
                                enemy["dive_cd"] = 150
                                enemy["dive_state"] = "dive"
                                enemy["dive_tx"] = max(0, min(SCREEN_WIDTH - r.w,
                                                              p.centerx - r.w // 2))
                                enemy["dive_ty"] = min(p.centery - 40, SCREEN_HEIGHT - 150)
                        elif enemy["dive_state"] == "dive":
                            dx   = enemy["dive_tx"] - r.x
                            dy   = enemy["dive_ty"] - r.y
                            dist = max(1, math.hypot(dx, dy))
                            spd  = enemy["speed"] * 2.5
                            r.x += int(dx / dist * spd)
                            r.y += int(dy / dist * spd)
                            if dist < spd + 4:
                                enemy["dive_state"] = "retreat"
                        elif enemy["dive_state"] == "retreat":
                            r.y -= 4
                            if r.y <= 80:
                                r.y = 80
                                enemy["dive_state"] = "sweep"

                # Shooting
                enemy["shoot_cd"] -= 1
                if enemy["shoot_cd"] <= 0:
                    enemy["shoot_cd"] = enemy["shoot_cd_max"]

                    # Aimed patterns: fire toward player
                    use_aimed = eff in ("aimed", "teleport")
                    if pat == "rage":
                        hp_pct    = enemy["hp"] / enemy["max_hp"]
                        use_aimed = hp_pct <= 0.66
                        n_bullets = 5 if hp_pct <= 0.33 else 3
                    else:
                        n_bullets = 3

                    if use_aimed:
                        dx   = p.centerx - r.centerx
                        dy   = p.centery  - r.centery
                        dist = max(1, math.hypot(dx, dy))
                        spd  = 6
                        base = math.atan2(dy, dx)
                        spread = math.radians(15)
                        offsets = [spread * (i - (n_bullets - 1) / 2)
                                   for i in range(n_bullets)]
                        for off in offsets:
                            ang = base + off
                            g["enemy_bullets"].append(make_bullet(
                                r.centerx - 4, r.bottom,
                                math.cos(ang) * spd, math.sin(ang) * spd))
                    else:
                        for vx in (-2, 0, 2):
                            g["enemy_bullets"].append(
                                make_bullet(r.centerx - 4, r.bottom, vx, 5))
            else:
                r.y += enemy["speed"]
                if enemy["vx"] != 0:
                    r.x += enemy["vx"]
                    if r.left <= 0:
                        r.left = 0
                        enemy["vx"] = abs(enemy["vx"])
                    elif r.right >= SCREEN_WIDTH:
                        r.right = SCREEN_WIDTH
                        enemy["vx"] = -abs(enemy["vx"])
                if r.top > SCREEN_HEIGHT:
                    g["enemies"].remove(enemy)
                    continue
                if random.random() < enemy_shoot_chance:
                    g["enemy_bullets"].append(make_bullet(r.centerx - 4, r.bottom, 0, 6))

            if enemy["flash"] > 0:
                enemy["flash"] -= 1

        # Move enemy bullets
        for eb in g["enemy_bullets"][:]:
            eb["rect"].x += eb["vx"]
            eb["rect"].y += eb["vy"]
            r = eb["rect"]
            if r.top > SCREEN_HEIGHT or r.right < 0 or r.left > SCREEN_WIDTH:
                g["enemy_bullets"].remove(eb)

        # Player bullets vs enemies
        for enemy in g["enemies"][:]:
            hit = False
            for bullet in g["bullets"][:]:
                if enemy["rect"].colliderect(bullet):
                    enemy["hp"]   -= 1
                    enemy["flash"] = 8
                    g["bullets"].remove(bullet)
                    hit = True
                    break
            if hit and enemy["hp"] <= 0:
                cx, cy = enemy["rect"].center
                explosions.append([cx, cy, 5, 40])
                explosion_sound.play()
                g["enemies"].remove(enemy)
                g["score"] += ENEMY_CONFIG[enemy["type"]]["pts"]

                if enemy["type"] == "boss":
                    g["score"] += BOSS_CLEAR_BONUS
                    if g["level"] >= MAX_LEVEL:
                        g["won"] = True
                    else:
                        g["level"]       += 1
                        g["phase"]        = "survive"
                        g["level_timer"]  = SURVIVE_FRAMES
                        g["boss_spawned"] = False
                        g["worm_timer"]   = WORM_INTERVAL
                        g["level_flash"]  = 180  # 3-second flash
                else:
                    roll = random.random()
                    if enemy["type"] == "tough":
                        if roll < 0.08:
                            ptype = "life"
                        elif roll < 0.22: ptype = "shield"
                        elif roll < 0.40: ptype = "spread"
                        else:             ptype = None
                    else:
                        ptype = "spread" if roll < 0.15 else None
                    # Only drop if no token of that type is already on screen
                    if ptype and not any(pw["type"] == ptype for pw in g["powerups"]):
                        if ptype == "life":
                            g["extra_life_drops"] += 1
                        g["powerups"].append({
                            "rect": pygame.Rect(cx - 10, cy - 10, 20, 20),
                            "type": ptype,
                        })

        # Enemy collisions with player
        if g["inv_timer"] == 0:
            for enemy in g["enemies"][:]:
                if enemy["type"] != "boss" and p.colliderect(enemy["rect"].inflate(-10, -10)):
                    explosions.append([enemy["rect"].centerx, enemy["rect"].centery, 5, 40])
                    explosion_sound.play()
                    g["enemies"].remove(enemy)
                    if g["shield_timer"] > 0:
                        pass   # shield absorbs the hit, keeps running
                    else:
                        g["lives"]    -= 1
                        g["inv_timer"] = INVINCIBILITY_DURATION
                        shake_timer    = SHAKE_DURATION
                        if g["lives"] <= 0:
                            g["game_over"] = True

            for eb in g["enemy_bullets"][:]:
                if p.colliderect(eb["rect"]):
                    g["enemy_bullets"].remove(eb)
                    if g["shield_timer"] > 0:
                        pass   # shield absorbs the hit, keeps running
                    else:
                        g["lives"]    -= 1
                        g["inv_timer"] = INVINCIBILITY_DURATION
                        shake_timer    = SHAKE_DURATION
                        if g["lives"] <= 0:
                            g["game_over"] = True

        # Power-ups
        for pw in g["powerups"][:]:
            pw["rect"].y += 2
            if pw["rect"].top > SCREEN_HEIGHT:
                g["powerups"].remove(pw)
            elif p.colliderect(pw["rect"]):
                g["powerups"].remove(pw)
                if pw["type"] == "spread":
                    g["spread_timer"] = POWERUP_DURATION
                elif pw["type"] == "shield":
                    g["shield_timer"] = SHIELD_DURATION
                elif pw["type"] == "life":
                    g["lives"] += 1

        # Explosions
        for exp in explosions[:]:
            exp[2] += 3
            if exp[2] >= exp[3]:
                explosions.remove(exp)

        # High score
        if (g["game_over"] or g["won"]) and g["score"] > high_score:
            high_score = g["score"]
            save_high_score(high_score)
            new_record = True

    # ----------------------------------------------------------------- draw
    bg_y = (bg_y + scroll_speed) % SCREEN_HEIGHT
    canvas.blit(bg_img, (0, bg_y - SCREEN_HEIGHT))
    canvas.blit(bg_img, (0, bg_y))

    # Level tint overlay
    tint = LEVEL_TINTS[(g["level"] - 1) % len(LEVEL_TINTS)]
    if tint[3] > 0:
        tint_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        tint_surf.fill(tint)
        canvas.blit(tint_surf, (0, 0))

    for exp in explosions:
        progress = exp[2] / exp[3]
        color    = (255, int(120 + 80 * (1 - progress)), 0)
        pygame.draw.circle(canvas, color, (exp[0], exp[1]), exp[2])
        pygame.draw.circle(canvas, WHITE, (exp[0], exp[1]), exp[2] // 3)

    for pw in g["powerups"]:
        cx, cy = pw["rect"].center
        if pw["type"] == "spread":
            pygame.draw.rect(canvas, CYAN, pw["rect"], border_radius=4)
            canvas.blit(font_small.render("3x", True, BLACK), (pw["rect"].x - 2, pw["rect"].y - 1))
        elif pw["type"] == "shield":
            pygame.draw.circle(canvas, ORANGE, (cx, cy), 12)
            pygame.draw.circle(canvas, WHITE,  (cx, cy), 12, 2)
            canvas.blit(font_tiny.render("SH", True, BLACK), (pw["rect"].x - 1, pw["rect"].y + 3))
        elif pw["type"] == "life":
            pygame.draw.circle(canvas, GREEN, (cx, cy), 12)
            pygame.draw.circle(canvas, WHITE, (cx, cy), 12, 2)
            canvas.blit(font_tiny.render("1UP", True, BLACK), (pw["rect"].x - 4, pw["rect"].y + 3))

    for bullet in g["bullets"]:
        pygame.draw.circle(canvas, WHITE, bullet.center, 4)
    for eb in g["enemy_bullets"]:
        pygame.draw.ellipse(canvas, RED, eb["rect"])

    for enemy in g["enemies"]:
        canvas.blit(enemy_imgs[enemy["type"]], enemy["rect"])
        if enemy["flash"] > 0:
            fade = enemy["flash"] / 8  # 1.0 → 0.0 as it expires
            if enemy["type"] in ("tough", "boss"):
                ring_col = CYAN if enemy["type"] == "tough" else (255, 80, 0)
                for inflate_px, width, a_mult in [(12, 3, 1.0), (24, 2, 0.35)]:
                    r = enemy["rect"].inflate(inflate_px, inflate_px)
                    s = pygame.Surface((r.w + 6, r.h + 6), pygame.SRCALPHA)
                    pygame.draw.ellipse(s, (*ring_col, int(255 * fade * a_mult)),
                                        pygame.Rect(3, 3, r.w, r.h), width)
                    canvas.blit(s, (r.x - 3, r.y - 3))
            else:
                fs = pygame.Surface(enemy["rect"].size, pygame.SRCALPHA)
                fs.fill((255, 255, 255, int(160 * fade)))
                canvas.blit(fs, enemy["rect"])
        if enemy["type"] == "boss":
            bx, by = enemy["rect"].x, enemy["rect"].bottom + 4
            bw     = enemy["rect"].w
            hp_w   = int(bw * enemy["hp"] / enemy["max_hp"])
            pygame.draw.rect(canvas, GRAY,  (bx, by, bw, 10))
            pygame.draw.rect(canvas, RED,   (bx, by, hp_w, 10))
            pygame.draw.rect(canvas, WHITE, (bx, by, bw, 10), 1)
            label = font_tiny.render("BOSS", True, RED)
            canvas.blit(label, (bx + bw // 2 - label.get_width() // 2, by + 12))

    p = g["player"]
    if g["inv_timer"] == 0 or (g["inv_timer"] // 8) % 2 == 0:
        canvas.blit(player_img, p)
    if g["shield_timer"] > 0:
        fade  = g["shield_timer"] / SHIELD_DURATION
        alpha = int(80 + 175 * fade)
        sh_s  = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(sh_s, (*ORANGE, alpha),        (40, 40), 36, 3)
        pygame.draw.circle(sh_s, (*ORANGE, alpha // 3),   (40, 40), 30, 1)
        canvas.blit(sh_s, (p.centerx - 40, p.centery - 40))

    # Power-up status bars
    hud_y = 40
    if g["spread_timer"] > 0:
        bar_w = int((g["spread_timer"] / POWERUP_DURATION) * 120)
        pygame.draw.rect(canvas, CYAN, (10, hud_y, bar_w, 8))
        canvas.blit(font_small.render("SPREAD", True, CYAN), (10, hud_y + 10))
        hud_y += 36
    if g["shield_timer"] > 0:
        bar_w = int((g["shield_timer"] / SHIELD_DURATION) * 120)
        pygame.draw.rect(canvas, ORANGE, (10, hud_y, bar_w, 8))
        canvas.blit(font_small.render("SHIELD", True, ORANGE), (10, hud_y + 10))
        hud_y += 36

    # Level transition flash
    if g["level_flash"] > 0:
        alpha   = min(255, g["level_flash"] * 3)
        fl_surf = pygame.Surface((SCREEN_WIDTH, 80), pygame.SRCALPHA)
        fl_surf.fill((0, 0, 0, min(180, alpha)))
        canvas.blit(fl_surf, (0, SCREEN_HEIGHT // 2 - 40))
        lv_text = font.render(f"LEVEL {g['level']}", True, YELLOW)
        lv_text.set_alpha(alpha)
        canvas.blit(lv_text, (SCREEN_WIDTH // 2 - lv_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))

    # HUD — countdown during survive, BOSS alert during boss phase
    if g["phase"] == "survive":
        secs     = max(0, g["level_timer"] // 60)
        hud_col  = YELLOW if secs <= 5 else WHITE
        hud_text = f"Score: {g['score']}   Level: {g['level']}/{MAX_LEVEL}   {secs}s"
    else:
        hud_col  = RED
        hud_text = f"Score: {g['score']}   Level: {g['level']}/{MAX_LEVEL}   BOSS!"
    canvas.blit(font_small.render(hud_text, True, hud_col), (10, 10))

    # Timer bar (survive phase only)
    if g["phase"] == "survive":
        bar_w = int((g["level_timer"] / SURVIVE_FRAMES) * 200)
        pygame.draw.rect(canvas, GRAY, (10, 30, 200, 5))
        pygame.draw.rect(canvas, CYAN, (10, 30, bar_w, 5))

    hs_surf = font_small.render(f"Best: {high_score}", True, YELLOW)
    canvas.blit(hs_surf, (SCREEN_WIDTH // 2 - hs_surf.get_width() // 2, 10))
    for i in range(g["lives"]):
        canvas.blit(player_life, (SCREEN_WIDTH - 40 - (i * 35), 5))

    if g["game_over"]:
        canvas.blit(font.render("GAME OVER :(", True, RED), (220, 200))
        canvas.blit(font_small.render(f"Score: {g['score']}   Best: {high_score}", True, WHITE), (230, 275))
        if new_record and (pygame.time.get_ticks() // 400) % 2 == 0:
            rec = font_small.render("NEW RECORD!", True, YELLOW)
            canvas.blit(rec, (SCREEN_WIDTH // 2 - rec.get_width() // 2, 315))
        canvas.blit(font_small.render("Press R to restart", True, GRAY), (300, 355))

    if g["won"]:
        canvas.blit(font.render("YOU WIN! :)", True, YELLOW), (230, 200))
        canvas.blit(font_small.render(f"Score: {g['score']}   Best: {high_score}", True, WHITE), (230, 275))
        if new_record and (pygame.time.get_ticks() // 400) % 2 == 0:
            rec = font_small.render("NEW RECORD!", True, YELLOW)
            canvas.blit(rec, (SCREEN_WIDTH // 2 - rec.get_width() // 2, 315))
        canvas.blit(font_small.render("Press R to restart", True, GRAY), (300, 355))

    if paused:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        canvas.blit(overlay, (0, 0))
        canvas.blit(font.render("PAUSED", True, WHITE),
                    (SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 - 30))
        canvas.blit(font_small.render("Press P to resume", True, GRAY),
                    (SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 40))

    if shake_timer > 0:
        ox = random.randint(-SHAKE_MAGNITUDE, SHAKE_MAGNITUDE)
        oy = random.randint(-SHAKE_MAGNITUDE, SHAKE_MAGNITUDE)
        screen.fill(BLACK)
    else:
        ox, oy = 0, 0
    screen.blit(canvas, (ox, oy))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
