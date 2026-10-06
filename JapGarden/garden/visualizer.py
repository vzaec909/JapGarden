"""Реалистичная отрисовка сада: песок, бороздки, мох, камни, тени."""
import math
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Ellipse

from .math_core import PHI
from .generator import compute_group_zones


# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def _draw_sand_base(ax, width, height):
    """Базовый фон песка с лёгким градиентом."""
    # Основной прямоугольник
    rect = patches.Rectangle(
        (0, 0), width, height,
        linewidth=2, edgecolor='#5c4033',
        facecolor='#e8dcc4', zorder=0
    )
    ax.add_patch(rect)

    # Тёплый градиент — несколько полупрозрачных прямоугольников
    for i in range(6):
        alpha = 0.04
        inset = i * 0.3
        grad = patches.Rectangle(
            (inset, inset), width - 2 * inset, height - 2 * inset,
            linewidth=0, facecolor='#c9a876', alpha=alpha, zorder=0.1
        )
        ax.add_patch(grad)


def _draw_rake_pattern(ax, width, height, seed=42):
    """
    Бороздки граблями — волнистые горизонтальные линии.
    Мягко «обтекают» зоны групп (визуальный эффект).
    """
    random.seed(seed)
    sand_color = '#b8a179'
    n_ripples = 45

    for k in range(n_ripples):
        y_base = (k + 0.5) * height / n_ripples
        # Точки вдоль линии
        step = 0.12
        xs = [i * step for i in range(int(width / step) + 1)]
        ys = []
        for x in xs:
            # Основная волна + мягкий шум
            ripple = (0.05 * math.sin(x * 0.7 + k * 0.4)
                      + 0.02 * math.sin(x * 2.1 + k * 0.9)
                      + random.uniform(-0.015, 0.015))
            ys.append(y_base + ripple)

        ax.plot(
            xs, ys,
            color=sand_color, linewidth=0.7, alpha=0.55,
            solid_capstyle='round', zorder=1
        )


def _draw_moss_zones(ax, zones, seed=7):
    """
    Неровные зелёные пятна мха вокруг каждой группы.
    Несколько перекрывающихся эллипсов с разным поворотом.
    """
    random.seed(seed)
    moss_colors = ['#7a8b4a', '#6b7c3f', '#8a9b5a', '#5c6d35']

    for gx, gy, gr, _ in zones:
        # Несколько эллипсов вокруг центра группы
        n_blobs = 8
        for i in range(n_blobs):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, gr * 0.7)
            bx = gx + dist * math.cos(angle)
            by = gy + dist * math.sin(angle)
            # Размер пятна
            w = gr * random.uniform(0.9, 1.6)
            h = gr * random.uniform(0.9, 1.6)
            rot = random.uniform(0, 180)
            color = random.choice(moss_colors)
            alpha = random.uniform(0.35, 0.6)

            ax.add_patch(Ellipse(
                (bx, by), w, h, angle=rot,
                facecolor=color, edgecolor='none',
                alpha=alpha, zorder=2
            ))

        # Немного тёмных вкраплений
        for _ in range(4):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, gr * 0.8)
            bx = gx + dist * math.cos(angle)
            by = gy + dist * math.sin(angle)
            r = random.uniform(0.08, 0.18)
            ax.add_patch(Circle(
                (bx, by), r,
                facecolor='#3e4a25', edgecolor='none',
                alpha=0.35, zorder=2.1
            ))


