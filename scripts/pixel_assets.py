"""Procedural pixel art + synthesized audio: replaces every image / sound asset.

Images are registered in IMAGES as 'folder/N.png' -> function returning a Surface
(pure black (0,0,0) is the transparent colorkey, so it is never used for art).
"""
import array
import math
import random

import pygame

TS = 16
IMAGES = {}


def _surf(w, h, fill=(0, 0, 0)):
  s = pygame.Surface((w, h))
  s.fill(fill)
  return s


def _add(folder, makers):
  for i, maker in enumerate(makers):
    IMAGES[folder + '/' + str(i) + '.png'] = maker


def listdir(folder):
  """Sorted file names of a procedural 'folder' (like os.listdir for the old assets)."""
  names = [k.rsplit('/', 1)[1] for k in IMAGES if k.rsplit('/', 1)[0] == folder]
  return sorted(names, key=lambda n: int(n.split('.')[0]))


# ---------------------------------------------------------------- tiles
# which sides have no neighbour, per autotile variant (matches AUTOTILE_MAP)
OPEN = {0: 'TL', 1: 'T', 2: 'TR', 3: 'R', 4: 'BR', 5: 'B', 6: 'BL', 7: 'L', 8: ''}
CORNER = {0: (0, 0), 2: (15, 0), 4: (15, 15), 6: (0, 15)}


def _tile(kind, v):
  o = OPEN[v]
  if kind == 'stone':
    base, dark, light = (104, 108, 128), (66, 70, 92), (148, 152, 174)
  else:
    base, dark, light = (122, 84, 54), (84, 56, 38), (158, 112, 74)
  s = _surf(TS, TS, base)
  rng = random.Random(v + (50 if kind == 'grass' else 0))
  for _ in range(14):
    s.set_at((rng.randrange(TS), rng.randrange(TS)), dark)

  if kind == 'stone':
    for y in (5, 11):
      pygame.draw.line(s, dark, (0, y), (15, y))
    for x, y0, y1 in ((8, 0, 4), (3, 6, 10), (12, 6, 10), (8, 12, 15)):
      pygame.draw.line(s, dark, (x, y0), (x, y1))

  if 'L' in o:
    pygame.draw.line(s, light, (0, 0), (0, 15))
  if 'R' in o:
    pygame.draw.line(s, dark, (15, 0), (15, 15))
  if 'B' in o:
    pygame.draw.line(s, dark, (0, 15), (15, 15))

  if 'T' in o:
    if kind == 'grass':
      green = (70, 168, 62)
      pygame.draw.rect(s, green, (0, 0, TS, 4))
      for x in range(TS):
        if rng.random() < 0.45:
          s.set_at((x, 4), green)
        if rng.random() < 0.15:
          s.set_at((x, 5), green)
      pygame.draw.line(s, (118, 206, 88), (0, 0), (15, 0))
    else:
      pygame.draw.line(s, light, (0, 0), (15, 0))

  if v in CORNER:  # round the outer corner
    s.set_at(CORNER[v], (0, 0, 0))
  return s


_add('tiles/grass', [lambda v=v: _tile('grass', v) for v in range(9)])
_add('tiles/stone', [lambda v=v: _tile('stone', v) for v in range(9)])


