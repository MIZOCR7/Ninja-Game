import json
import math
import os
import random
import sys

import pygame


WIDTH, HEIGHT = 640 * 1.2, 480 * 1.2
FPS = 60
TILE_SIZE = 16
IMAGE_FACTORIES = {}


def resource_path(path):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, path)


def _surface(width, height, color=(0, 0, 0)):
    surface = pygame.Surface((width, height))
    surface.fill(color)
    return surface


def _register_images(folder, factories):
    for index, factory in enumerate(factories):
        IMAGE_FACTORIES[f"{folder}/{index}.png"] = factory


def _tile(kind, variant):
    open_sides = {
        0: "TL", 1: "T", 2: "TR", 3: "R", 4: "BR",
        5: "B", 6: "BL", 7: "L", 8: "",
    }[variant]
    if kind == "stone":
        base, dark, light = (104, 108, 128), (66, 70, 92), (148, 152, 174)
    else:
        base, dark, light = (122, 84, 54), (84, 56, 38), (158, 112, 74)

    surface = _surface(TILE_SIZE, TILE_SIZE, base)
    rng = random.Random(variant + (50 if kind == "grass" else 0))
    for _ in range(14):
        surface.set_at((rng.randrange(TILE_SIZE), rng.randrange(TILE_SIZE)), dark)

    if kind == "stone":
        for y in (5, 11):
            pygame.draw.line(surface, dark, (0, y), (15, y))
        for x, top, bottom in ((8, 0, 4), (3, 6, 10), (12, 6, 10), (8, 12, 15)):
            pygame.draw.line(surface, dark, (x, top), (x, bottom))
    if "L" in open_sides:
        pygame.draw.line(surface, light, (0, 0), (0, 15))
    if "R" in open_sides:
        pygame.draw.line(surface, dark, (15, 0), (15, 15))
    if "B" in open_sides:
        pygame.draw.line(surface, dark, (0, 15), (15, 15))
    if "T" in open_sides:
        if kind == "grass":
            green = (70, 168, 62)
            pygame.draw.rect(surface, green, (0, 0, TILE_SIZE, 4))
            for x in range(TILE_SIZE):
                if rng.random() < 0.45:
                    surface.set_at((x, 4), green)
                if rng.random() < 0.15:
                    surface.set_at((x, 5), green)
            pygame.draw.line(surface, (118, 206, 88), (0, 0), (15, 0))
        else:
            pygame.draw.line(surface, light, (0, 0), (15, 0))
    corners = {0: (0, 0), 2: (15, 0), 4: (15, 15), 6: (0, 15)}
    if variant in corners:
        surface.set_at(corners[variant], (0, 0, 0))
    return surface


def _decor(variant):
    surface = _surface(16, 16)
    green, dark_green = (70, 168, 62), (40, 120, 50)
    if variant in (0, 1):
        blades = (
            ((3, 6), (6, 9), (9, 7), (12, 5))
            if variant == 0
            else ((2, 3), (5, 4), (8, 3), (11, 5), (13, 3))
        )
        for x, height in blades:
            color = green if variant == 0 else dark_green
            pygame.draw.rect(surface, color, (x, 16 - height, 1, height))
            if variant == 0:
                surface.set_at((x, 16 - height), (118, 206, 88))
    elif variant == 2:
        pygame.draw.rect(surface, dark_green, (7, 8, 1, 8))
        for point in ((5, 12), (6, 11), (9, 11), (10, 12)):
            surface.set_at(point, green)
        for point in ((6, 7), (8, 7), (7, 6), (7, 8)):
            surface.set_at(point, (220, 60, 70))
        surface.set_at((7, 7), (250, 220, 80))
    else:
        pygame.draw.rect(surface, (230, 220, 200), (7, 11, 2, 5))
        pygame.draw.rect(surface, (200, 50, 60), (5, 8, 6, 3))
        pygame.draw.rect(surface, (200, 50, 60), (6, 7, 4, 1))
        surface.set_at((6, 9), (255, 255, 255))
        surface.set_at((9, 8), (255, 255, 255))
    return surface


