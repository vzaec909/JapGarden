"""Валидация распределения камней + предложения по улучшению."""
from .math_core import is_fibonacci, nearest_fibonacci


def validate_group_input(groups):
    """
    Возвращает (status, message, suggestions).
    status: 'ok' | 'warning' | 'suggestion' | 'error'
    """
    n_groups = len(groups)
    total = sum(groups)
    messages = []
    suggestions = []
    status = 'ok'

    if total == 0:
        return 'error', "❌ Не задано ни одного камня.", []

    if total > 40:
        return 'error', (
            f"❌ Слишком много камней: {total}. Максимум — 40.\n"
            f"Классика — 15."
        ), [f"Уменьшите до 15 (Рёандзи) или {nearest_fibonacci(total)} "
            f"(ближайшее Фибоначчи)."]

    if total < 3:
        status = 'warning'
        messages.append(f"⚠️  Всего {total} камня — слишком разреженно. "
                        f"Минимум для выразительной композиции — 3.")

    for i, g in enumerate(groups):
        if g <= 0:
            status = 'error'
            messages.append(f"❌ Группа {i+1}: {g} камней — невозможно.")
            continue
        if g > 7:
            status = 'error'
            messages.append(f"❌ Группа {i+1}: {g} камней. Максимум — 7.")
            suggestions.append(
                f"Разбейте группу {i+1} ({g}) на две: например, "
                f"{g // 2} и {g - g // 2}."
            )
        if g == 1 and n_groups > 3 and status == 'ok':
            status = 'warning'
            messages.append(
                f"⚠️  Группа {i+1}: одиночный камень. "
                f"Символично, но при {n_groups} группах выглядит потерянно."
            )
        if g > 1 and not is_fibonacci(g) and status == 'ok':
            status = 'warning'
            messages.append(
                f"⚠️  Группа {i+1}: {g} — не Фибоначчи "
                f"(ближайшее {nearest_fibonacci(g)})."
            )

    if n_groups not in (3, 5, 7) and status == 'ok':
        status = 'warning'
        messages.append(
            f"⚠️  {n_groups} групп. Классические композиции: 3, 5, 7."
        )
        if n_groups > 7:
            suggestions.append("Объедините до 5 групп (как в Рёандзи).")
        elif n_groups < 3:
            suggestions.append("Добавьте группы до 3 — минимальная композиция.")

    if total > 0 and not is_fibonacci(total) and status == 'ok':
        status = 'suggestion'
        suggestions.append(
            f"💡 Сумма камней = {total}. Ближайшее число Фибоначчи: "
            f"{nearest_fibonacci(total)} — даст более гармоничный ансамбль."
        )

    if n_groups > 1:
        spread = max(groups) - min(groups)
        avg = total / n_groups
        if spread == 0 and n_groups > 2 and status == 'ok':
            status = 'suggestion'
            suggestions.append(
                "💡 Все группы равны — для асимметрии дзен попробуйте "
                "[5, 2, 3, 2, 3]."
            )
        if spread > avg * 1.5 and status == 'ok':
            status = 'warning'
            messages.append(
                f"⚠️  Сильный разброс групп: {min(groups)} … {max(groups)}. "
                f"Одна группа подавляет остальные."
            )

    if groups == [5, 2, 3, 2, 3]:
        messages.append("🌸 Идеально! Классическое распределение сада Рёандзи — "
                        "15 камней в 5 группах.")
        status = 'ok'

    if not messages:
        messages.append("✓ Распределение гармонично.")

    return status, "\n".join(messages), suggestions


def auto_suggest_from_single(n):
    """
    Варианты разбиения N камней. Возвращает список (название, [группы]).
    Все варианты валидны: 1 <= камней в группе <= 7.
    """
    if n <= 0:
        return []

    variants = []
    seen = set()

    def add(name, groups):
        key = tuple(groups)
        if key in seen:
            return
        if sum(groups) != n:
            return
        if any(g <= 0 or g > 7 for g in groups):
            return
        seen.add(key)
        variants.append((name, list(groups)))

    if n == 15:
        add("Классика Рёандзи (5 групп)", [5, 2, 3, 2, 3])

    if n >= 5:
        target = [5, 3, 2, 1, 1]
        candidate = []
        remaining = n
        for i, t in enumerate(target):
            slots_left = len(target) - i - 1
            take = min(t, remaining - slots_left)
            take = max(take, 1)
            candidate.append(take)
            remaining -= take
        if remaining > 0:
            candidate[-1] += remaining
        add("Асимметричное (5 групп)", candidate)

    if n >= 3:
        base = [5, 3, 2]
        if n == 15:
            add("Асимметричное (3 группы)", base)
        elif n > 3:
            total_base = sum(base)
            scaled = [max(1, min(7, round(g * n / total_base))) for g in base]
            diff = n - sum(scaled)
            i = 0
            while diff != 0 and i < 20:
                idx = i % 3
                if diff > 0 and scaled[idx] < 7:
                    scaled[idx] += 1
                    diff -= 1
                elif diff < 0 and scaled[idx] > 1:
                    scaled[idx] -= 1
                    diff += 1
                i += 1
            add("Асимметричное (3 группы)", scaled)

    if n % 5 == 0 and 1 <= n // 5 <= 7:
        add("Равномерное (5 групп)", [n // 5] * 5)
    if n % 3 == 0 and 1 <= n // 3 <= 7:
        add("Равномерное (3 группы)", [n // 3] * 3)
    if n % 7 == 0 and 1 <= n // 7 <= 7:
        add("Равномерное (7 групп)", [n // 7] * 7)

    if n >= 3:
        add("Ядро + 2 одиночки (3 группы)", [n - 2, 1, 1])
    if n >= 5:
        add("Ядро + 4 одиночки (5 групп)", [n - 4, 1, 1, 1, 1])

    if not variants:
        candidate = []
        remaining = n
        while remaining > 0:
            take = min(7, remaining)
            candidate.append(take)
            remaining -= take
        add("Жадное разбиение (по 7)", candidate)

    if not variants:
        candidate = []
        remaining = n
        pattern = [5, 3, 2, 1]
        i = 0
        while remaining > 0:
            take = min(pattern[i % len(pattern)], remaining)
            candidate.append(max(1, take))
            remaining -= take
            i += 1
        add("Разбиение 5-3-2-1", candidate)

    return variants