"""Генерация координат камней по распределению групп."""
import math
from .math_core import PHI, GOLDEN_ANGLE, golden_spiral_points


def place_group_centers(n_groups, width, height):
    """
    Размещает центры групп:
    - 5 групп: классические позиции Рёандзи
    - иначе: по золотой спирали
    """
    if n_groups == 5:
        return [
            (0.15 * width, 0.25 * height),
            (0.40 * width, 0.55 * height),
            (0.62 * width, 0.20 * height),
            (0.78 * width, 0.65 * height),
            (0.30 * width, 0.80 * height),
        ]
    centers = []
    margin = 0.15
    for i in range(n_groups):
        r_norm = (i + 0.5) / n_groups
        r = (0.5 - margin) * (PHI ** (r_norm * 2) - 1) / (PHI ** 2 - 1)
        theta = i * GOLDEN_ANGLE * 1.3
        cx = 0.5 * width + r * width * math.cos(theta)
        cy = 0.5 * height + r * height * math.sin(theta)
        cx = min(max(cx, margin * width), (1 - margin) * width)
        cy = min(max(cy, margin * height), (1 - margin) * height)
        centers.append((cx, cy))
    return centers


def create_garden(groups):
    """
    Возвращает (stones, width, height).
    stones — список словарей {x, y, radius, group}.
    """
    garden_width = PHI * 10
    garden_height = 10.0
    centers = place_group_centers(len(groups), garden_width, garden_height)
    stones = []
    for idx, (count, (cx, cy)) in enumerate(zip(groups, centers)):
        group_radius = (1.0 / PHI) * (1 + count / 10.0)
        rotation = idx * (math.pi / PHI)
        spiral_points = golden_spiral_points(count, group_radius, rotation)
        for i, (dx, dy, r) in enumerate(spiral_points):
            stones.append({
                'x': cx + dx,
                'y': cy + dy,
                'radius': 0.15 + 0.25 / PHI * (i / max(count - 1, 1) + 0.5),
                'group': idx,
            })
    return stones, garden_width, garden_height


def compute_group_zones(stones):
    """
    Возвращает список (center_x, center_y, radius) для каждой группы.
    Используется для рисования мха.
    """
    zones = []
    for g in sorted(set(s['group'] for s in stones)):
        gs = [st for st in stones if st['group'] == g]
        gx = sum(st['x'] for st in gs) / len(gs)
        gy = sum(st['y'] for st in gs) / len(gs)
        gr = max(math.hypot(st['x'] - gx, st['y'] - gy) + st['radius']
                 for st in gs)
        zones.append((gx, gy, gr, g))
    return zones