def _large_decor(variant):
    if variant < 2:
        surface = _surface(32, 16)
        if variant == 0:
            for center, radius, color in (
                ((9, 10), 7, (46, 140, 58)),
                ((20, 8), 8, (46, 140, 58)),
                ((26, 11), 5, (46, 140, 58)),
                ((8, 8), 3, (80, 180, 80)),
                ((19, 5), 3, (80, 180, 80)),
            ):
                pygame.draw.circle(surface, color, center, radius)
            pygame.draw.rect(surface, (30, 100, 46), (2, 14, 28, 2))
        else:
            pygame.draw.polygon(
                surface, (120, 124, 140),
                [(2, 15), (6, 6), (14, 3), (20, 8), (22, 15)],
            )
            pygame.draw.polygon(
                surface, (96, 100, 118), [(18, 15), (22, 9), (28, 8), (31, 15)]
            )
            pygame.draw.line(surface, (160, 164, 182), (7, 7), (13, 4))
            pygame.draw.line(surface, (130, 134, 152), (23, 10), (27, 9))
        return surface

    surface = _surface(32, 32)
    pygame.draw.rect(surface, (110, 72, 44), (14, 16, 4, 16))
    pygame.draw.rect(surface, (80, 50, 32), (16, 16, 2, 16))
    pygame.draw.rect(surface, (110, 72, 44), (10, 20, 4, 1))
    for center, radius, color in (
        ((10, 12), 8, (36, 120, 52)),
        ((22, 12), 8, (36, 120, 52)),
        ((16, 8), 8, (46, 140, 58)),
        ((13, 6), 4, (84, 188, 84)),
        ((22, 10), 3, (70, 170, 70)),
    ):
        pygame.draw.circle(surface, color, center, radius)
    rng = random.Random(3)
    for _ in range(18):
        surface.set_at((rng.randrange(4, 28), rng.randrange(2, 18)), (28, 96, 44))
    return surface


def _spawner(variant):
    color = (60, 120, 255) if variant == 0 else (255, 80, 80)
    surface = _surface(TILE_SIZE, TILE_SIZE, (20, 20, 40))
    pygame.draw.rect(surface, color, (0, 0, TILE_SIZE, TILE_SIZE), 1)
    pygame.draw.rect(surface, color, (6, 5, 4, 6))
    return surface


def _cloud(width, height, blobs):
    surface = _surface(width, height)
    color, shade = (236, 242, 255), (200, 214, 240)
    for center_x, center_y, radius in blobs:
        pygame.draw.circle(surface, color, (center_x, center_y), radius)
    pygame.draw.rect(surface, color, (4, height - 6, width - 8, 6))
    pygame.draw.rect(surface, shade, (4, height - 3, width - 8, 3))
    return surface