def _draw_stone(ax, x, y, radius, base_color, shadow=True, seed=0):
    """
    Реалистичный камень:
    - мягкая тень (несколько слоёв)
    - градиентное тело (несколько концентрических кругов)
    - тёмный контур
    - блик сверху-слева
    - крапинки текстуры
    """
    rng = random.Random(seed)

    # --- ТЕНЬ ---
    if shadow:
        # Смещённая мягкая тень: несколько кругов с растущим радиусом
        for k in range(5, 0, -1):
            alpha = 0.06 + 0.04 * k
            offset = 0.03 + 0.02 * k
            ax.add_patch(Circle(
                (x + offset, y - offset),
                radius * (1 + 0.15 * k / 5),
                facecolor='#3a2f1f', edgecolor='none',
                alpha=alpha, zorder=3
            ))

    # --- ТЕЛО КАМНЯ (градиент) ---
    # Внешний контур — самый тёмный
    ax.add_patch(Circle(
        (x, y), radius,
        facecolor=base_color,
        edgecolor='#2b1f14', linewidth=1.4, zorder=4
    ))

    # Градиент: несколько кругов со смещением к верхнему-левому углу
    n_layers = 8
    for i in range(n_layers):
        t = i / n_layers
        # Смещение к верхнему-левому краю
        cx = x - radius * 0.35 * t
        cy = y + radius * 0.35 * t
        # Радиус уменьшается
        r = radius * (0.92 - 0.75 * t)
        # Цвет светлеет
        light = 1 + 0.35 * t
        c = (
            min(1, base_color[0] * light),
            min(1, base_color[1] * light),
            min(1, base_color[2] * light),
        )
        ax.add_patch(Circle(
            (cx, cy), r,
            facecolor=c, edgecolor='none',
            alpha=0.85, zorder=4.1
        ))

    # --- БЛИК ---
    ax.add_patch(Circle(
        (x - radius * 0.35, y + radius * 0.35),
        radius * 0.22,
        facecolor='white', edgecolor='none',
        alpha=0.35, zorder=4.2
    ))
    # Маленький яркий блик
    ax.add_patch(Circle(
        (x - radius * 0.42, y + radius * 0.42),
        radius * 0.09,
        facecolor='white', edgecolor='none',
        alpha=0.7, zorder=4.3
    ))

    # --- КРАПИНКИ ТЕКСТУРЫ ---
    n_spots = max(3, int(radius * 12))
    for _ in range(n_spots):
        angle = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(0, radius * 0.85)
        sx = x + dist * math.cos(angle)
        sy = y + dist * math.sin(angle)
        sr = rng.uniform(0.01, 0.03)
        # Тёмные вкрапления
        ax.add_patch(Circle(
            (sx, sy), sr,
            facecolor='#1a1208', edgecolor='none',
            alpha=rng.uniform(0.15, 0.4), zorder=4.4
        ))
    # Светлые вкрапления
    for _ in range(n_spots // 2):
        angle = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(0, radius * 0.7)
        sx = x + dist * math.cos(angle)
        sy = y + dist * math.sin(angle)
        sr = rng.uniform(0.008, 0.02)
        ax.add_patch(Circle(
            (sx, sy), sr,
            facecolor='#f5e6c8', edgecolor='none',
            alpha=rng.uniform(0.2, 0.5), zorder=4.4
        ))


def _draw_golden_grid(ax, width, height):
    """Золотая сетка — для архитекторов."""
    for i in range(1, 5):
        x = width * (1 / PHI) ** i
        y = height * (1 / PHI) ** i
        for xx in (x, width - x):
            ax.axvline(xx, color='#c94f2c', linestyle='--',
                       linewidth=0.7, alpha=0.4, zorder=10)
        for yy in (y, height - y):
            ax.axhline(yy, color='#c94f2c', linestyle='--',
                       linewidth=0.7, alpha=0.4, zorder=10)
    # Подписи долей
    ax.text(width * 0.382, -0.4, "0.382·W", color='#c94f2c',
            fontsize=7, ha='center', zorder=10)
    ax.text(width * 0.618, -0.4, "0.618·W", color='#c94f2c',
            fontsize=7, ha='center', zorder=10)


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ ОТРИСОВКИ
# ============================================================

def draw_garden(stones, width, height, title_extra="",
                save_path=None, show_golden_grid=False):
    """
    Рисует реалистичный сад.
    show_golden_grid: True — рисует золотую сетку поверх.
    """
    fig, ax = plt.subplots(figsize=(11, 11 / PHI))
    fig.patch.set_facecolor('#1e1e1e')
    ax.set_facecolor('#e8dcc4')
    ax.set_xlim(-0.5, width + 0.5)
    ax.set_ylim(-0.5, height + 0.5)
    ax.set_aspect('equal')

    # 1. Песок + градиент
    _draw_sand_base(ax, width, height)

    # 2. Бороздки граблями
    _draw_rake_pattern(ax, width, height, seed=42)

    # 3. Мох вокруг групп
    zones = compute_group_zones(stones)
    _draw_moss_zones(ax, zones, seed=7)

    # 4. Камни с градиентом, тенью, бликом
    n_groups = len(set(s['group'] for s in stones))
    for idx, s in enumerate(stones):
        # Базовый цвет зависит от группы (чуть разные оттенки серого)
        t = s['group'] / max(n_groups - 1, 1)
        base = (
            0.42 + 0.12 * t,
            0.38 + 0.10 * t,
            0.32 + 0.08 * t,
        )
        _draw_stone(
            ax, s['x'], s['y'], s['radius'],
            base_color=base,
            shadow=True,
            seed=idx * 13 + 7
        )

    # 5. Золотая сетка (опционально)
    if show_golden_grid:
        _draw_golden_grid(ax, width, height)

    # 6. Заголовок
    grid_note = "  •  сетка φ" if show_golden_grid else ""
    ax.set_title(
        f"Сад Рёандзи — {len(stones)} камней\n{title_extra}{grid_note}",
        color='#f5e6c8', fontsize=13, pad=15
    )
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor('#5c4033')
        spine.set_linewidth(2)

    plt.tight_layout()

    if save_path:
        try:
            plt.savefig(save_path, dpi=150,
                        facecolor=fig.get_facecolor(),
                        bbox_inches='tight')
            print(f"✓ Сохранено: {save_path}")
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")

    plt.show()
    plt.close(fig)