def _decor(v):
  s = _surf(16, 16)
  g, gd = (70, 168, 62), (40, 120, 50)
  if v == 0:    # tall grass
    for x, h in ((3, 6), (6, 9), (9, 7), (12, 5)):
      pygame.draw.rect(s, g, (x, 16 - h, 1, h))
      s.set_at((x, 16 - h), (118, 206, 88))
  elif v == 1:  # short grass
    for x, h in ((2, 3), (5, 4), (8, 3), (11, 5), (13, 3)):
      pygame.draw.rect(s, gd, (x, 16 - h, 1, h))
  elif v == 2:  # red flower
    pygame.draw.rect(s, gd, (7, 8, 1, 8))
    s.set_at((5, 12), g); s.set_at((6, 11), g); s.set_at((9, 11), g); s.set_at((10, 12), g)
    for p in ((6, 7), (8, 7), (7, 6), (7, 8)):
      s.set_at(p, (220, 60, 70))
    s.set_at((7, 7), (250, 220, 80))
  else:         # mushroom
    pygame.draw.rect(s, (230, 220, 200), (7, 11, 2, 5))
    pygame.draw.rect(s, (200, 50, 60), (5, 8, 6, 3))
    pygame.draw.rect(s, (200, 50, 60), (6, 7, 4, 1))
    s.set_at((6, 9), (255, 255, 255)); s.set_at((9, 8), (255, 255, 255))
  return s


_add('tiles/decor', [lambda v=v: _decor(v) for v in range(4)])


def _large_decor(v):
  if v == 0:    # bush
    s = _surf(32, 16)
    for c, r, col in (((9, 10), 7, (46, 140, 58)), ((20, 8), 8, (46, 140, 58)),
                      ((26, 11), 5, (46, 140, 58)), ((8, 8), 3, (80, 180, 80)),
                      ((19, 5), 3, (80, 180, 80))):
      pygame.draw.circle(s, col, c, r)
    pygame.draw.rect(s, (30, 100, 46), (2, 14, 28, 2))
  elif v == 1:  # rocks
    s = _surf(32, 16)
    pygame.draw.polygon(s, (120, 124, 140), [(2, 15), (6, 6), (14, 3), (20, 8), (22, 15)])
    pygame.draw.polygon(s, (96, 100, 118), [(18, 15), (22, 9), (28, 8), (31, 15)])
    pygame.draw.line(s, (160, 164, 182), (7, 7), (13, 4))
    pygame.draw.line(s, (130, 134, 152), (23, 10), (27, 9))
  else:         # tree (canopy on top = where leaves spawn, trunk below)
    s = _surf(32, 32)
    pygame.draw.rect(s, (110, 72, 44), (14, 16, 4, 16))
    pygame.draw.rect(s, (80, 50, 32), (16, 16, 2, 16))
    pygame.draw.rect(s, (110, 72, 44), (10, 20, 4, 1))
    for c, r, col in (((10, 12), 8, (36, 120, 52)), ((22, 12), 8, (36, 120, 52)),
                      ((16, 8), 8, (46, 140, 58)), ((13, 6), 4, (84, 188, 84)),
                      ((22, 10), 3, (70, 170, 70))):
      pygame.draw.circle(s, col, c, r)
    rng = random.Random(3)
    for _ in range(18):
      s.set_at((rng.randrange(4, 28), rng.randrange(2, 18)), (28, 96, 44))
  return s


_add('tiles/large_decor', [lambda v=v: _large_decor(v) for v in range(3)])


def _spawner(v):
  col = (60, 120, 255) if v == 0 else (255, 80, 80)
  s = _surf(TS, TS, (20, 20, 40))
  pygame.draw.rect(s, col, (0, 0, TS, TS), 1)
  pygame.draw.rect(s, col, (6, 5, 4, 6))
  return s


_add('tiles/spawners', [lambda v=v: _spawner(v) for v in range(2)])


# ---------------------------------------------------------------- scenery
def _cloud(w, h, blobs):
  s = _surf(w, h)
  col, shade = (236, 242, 255), (200, 214, 240)
  for cx, cy, r in blobs:
    pygame.draw.circle(s, col, (cx, cy), r)
  pygame.draw.rect(s, col, (4, h - 6, w - 8, 6))
  pygame.draw.rect(s, shade, (4, h - 3, w - 8, 3))
  return s


_add('clouds', [
  lambda: _cloud(48, 20, [(12, 12, 8), (24, 9, 9), (36, 13, 7)]),
  lambda: _cloud(64, 24, [(14, 15, 9), (30, 11, 11), (46, 14, 9), (56, 17, 6)]),
  lambda: _cloud(36, 16, [(10, 10, 7), (22, 8, 8), (29, 11, 5)]),
])