def _background():
    surface = _surface(320, 240)
    top, bottom = (64, 112, 200), (170, 210, 240)
    for y in range(240):
        blend = (y // 12 * 12) / 240
        color = tuple(int(top[i] + (bottom[i] - top[i]) * blend) for i in range(3))
        pygame.draw.line(surface, color, (0, y), (319, y))
    for base, amplitude, color, phase in (
        (150, 14, (128, 170, 220), 0.0),
        (185, 10, (104, 150, 200), 2.0),
    ):
        for x in range(320):
            height = base + int(
                amplitude * math.sin(x * 0.02 + phase)
                + amplitude * 0.5 * math.sin(x * 0.05 + phase + 1)
            )
            pygame.draw.line(surface, color, (x, height), (x, 239))
    return surface


PLAYER_PALETTE = ((46, 52, 92), (28, 32, 60), (220, 50, 60), (240, 200, 160))
ENEMY_PALETTE = ((92, 64, 64), (56, 40, 44), (240, 190, 60), (226, 186, 150))
RUN_LEGS = [
    ((-2, 0), (2, 2)), ((-1, 0), (1, 1)), ((0, 0), (0, 0)),
    ((2, 2), (-2, 0)), ((1, 1), (-1, 0)), ((0, 0), (0, 0)),
]
RUN_ARMS = [-1, 0, 1, 1, 0, -1]


def _ninja(palette, bob=0, legs=((0, 0), (0, 0)), arm=0):
    body, dark, accent, skin = palette
    surface = _surface(16, 18)
    for (offset, lift), x in zip(legs, (5, 8)):
        pygame.draw.rect(surface, dark, (x + offset, 14, 2, 4 - lift))
    pygame.draw.rect(surface, dark, (3, 10 + bob - arm, 2, 3))
    pygame.draw.rect(surface, body, (4, 9 + bob, 7, 5))
    pygame.draw.rect(surface, accent, (4, 12 + bob, 7, 1))
    pygame.draw.rect(surface, body, (4, 3 + bob, 7, 6))
    pygame.draw.rect(surface, skin, (7, 5 + bob, 4, 2))
    surface.set_at((9, 5 + bob), (20, 20, 30))
    pygame.draw.rect(surface, accent, (4, 4 + bob, 7, 1))
    pygame.draw.rect(surface, accent, (2, 4 + bob, 2, 1))
    surface.set_at((1, 5 + bob), accent)
    pygame.draw.rect(surface, dark, (9, 10 + bob + arm, 2, 3))
    return surface


def _gun():
    surface = _surface(7, 4)
    pygame.draw.rect(surface, (130, 130, 140), (0, 1, 6, 2))
    pygame.draw.rect(surface, (110, 74, 44), (1, 3, 2, 1))
    surface.set_at((6, 1), (200, 200, 210))
    return surface


def _projectile():
    surface = _surface(5, 3)
    pygame.draw.rect(surface, (255, 190, 70), (0, 0, 5, 3))
    pygame.draw.rect(surface, (255, 250, 220), (1, 1, 3, 1))
    return surface


def _leaf(index):
    surface = _surface(4, 4)
    if index % 2 == 0:
        pygame.draw.rect(surface, (60, 160, 60), (0, 1, 3, 2))
    else:
        pygame.draw.rect(surface, (60, 160, 60), (1, 0, 2, 3))
    surface.set_at((1, 1), (120, 205, 90))
    return surface


def _particle(radius):
    surface = _surface(9, 9)
    pygame.draw.circle(surface, (255, 255, 255), (4, 4), radius)
    return surface


_register_images("tiles/grass", [lambda i=i: _tile("grass", i) for i in range(9)])
_register_images("tiles/stone", [lambda i=i: _tile("stone", i) for i in range(9)])
_register_images("tiles/decor", [lambda i=i: _decor(i) for i in range(4)])
_register_images("tiles/large_decor", [lambda i=i: _large_decor(i) for i in range(3)])
_register_images("tiles/spawners", [lambda i=i: _spawner(i) for i in range(2)])
_register_images(
    "clouds",
    [
        lambda: _cloud(48, 20, [(12, 12, 8), (24, 9, 9), (36, 13, 7)]),
        lambda: _cloud(64, 24, [(14, 15, 9), (30, 11, 11), (46, 14, 9), (56, 17, 6)]),
        lambda: _cloud(36, 16, [(10, 10, 7), (22, 8, 8), (29, 11, 5)]),
    ],
)
IMAGE_FACTORIES["background.png"] = _background
for _name, _palette in (("player", PLAYER_PALETTE), ("enemy", ENEMY_PALETTE)):
    _register_images(
        f"entities/{_name}/idle",
        [lambda p=_palette, b=b: _ninja(p, bob=b) for b in (0, 0, 0, 1, 1, 1)],
    )
    _register_images(
        f"entities/{_name}/run",
        [
            lambda p=_palette, i=i: _ninja(
                p, bob=i % 2, legs=RUN_LEGS[i], arm=RUN_ARMS[i]
            )
            for i in range(6)
        ],
    )
    if _name == "player":
        _register_images(
            "entities/player/jump",
            [lambda: _ninja(PLAYER_PALETTE, legs=((-1, 1), (2, 1)), arm=-2)],
        )
        _register_images(
            "entities/player/slide",
            [lambda: _ninja(PLAYER_PALETTE, bob=3, legs=((0, 2), (0, 2)))],
        )
        _register_images(
            "entities/player/wall_slide",
            [lambda: _ninja(PLAYER_PALETTE, legs=((0, 0), (-1, 1)), arm=-3)],
        )
IMAGE_FACTORIES["entities/player.png"] = (
    lambda: _ninja(PLAYER_PALETTE).subsurface((3, 3, 8, 15)).copy()
)
IMAGE_FACTORIES["gun.png"] = _gun
IMAGE_FACTORIES["projectile.png"] = _projectile
_register_images("particles/leaf", [lambda i=i: _leaf(i) for i in range(6)])
_register_images("particles/particle", [lambda r=r: _particle(r) for r in (4, 3, 2, 1)])


def load_image(path):
    image = IMAGE_FACTORIES[path]().convert()
    image.set_colorkey((0, 0, 0))
    return image


def load_images(folder):
    filenames = sorted(
        (path.rsplit("/", 1)[1] for path in IMAGE_FACTORIES if path.rsplit("/", 1)[0] == folder),
        key=lambda name: int(name.split(".")[0]),
    )
    return [load_image(f"{folder}/{filename}") for filename in filenames]


class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)

    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    def img(self):
        return self.images[int(self.frame / self.img_duration)]


