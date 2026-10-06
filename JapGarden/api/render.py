"""Рендер сада в PNG-байты (headless, без plt.show())."""
import io
import matplotlib
matplotlib.use("Agg")  # важно: до import pyplot
import matplotlib.pyplot as plt

from garden.visualizer import (
    _draw_sand_base, _draw_rake_pattern, _draw_moss_zones,
    _draw_stone, _draw_golden_grid
)
from garden.generator import compute_group_zones
from garden.math_core import PHI


def render_garden_png(stones, width, height, show_golden_grid=False,
                      dpi=150) -> bytes:
    """
    Рисует сад и возвращает PNG в виде байтов.
    Не открывает окно, не трогает файловую систему.
    """
    fig, ax = plt.subplots(figsize=(11, 11 / PHI))
    fig.patch.set_facecolor('#1e1e1e')
    ax.set_facecolor('#e8dcc4')
    ax.set_xlim(-0.5, width + 0.5)
    ax.set_ylim(-0.5, height + 0.5)
    ax.set_aspect('equal')

    # 1. Песок
    _draw_sand_base(ax, width, height)

    # 2. Бороздки
    _draw_rake_pattern(ax, width, height, seed=42)

    # 3. Мох
    zones = compute_group_zones(stones)
    _draw_moss_zones(ax, zones, seed=7)

    # 4. Камни
    n_groups = len(set(s['group'] for s in stones))
    for idx, s in enumerate(stones):
        t = s['group'] / max(n_groups - 1, 1)
        base = (0.42 + 0.12 * t, 0.38 + 0.10 * t, 0.32 + 0.08 * t)
        _draw_stone(ax, s['x'], s['y'], s['radius'],
                    base_color=base, shadow=True, seed=idx * 13 + 7)

    # 5. Золотая сетка
    if show_golden_grid:
        _draw_golden_grid(ax, width, height)

    # Заголовок и оформление
    grid_note = "  •  сетка φ" if show_golden_grid else ""
    ax.set_title(
        f"Сад Рёандзи — {len(stones)} камней{grid_note}",
        color='#f5e6c8', fontsize=13, pad=15
    )
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor('#5c4033')
        spine.set_linewidth(2)

    plt.tight_layout()

    # В байты
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=dpi,
                facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf.read()