def _background():
  s = _surf(320, 240)
  top, bot = (64, 112, 200), (170, 210, 240)
  for y in range(240):
    k = (y // 12 * 12) / 240  # banded gradient = pixel-art look
    pygame.draw.line(s, tuple(int(top[i] + (bot[i] - top[i]) * k) for i in range(3)), (0, y), (319, y))
  for base, amp, col, ph in ((150, 14, (128, 170, 220), 0.0), (185, 10, (104, 150, 200), 2.0)):
    for x in range(320):
      h = base + int(amp * math.sin(x * 0.02 + ph) + amp * 0.5 * math.sin(x * 0.05 + ph + 1))
      pygame.draw.line(s, col, (x, h), (x, 239))
  return s


IMAGES['background.png'] = _background


# ---------------------------------------------------------------- characters
PLAYER = ((46, 52, 92), (28, 32, 60), (220, 50, 60), (240, 200, 160))
ENEMY = ((92, 64, 64), (56, 40, 44), (240, 190, 60), (226, 186, 150))


def _ninja(pal, bob=0, legs=((0, 0), (0, 0)), arm=0):
  """16x18 sprite facing right; hitbox (8x15) sits at x 3..10, feet on the last row."""
  body, dark, accent, skin = pal
  y = bob
  s = _surf(16, 18)
  for (dx, lift), x0 in zip(legs, (5, 8)):
    pygame.draw.rect(s, dark, (x0 + dx, 14, 2, 4 - lift))
  pygame.draw.rect(s, dark, (3, 10 + y - arm, 2, 3))     # back arm
  pygame.draw.rect(s, body, (4, 9 + y, 7, 5))            # torso
  pygame.draw.rect(s, accent, (4, 12 + y, 7, 1))         # belt
  pygame.draw.rect(s, body, (4, 3 + y, 7, 6))            # head
  pygame.draw.rect(s, skin, (7, 5 + y, 4, 2))            # face
  s.set_at((9, 5 + y), (20, 20, 30))                     # eye
  pygame.draw.rect(s, accent, (4, 4 + y, 7, 1))          # headband
  pygame.draw.rect(s, accent, (2, 4 + y, 2, 1))          # headband tail
  s.set_at((1, 5 + y), accent)
  pygame.draw.rect(s, dark, (9, 10 + y + arm, 2, 3))     # front arm
  return s


RUN_LEGS = [((-2, 0), (2, 2)), ((-1, 0), (1, 1)), ((0, 0), (0, 0)),
            ((2, 2), (-2, 0)), ((1, 1), (-1, 0)), ((0, 0), (0, 0))]
RUN_ARMS = [-1, 0, 1, 1, 0, -1]

for _name, _pal in (('player', PLAYER), ('enemy', ENEMY)):
  _add('entities/' + _name + '/idle', [lambda p=_pal, b=b: _ninja(p, bob=b) for b in (0, 0, 0, 1, 1, 1)])
  _add('entities/' + _name + '/run', [lambda p=_pal, i=i: _ninja(p, bob=i % 2, legs=RUN_LEGS[i], arm=RUN_ARMS[i]) for i in range(6)])
  if _name == 'player':
    _add('entities/player/jump', [lambda: _ninja(PLAYER, legs=((-1, 1), (2, 1)), arm=-2)])
    _add('entities/player/slide', [lambda: _ninja(PLAYER, bob=3, legs=((0, 2), (0, 2)))])
    _add('entities/player/wall_slide', [lambda: _ninja(PLAYER, legs=((0, 0), (-1, 1)), arm=-3)])

IMAGES['entities/player.png'] = lambda: _ninja(PLAYER).subsurface((3, 3, 8, 15)).copy()


def _gun():
  s = _surf(7, 4)
  pygame.draw.rect(s, (130, 130, 140), (0, 1, 6, 2))
  pygame.draw.rect(s, (110, 74, 44), (1, 3, 2, 1))
  s.set_at((6, 1), (200, 200, 210))
  return s


def _projectile():
  s = _surf(5, 3)
  pygame.draw.rect(s, (255, 190, 70), (0, 0, 5, 3))
  pygame.draw.rect(s, (255, 250, 220), (1, 1, 3, 1))
  return s


IMAGES['gun.png'] = _gun
IMAGES['projectile.png'] = _projectile


# ---------------------------------------------------------------- particles
def _leaf(i):
  s = _surf(4, 4)
  if i % 2 == 0:
    pygame.draw.rect(s, (60, 160, 60), (0, 1, 3, 2))
  else:
    pygame.draw.rect(s, (60, 160, 60), (1, 0, 2, 3))
  s.set_at((1, 1), (120, 205, 90))
  return s


def _dot(r):
  s = _surf(9, 9)
  pygame.draw.circle(s, (255, 255, 255), (4, 4), r)
  return s


_add('particles/leaf', [lambda i=i: _leaf(i) for i in range(6)])
_add('particles/particle', [lambda r=r: _dot(r) for r in (4, 3, 2, 1)])


# ---------------------------------------------------------------- audio
def _synth(seconds, fn):
  freq, _fmt, ch = pygame.mixer.get_init()
  n = int(freq * seconds)
  buf = array.array('h')
  for i in range(n):
    v = int(max(-1.0, min(1.0, fn(i / freq, i / n))) * 20000)
    buf.extend([v] * ch)
  return pygame.mixer.Sound(buffer=buf.tobytes())


def _square(p):
  return 1.0 if (p % 1.0) < 0.5 else -1.0


def _tri(p):
  return 4 * abs((p % 1.0) - 0.5) - 1


def _sweep(f0, f1, dur, t):  # phase of a linear frequency sweep
  return f0 * t + (f1 - f0) * t * t / (2 * dur)


_CHORDS = [(0, 3, 7), (-4, 0, 3), (3, 7, 10), (-2, 2, 5)]
_NOTES = [c[p] + (12 if p == 2 else 0) for c in _CHORDS for p in (0, 1, 2, 1, 0, 1, 2, 1)]
_NOTE_LEN = 0.2


def _music(t, k):
  idx = min(int(t / _NOTE_LEN), len(_NOTES) - 1)
  local = t - idx * _NOTE_LEN
  f = 220 * 2 ** (_NOTES[idx] / 12)
  root = 110 * 2 ** (_CHORDS[idx // 8][0] / 12)
  return _tri(f * local + 0.25) * 0.3 * math.exp(-local * 12) + _square(root * t) * 0.05


SOUNDS = {
  'jump': lambda: _synth(0.15, lambda t, k: _square(_sweep(260, 620, 0.15, t)) * 0.35 * (1 - k)),
  'dash': lambda: _synth(0.3, lambda t, k: random.uniform(-1, 1) * 0.5 * math.sin(math.pi * k)),
  'hit': lambda: _synth(0.3, lambda t, k: (random.uniform(-1, 1) * 0.6 + math.sin(2 * math.pi * 90 * t) * 0.7) * (1 - k) ** 2),
  'shoot': lambda: _synth(0.18, lambda t, k: _square(_sweep(900, 150, 0.18, t)) * 0.35 * (1 - k) ** 1.5),
  # integer cycles over 4s -> loops with no click
  'ambience': lambda: _synth(4, lambda t, k: (math.sin(2 * math.pi * 55 * t) * 0.3 + math.sin(2 * math.pi * 82.5 * t) * 0.2)
                              * (0.6 + 0.4 * math.sin(2 * math.pi * 0.5 * t))),
  'music': lambda: _synth(_NOTE_LEN * len(_NOTES), _music),
}


def make_sound(name):
  return SOUNDS[name]()