AUTOTILE_MAP = {
    tuple(sorted(((1, 0), (0, 1)))): 0,
    tuple(sorted(((1, 0), (0, 1), (-1, 0)))): 1,
    tuple(sorted(((-1, 0), (0, 1)))): 2,
    tuple(sorted(((-1, 0), (0, -1), (0, 1)))): 3,
    tuple(sorted(((-1, 0), (0, -1)))): 4,
    tuple(sorted(((-1, 0), (0, -1), (1, 0)))): 5,
    tuple(sorted(((1, 0), (0, -1)))): 6,
    tuple(sorted(((1, 0), (0, -1), (0, 1)))): 7,
    tuple(sorted(((1, 0), (-1, 0), (0, 1), (0, -1)))): 8,
}
NEIGHBOR_OFFSETS = [
    (-1, 0), (-1, -1), (1, -1), (1, 0),
    (0, 0), (-1, 1), (0, 1), (1, 1),
]
PHYSICS_TILES = {"grass", "stone"}


class Tilemap:
    def __init__(self, game, tile_size=TILE_SIZE):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile["type"], tile["variant"]) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)
        for location in list(self.tilemap):
            tile = self.tilemap[location]
            if (tile["type"], tile["variant"]) in id_pairs:
                matches.append(tile.copy())
                matches[-1]["pos"] = matches[-1]["pos"].copy()
                matches[-1]["pos"][0] *= self.tile_size
                matches[-1]["pos"][1] *= self.tile_size
                if not keep:
                    del self.tilemap[location]
        return matches

    def tiles_around(self, pos):
        tile_x, tile_y = int(pos[0] // self.tile_size), int(pos[1] // self.tile_size)
        tiles = []
        for dx, dy in NEIGHBOR_OFFSETS:
            key = f"{tile_x + dx};{tile_y + dy}"
            if key in self.tilemap:
                tiles.append(self.tilemap[key])
        return tiles

    def save(self, path):
        with open(path, "w") as file:
            json.dump(
                {
                    "tilemap": self.tilemap,
                    "tile_size": self.tile_size,
                    "offgrid": self.offgrid_tiles,
                },
                file,
            )

    def load(self, path):
        with open(path, "r") as file:
            map_data = json.load(file)
        self.tilemap = map_data["tilemap"]
        self.tile_size = map_data["tile_size"]
        self.offgrid_tiles = map_data["offgrid"]

    def solid_checks(self, pos):
        location = f"{int(pos[0] // self.tile_size)};{int(pos[1] // self.tile_size)}"
        tile = self.tilemap.get(location)
        if tile and tile["type"] in PHYSICS_TILES:
            return tile
        return None

    def physics_rects_around(self, pos):
        rects = []
        left, top = int(pos[0] // self.tile_size), int(pos[1] // self.tile_size)
        right = int((pos[0] + self.tile_size - 1) // self.tile_size)
        bottom = int((pos[1] + self.tile_size - 1) // self.tile_size)
        for tile_y in range(top - 1, bottom + 2):
            for tile_x in range(left - 1, right + 2):
                tile = self.tilemap.get(f"{tile_x};{tile_y}")
                if tile and tile["type"] in PHYSICS_TILES:
                    rects.append(
                        pygame.Rect(
                            tile["pos"][0] * self.tile_size,
                            tile["pos"][1] * self.tile_size,
                            self.tile_size,
                            self.tile_size,
                        )
                    )
        return rects

    def autotile(self):
        for tile in self.tilemap.values():
            neighbors = set()
            for shift in ((1, 0), (-1, 0), (0, -1), (0, 1)):
                location = f"{tile['pos'][0] + shift[0]};{tile['pos'][1] + shift[1]}"
                neighbor = self.tilemap.get(location)
                if neighbor and neighbor["type"] == tile["type"]:
                    neighbors.add(shift)
            neighbor_key = tuple(sorted(neighbors))
            if tile["type"] in PHYSICS_TILES and neighbor_key in AUTOTILE_MAP:
                tile["variant"] = AUTOTILE_MAP[neighbor_key]

    def render(self, surface, offset=(0, 0)):
        for tile in self.offgrid_tiles:
            if tile["type"] in self.game.assets:
                surface.blit(
                    self.game.assets[tile["type"]][tile["variant"]],
                    (tile["pos"][0] - offset[0], tile["pos"][1] - offset[1]),
                )
        left = offset[0] // self.tile_size
        right = (offset[0] + surface.get_width()) // self.tile_size + 1
        top = offset[1] // self.tile_size
        bottom = (offset[1] + surface.get_height()) // self.tile_size + 1
        for tile_x in range(left, right):
            for tile_y in range(top, bottom):
                tile = self.tilemap.get(f"{tile_x};{tile_y}")
                if tile and tile["type"] in self.game.assets:
                    surface.blit(
                        self.game.assets[tile["type"]][tile["variant"]],
                        (
                            tile["pos"][0] * self.tile_size - offset[0],
                            tile["pos"][1] * self.tile_size - offset[1],
                        ),
                    )


class Cloud:
    def __init__(self, pos, image, speed, depth):
        self.pos = list(pos)
        self.image = image
        self.speed = speed
        self.depth = depth

    def update(self):
        self.pos[0] += self.speed

    def render(self, surface, offset=(0, 0)):
        x = self.pos[0] - offset[0] * self.depth
        y = self.pos[1] - offset[1] * self.depth
        surface.blit(
            self.image,
            (
                x % (surface.get_width() + self.image.get_width()),
                y % (surface.get_height() + self.image.get_height()) - self.image.get_height(),
            ),
        )


class Clouds:
    def __init__(self, images, count=16):
        self.clouds = [
            Cloud(
                (random.random() * 99999, random.random() * 99999),
                random.choice(images),
                random.random() * 0.05 + 0.05,
                random.random() * 0.6 + 0.2,
            )
            for _ in range(count)
        ]
        self.clouds.sort(key=lambda cloud: cloud.depth)

    def update(self):
        for cloud in self.clouds:
            cloud.update()

    def render(self, surface, offset=(0, 0)):
        for cloud in self.clouds:
            cloud.render(surface, offset=offset)


class Particle:
    def __init__(self, game, p_type, pos, velocity=None, frame=0):
        self.game = game
        self.type = p_type
        self.pos = list(pos)
        self.velocity = list(velocity or (0, 0))
        self.animation = game.assets[f"particle/{p_type}"].copy()
        self.animation.frame = frame

    def update(self):
        kill = self.animation.done
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.animation.update()
        return kill

    def render(self, surface, offset=(0, 0)):
        image = self.animation.img()
        surface.blit(
            image,
            (
                self.pos[0] - offset[0] - image.get_width() // 2,
                self.pos[1] - offset[1] - image.get_height() // 2,
            ),
        )


class Spark:
    def __init__(self, pos, angle, speed):
        self.pos = list(pos)
        self.angle = angle
        self.speed = speed

    def update(self):
        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed
        self.speed = max(0, self.speed - 0.1)
        return self.speed

    def render(self, surface, offset=(0, 0)):
        points = [
            (
                self.pos[0] + math.cos(self.angle) * self.speed * 3 - offset[0],
                self.pos[1] + math.sin(self.angle) * self.speed * 3 - offset[1],
            ),
            (
                self.pos[0] + math.cos(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[0],
                self.pos[1] + math.sin(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[1],
            ),
            (
                self.pos[0] + math.cos(self.angle + math.pi) * self.speed * 3 - offset[0],
                self.pos[1] + math.sin(self.angle + math.pi) * self.speed * 3 - offset[1],
            ),
            (
                self.pos[0] + math.cos(self.angle - math.pi * 0.5) * self.speed * 0.5 - offset[0],
                self.pos[1] + math.sin(self.angle - math.pi * 0.5) * self.speed * 0.5 - offset[1],
            ),
        ]
        pygame.draw.polygon(surface, (255, 255, 255), points)


class PhysicsEntity:
    def __init__(self, game, entity_type, pos, size):
        self.game = game
        self.type = entity_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {"up": False, "down": False, "right": False, "left": False}
        self.action = ""
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action("idle")
        self.last_movement = [0, 0]

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[f"{self.type}/{self.action}"].copy()

    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {"up": False, "down": False, "right": False, "left": False}
        frame_movement = (
            movement[0] + self.velocity[0],
            movement[1] + self.velocity[1],
        )
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions["right"] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions["left"] = True
                self.pos[0] = entity_rect.x
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions["down"] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions["up"] = True
                self.pos[1] = entity_rect.y
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
        self.last_movement = movement
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        if self.collisions["down"] or self.collisions["up"]:
            self.velocity[1] = 0
        self.animation.update()

    def render(self, surface, offset=(0, 0)):
        image = pygame.transform.flip(self.animation.img(), self.flip, False)
        surface.blit(
            image,
            (
                self.pos[0] - offset[0] + self.anim_offset[0],
                self.pos[1] - offset[1] + self.anim_offset[1],
            ),
        )


class Enemy(PhysicsEntity):
    def __init__(self, game, entity_type, pos, size):
        super().__init__(game, "enemy", pos, size)
        self.walking = 0

    def update(self, tilemap, movement=(0, 0)):
        if self.walking:
            if tilemap.solid_checks(
                (self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)
            ):
                if self.collisions["right"] or self.collisions["left"]:
                    self.flip = not self.flip
                else:
                    movement = (
                        movement[0] - 0.5 if self.flip else movement[0] + 0.5,
                        movement[1],
                    )
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking:
                distance = (
                    self.game.player.pos[0] - self.pos[0],
                    self.game.player.pos[1] - self.pos[1],
                )
                if abs(distance[1]) < 16:
                    if self.flip and distance[0] < 0:
                        self._shoot(-1.5, math.pi)
                    elif not self.flip and distance[0] > 0:
                        self._shoot(1.5, 0)
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)

        super().update(tilemap, movement=movement)
        self.set_action("run" if movement[0] != 0 else "idle")
        if abs(self.game.player.dashing) >= 50 and self.rect().colliderect(
            self.game.player.rect()
        ):
            self.game.screen_shake = max(16, self.game.screen_shake)
            self.game.sfx["hit"].play()
            self.game.freeze = 8
            for _ in range(30):
                angle = random.random() * math.pi * 2
                speed = random.random() * 5
                self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                self.game.particles.append(
                    Particle(
                        self.game,
                        "particle",
                        self.rect().center,
                        velocity=[
                            math.cos(angle + math.pi) * speed * 0.5,
                            math.sin(angle + math.pi) * speed * 0.5,
                        ],
                        frame=random.randint(0, 7),
                    )
                )
            self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
            self.game.sparks.append(
                Spark(self.rect().center, math.pi, 5 + random.random())
            )
            return True
        return False

    def _shoot(self, speed, angle_offset):
        self.game.sfx["shoot"].play()
        x_offset = -7 if speed < 0 else 7
        projectile = [[self.rect().centerx + x_offset, self.rect().centery], speed, 0]
        self.game.projectiles.append(projectile)
        for _ in range(4):
            self.game.sparks.append(
                Spark(
                    projectile[0],
                    random.random() - 0.5 + angle_offset,
                    2 + random.random(),
                )
            )

    def render(self, surface, offset=(0, 0)):
        super().render(surface, offset=offset)
        if self.flip:
            gun = pygame.transform.flip(self.game.assets["gun"], True, False)
            pos = (
                self.rect().centerx - 4 - gun.get_width() - offset[0],
                self.rect().centery - offset[1],
            )
        else:
            gun = self.game.assets["gun"]
            pos = (self.rect().centerx + 4 - offset[0], self.rect().centery - offset[1])
        surface.blit(gun, pos)


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, "player", pos, size)
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)
        self.air_time += 1
        if self.air_time > 120:
            if not self.game.dead:
                self.game.screen_shake = max(16, self.game.screen_shake)
            self.game.dead += 1
        if self.collisions["down"]:
            self.air_time = 0
            self.jumps = 1

        self.wall_slide = False
        if (self.collisions["right"] or self.collisions["left"]) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            self.flip = not self.collisions["right"]
            self.set_action("wall_slide")
        elif self.air_time > 4:
            self.set_action("jump")
        elif movement[0] != 0:
            self.set_action("run")
        else:
            self.set_action("idle")

        if abs(self.dashing) in {60, 50}:
            for _ in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                self.game.particles.append(
                    Particle(
                        self.game,
                        "particle",
                        self.rect().center,
                        velocity=[math.cos(angle) * speed, math.sin(angle) * speed],
                        frame=random.randint(0, 7),
                    )
                )
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
            particle_speed = abs(self.dashing) / self.dashing * random.random() * 3
            self.game.particles.append(
                Particle(
                    self.game,
                    "particle",
                    self.rect().center,
                    velocity=[particle_speed, 0],
                    frame=random.randint(0, 7),
                )
            )
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    def render(self, surface, offset=(0, 0)):
        if abs(self.dashing) <= 50:
            super().render(surface, offset=offset)

    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0], self.velocity[1] = 3.5, -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            if not self.flip and self.last_movement[0] > 0:
                self.velocity[0], self.velocity[1] = -3.5, -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
        elif self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5
            return True
        return False

    def dash(self):
        if not self.dashing:
            self.game.sfx["dash"].play()
            self.dashing = -60 if self.flip else 60


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Ninja Game")
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 240))
        self.clock = pygame.time.Clock()
        self.movement = [False, False]
        self.freeze = 0
        self.assets = {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "large_decor": load_images("tiles/large_decor"),
            "stone": load_images("tiles/stone"),
            "player": load_image("entities/player.png"),
            "background": load_image("background.png"),
            "clouds": load_images("clouds"),
            "player/idle": Animation(load_images("entities/player/idle"), img_dur=6),
            "player/run": Animation(load_images("entities/player/run"), img_dur=4),
            "player/jump": Animation(load_images("entities/player/jump")),
            "player/slide": Animation(load_images("entities/player/slide")),
            "player/wall_slide": Animation(load_images("entities/player/wall_slide")),
            "particle/leaf": Animation(
                load_images("particles/leaf"), img_dur=20, loop=False
            ),
            "particle/particle": Animation(
                load_images("particles/particle"), img_dur=6, loop=False
            ),
            "enemy/idle": Animation(load_images("entities/enemy/idle"), img_dur=6),
            "enemy/run": Animation(load_images("entities/enemy/run"), img_dur=4),
            "gun": load_image("gun.png"),
            "projectile": load_image("projectile.png"),
        }
        self.sfx = {
            name: pygame.mixer.Sound(resource_path(f"data/sfx/{name}.wav"))
            for name in ("jump", "dash", "hit", "shoot", "ambience")
        }
        for name, volume in {
            "ambience": 0.2, "shoot": 0.4, "hit": 0.8, "dash": 0.3, "jump": 0.7,
        }.items():
            self.sfx[name].set_volume(volume)
        self.clouds = Clouds(self.assets["clouds"], count=16)
        self.player = Player(self, (50, 50), (8, 15))
        self.tilemap = Tilemap(self)
        self.level = 0
        self.load_level(str(self.level))
        self.screen_shake = 0
        self.font = pygame.font.Font(None, 16)

    def draw_text(self, text, surface, pos, color=(255, 255, 255), shadow_color=(0, 0, 0)):
        shadow = self.font.render(text, False, shadow_color)
        surface.blit(shadow, (pos[0] + 1, pos[1] + 1))
        surface.blit(self.font.render(text, False, color), pos)

    def load_level(self, map_id):
        self.tilemap.load(resource_path(f"data/maps/{map_id}.json"))
        self.leaf_spawners = [
            pygame.Rect(4 + tree["pos"][0], 4 + tree["pos"][1], 23, 13)
            for tree in self.tilemap.extract([("large_decor", 2)], keep=True)
        ]
        self.enemies = []
        for spawner in self.tilemap.extract([("spawners", 0), ("spawners", 1)]):
            if spawner["variant"] == 0:
                self.player.pos = spawner["pos"]
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, "enemy", spawner["pos"], (8, 15)))
        self.projectiles = []
        self.particles = []
        self.scroll = [0, 0]
        self.sparks = []
        self.dead = 0
        self.transition_level = -30

    def run(self):
        pygame.mixer.music.load(resource_path("data/music.wav"))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        self.sfx["ambience"].play(-1)
        while True:
            self.screen_shake = max(0, self.screen_shake - 1)
            if self.freeze > 0:
                self.freeze -= 1
            if not self.freeze:
                self._update_world()
            self._handle_events()
            self._draw_transition()
            self._draw_hud()
            self._present_frame()
            self.clock.tick(FPS)

    def _update_world(self):
        self.display.fill((0, 0, 0, 0))
        self.display_2.blit(self.assets["background"], (0, 0))
        if not self.enemies:
            self.transition_level += 1
            if self.transition_level > 30:
                map_count = len(
                    [
                        filename
                        for filename in os.listdir(resource_path("data/maps"))
                        if filename.endswith(".json") and filename[0].isdigit()
                    ]
                )
                self.level = min(self.level + 1, map_count - 1)
                self.load_level(str(self.level))
        if self.transition_level < 0:
            self.transition_level += 1
        if self.dead:
            self.dead += 1
            if self.dead == 10:
                self.transition_level = min(30, self.transition_level + 1)
            if self.dead > 40:
                self.load_level(str(self.level))
        self.scroll[0] += (
            self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]
        ) / 30
        self.scroll[1] += (
            self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]
        ) / 30
        render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
        for rect in self.leaf_spawners:
            if random.random() * 4999 < rect.width * rect.height:
                pos = (
                    rect.x + random.random() * rect.width,
                    rect.y + random.random() * rect.height,
                )
                self.particles.append(
                    Particle(
                        self, "leaf", pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)
                    )
                )
        self.clouds.update()
        self.clouds.render(self.display_2, offset=render_scroll)
        self.tilemap.render(self.display, offset=render_scroll)
        for enemy in self.enemies.copy():
            kill = enemy.update(self.tilemap, (0, 0))
            enemy.render(self.display, offset=render_scroll)
            if kill:
                self.enemies.remove(enemy)
        if not self.dead:
            self.player.update(
                self.tilemap, (self.movement[1] - self.movement[0], 0)
            )
            self.player.render(self.display, offset=render_scroll)
        self._update_projectiles(render_scroll)
        self._update_sparks(render_scroll)
        mask = pygame.mask.from_surface(self.display)
        silhouette = mask.to_surface(
            setcolor=(0, 0, 0, 100), unsetcolor=(0, 0, 0, 0)
        )
        for offset in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            self.display_2.blit(silhouette, offset)
        for particle in self.particles.copy():
            kill = particle.update()
            particle.render(self.display, offset=render_scroll)
            if particle.type == "leaf":
                particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
            if kill:
                self.particles.remove(particle)

    def _update_projectiles(self, render_scroll):
        image = self.assets["projectile"]
        for projectile in self.projectiles.copy():
            projectile[0][0] += projectile[1]
            projectile[2] += 1
            self.display.blit(
                image,
                (
                    projectile[0][0] - image.get_width() / 2 - render_scroll[0],
                    projectile[0][1] - image.get_height() / 2 - render_scroll[1],
                ),
            )
            if self.tilemap.solid_checks(projectile[0]):
                self.projectiles.remove(projectile)
                for _ in range(4):
                    self.sparks.append(
                        Spark(
                            projectile[0],
                            random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0),
                            2 + random.random(),
                        )
                    )
            elif projectile[2] > 360:
                self.projectiles.remove(projectile)
            elif abs(self.player.dashing) < 50 and self.player.rect().collidepoint(
                projectile[0]
            ):
                self.projectiles.remove(projectile)
                self.dead += 1
                self.sfx["hit"].play()
                self.screen_shake = max(16, self.screen_shake)
                center = self.player.rect().center
                for _ in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.sparks.append(Spark(center, angle, 2 + random.random()))
                    self.particles.append(
                        Particle(
                            self,
                            "particle",
                            center,
                            velocity=[
                                math.cos(angle + math.pi) * speed * 0.5,
                                math.sin(angle + math.pi) * speed * 0.5,
                            ],
                            frame=random.randint(0, 7),
                        )
                    )

    def _update_sparks(self, render_scroll):
        for spark in self.sparks.copy():
            kill = spark.update()
            spark.render(self.display, offset=render_scroll)
            if kill:
                self.sparks.remove(spark)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.movement[0] = True
                elif event.key == pygame.K_d:
                    self.movement[1] = True
                elif event.key == pygame.K_w:
                    if self.player.jump():
                        self.sfx["jump"].play()
                elif event.key == pygame.K_x:
                    self.player.dash()
                elif event.key == pygame.K_ESCAPE:
                    self._quit()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.movement[0] = False
                elif event.key == pygame.K_d:
                    self.movement[1] = False

    @staticmethod
    def _quit():
        pygame.quit()
        sys.exit()

    def _draw_transition(self):
        if self.transition_level:
            transition = pygame.Surface(self.display.get_size())
            pygame.draw.circle(
                transition,
                (255, 255, 255),
                (self.display.get_width() // 2, self.display.get_height() // 2),
                (30 - abs(self.transition_level)) * 8,
            )
            transition.set_colorkey((255, 255, 255))
            self.display.blit(transition, (0, 0))

    def _draw_hud(self):
        self.draw_text(
            f"ENEMIES: {len(self.enemies)}", self.display, (8, 6), color=(255, 215, 0)
        )
        self.draw_text(
            f"STAGE {self.level + 1}",
            self.display,
            (self.display.get_width() - 65, 6),
            color=(200, 200, 200),
        )
        if self.dead > 5:
            self.draw_text(
                "YOU DIED",
                self.display,
                (
                    self.display.get_width() // 2 - 30,
                    self.display.get_height() // 2 - 10,
                ),
                color=(255, 40, 40),
            )

    def _present_frame(self):
        self.display_2.blit(self.display, (0, 0))
        shake = (
            random.random() * self.screen_shake - self.screen_shake / 2,
            random.random() * self.screen_shake - self.screen_shake / 2,
        )
        self.screen.blit(
            pygame.transform.scale(self.display_2, self.screen.get_size()), shake
        )
        pygame.display.update()


if __name__ == "__main__":
    Game().run()
