import random
from typing import List

from app.models import Character, Skill
from app.data_traits import ADVANTAGES, DISADVANTAGES
from app.data_skills import SKILLS
from app.archetypes import Archetype, ARCHETYPE_ATTR_WEIGHTS, ARCHETYPE_CATEGORY_WEIGHTS


def filter_by_options(items: List, tl: int, allow_super: bool, allow_supernatural: bool):
    """Фильтр по TL и GURPS-тегам (mundane/super/supernatural)."""
    result = []
    for item in items:
        if not (item.min_tl <= tl <= item.max_tl):
            continue
        tags = set(item.tags)
        if "super" in tags and not allow_super:
            continue
        if "supernatural" in tags and not allow_supernatural:
            continue
        result.append(item)
    return result


def increase_attribute_randomly(char: Character, budget: int, archetype: Archetype) -> int:
    costs = {
        "ST": 10, "DX": 20, "IQ": 20, "HT": 10,
        "Will": 5, "Per": 5,
    }
    attrs = list(costs.keys())
    weights_cfg = ARCHETYPE_ATTR_WEIGHTS.get(archetype, ARCHETYPE_ATTR_WEIGHTS["generalist"])

    spent = 0
    target_spend = int(budget * random.uniform(0.3, 0.5))

    while spent < target_spend:
        # выбор атрибута с учётом архетипа
        weights = [weights_cfg.get(a, 1) for a in attrs]
        attr = random.choices(attrs, weights=weights, k=1)[0]

        cost = costs[attr]
        if spent + cost > budget:
            break
        if getattr(char, attr) >= 16:
            continue

        setattr(char, attr, getattr(char, attr) + 1)
        spent += cost

    return spent



def pick_random_advantages(char: Character, tl: int, allow_super: bool,
                           allow_supernatural: bool, budget: int) -> int:
    pool = filter_by_options(ADVANTAGES, tl, allow_super, allow_supernatural)
    random.shuffle(pool)
    spent = 0

    for adv in pool:
        if spent + adv.cost > budget:
            continue
        if adv.name in (a.name for a in char.advantages):
            continue
        char.advantages.append(adv)
        spent += adv.cost

    return spent


def pick_random_disadvantages(char: Character, tl: int, allow_super: bool,
                              allow_supernatural: bool, min_negative_points: int) -> int:
    """
    Набираем недостатков до (по модулю) некоторого лимита.
    Возвращает суммарные ОТРИЦАТЕЛЬНЫЕ очки (например -40).
    """
    pool = filter_by_options(DISADVANTAGES, tl, allow_super, allow_supernatural)
    random.shuffle(pool)
    total_negative = 0

    for dis in pool:
        if abs(total_negative + dis.cost) > abs(min_negative_points):
            continue
        if dis.name in (d.name for d in char.disadvantages):
            continue
        char.disadvantages.append(dis)
        total_negative += dis.cost

    return total_negative


def get_skill_weight(skill: Skill, tl: int, archetype: Archetype | None = None) -> int:
    """
    Возвращает эффективный вес навыка для данного TL.
    Если TL персонажа вне диапазона min_tl..max_tl навыка — вес = 0.
    Основано на категориях:
      melee_blade, melee_unarmed, ranged_primitive, firearms,
      firearms_hi_tech, vehicle, protective_suit, computer, electronics,
      medicine, science, social, magic, survival, stealth.
    """

    # Жёсткий срез по TL: этот навык недоступен вообще
    if tl < skill.min_tl or tl > skill.max_tl:
        return 0

    w = skill.base_weight
    cats = set(skill.categories)

    # === БЛИЖНИЙ БОЙ ===
    if "melee_unarmed" in cats:
        w *= 2  # рукопашка всегда актуальна

    if "melee_blade" in cats:
        if tl <= 3:
            w *= 3
        elif tl <= 5:
            w *= 2
        else:
            w = max(1, w // 2)

    # === ДИСТАНЦИОННОЕ ОРУЖИЕ ===
    if "ranged_primitive" in cats:
        if tl <= 3:
            w *= 3
        elif tl <= 5:
            w *= 2
        else:
            w = max(1, w // 2)

    if "firearms" in cats:
        if tl >= 5:
            w *= 3
        else:
            w = max(1, w // 3)

    if "firearms_hi_tech" in cats:
        if tl >= 9:
            w *= 4
        else:
            w = max(1, w // 4)

    # === ТРАНСПОРТ / СНАРЯГА ===
    if "vehicle" in cats:
        if tl >= 6:
            w *= 2
        else:
            w = max(1, w // 2)

    if "protective_suit" in cats:
        if tl >= 8:
            w *= 3
        else:
            w = max(1, w // 3)

    # === HI-TECH ===
    if "computer" in cats:
        if tl >= 7:
            w *= 4
        else:
            w = max(1, w // 3)

    if "electronics" in cats:
        if tl >= 6:
            w *= 3
        else:
            w = max(1, w // 2)

    # === НАУКА / МЕД ===
    if "science" in cats:
        if tl >= 5:
            w *= 2

    if "medicine" in cats:
        if tl >= 6:
            w *= 2

    # === СОЦИАЛКА / СТЕЛС / ВЫЖИВАНИЕ / МАГИЯ ===
    if "social" in cats:
        w *= 2

    if "survival" in cats:
        if tl <= 4:
            w *= 2

    if "stealth" in cats:
        w *= 2

    if "magic" in cats:
        if tl <= 4:
            w *= 3
        else:
            w *= 2

    if archetype:
        arch_cfg = ARCHETYPE_CATEGORY_WEIGHTS.get(archetype, {})
        # берём максимальный множитель среди категорий навыка
        mult = 1
        for c in cats:
            mult = max(mult, arch_cfg.get(c, 1))
        w *= mult


    return max(w, 0)



def pick_random_skills(char: Character, tl: int, allow_super: bool,
                       allow_supernatural: bool, budget: int,
                       archetype: Archetype) -> int:
    pool = filter_by_options(SKILLS, tl, allow_super, allow_supernatural)
    if not pool:
        return 0

    weights = [get_skill_weight(s, tl, archetype) for s in pool]
    pool = [s for s, w in zip(pool, weights) if w > 0]
    weights = [w for w in weights if w > 0]

    if not pool:
        return 0

    spent = 0
    max_iterations = len(pool) * 3

    for _ in range(max_iterations):
        if spent >= budget or not pool:
            break

        skill_template = random.choices(pool, weights=weights, k=1)[0]
        idx = pool.index(skill_template)

        skill = Skill(
            name=skill_template.name,
            base_attr=skill_template.base_attr,
            difficulty=skill_template.difficulty,
            tags=skill_template.tags,
            min_tl=skill_template.min_tl,
            max_tl=skill_template.max_tl,
            points=0,
            categories=list(skill_template.categories),
            base_weight=skill_template.base_weight,
        )

        pts = random.choice([1, 2, 4])
        if spent + pts > budget:
            pool.pop(idx)
            weights.pop(idx)
            continue

        if any(s.name == skill.name for s in char.skills):
            pool.pop(idx)
            weights.pop(idx)
            continue

        skill.points = pts
        char.skills.append(skill)
        spent += pts

        pool.pop(idx)
        weights.pop(idx)

    return spent


def generate_character(
    total_points: int,
    tl: int,
    allow_super: bool,
    allow_supernatural: bool,
    name: str = "Безымянный",
    archetype: Archetype = "generalist",
) -> Character:
    char = Character(name=name, tl=tl, total_points=total_points, archetype=archetype)

    # Will и Per базово равны IQ
    char.Will = char.IQ
    char.Per = char.IQ

    # 1. Атрибуты
    attr_budget = int(total_points * 0.4)
    spent_attrs = increase_attribute_randomly(char, attr_budget, archetype)
    char.points_spent += spent_attrs

    # 2. Недостатки
    max_disads = int(-total_points * 0.4)
    negative_from_disads = pick_random_disadvantages(
        char, tl, allow_super, allow_supernatural, max_disads
    )
    char.points_spent += negative_from_disads

    # 3. Преимущества
    adv_budget = int(total_points * 0.3)
    spent_adv = pick_random_advantages(
        char, tl, allow_super, allow_supernatural, adv_budget
    )
    char.points_spent += spent_adv

    # 4. Навыки
    skills_budget = max(0, int((total_points - char.points_spent) * 0.7))
    spent_skills = pick_random_skills(
        char, tl, allow_super, allow_supernatural, skills_budget, archetype
    )
    char.points_spent += spent_skills

    # 5. Дожиг очков (можно при желании тоже адаптировать под архетип)
    spend_remaining_points(char, tl, allow_super, allow_supernatural)

    return char



def compute_skill_level(skill: Skill, char: Character) -> int:
    """
    Считает уровень навыка по GURPS-подобной схеме с плато:

    E:
        1     -> Attr
        2–3   -> Attr+1
        4–7   -> Attr+2
        8–11  -> Attr+3
        12–15 -> Attr+4
        дальше: +1 за каждые 4 очка

    A:
        1     -> Attr-1
        2–3   -> Attr
        4–7   -> Attr+1
        8–11  -> Attr+2
        12–15 -> Attr+3
        дальше: +1 за каждые 4 очка

    H:
        1     -> Attr-2
        2–3   -> Attr-1
        4–7   -> Attr
        8–11  -> Attr+1
        12–15 -> Attr+2
        дальше: +1 за каждые 4 очка

    VH:
        1     -> Attr-3
        2–3   -> Attr-2
        4–7   -> Attr-1
        8–11  -> Attr
        12–15 -> Attr+1
        дальше: +1 за каждые 4 очка
    """
    attr_value = getattr(char, skill.base_attr)
    pts = skill.points

    # На случай, если навыок есть, но очков 0
    if pts <= 0:
        # Очень грубое приближение "по умолчанию"
        return attr_value - 4

    # Таблица порогов: {кол-во очков: относительный уровень к атрибуту}
    tables = {
        "E": {1: 0, 2: 1, 4: 2, 8: 3, 12: 4},
        "A": {1: -1, 2: 0, 4: 1, 8: 2, 12: 3},
        "H": {1: -2, 2: -1, 4: 0, 8: 1, 12: 2},
        "VH": {1: -3, 2: -2, 4: -1, 8: 0, 12: 1},
    }

    diff = skill.difficulty
    if diff not in tables:
        # На всякий случай, если вдруг что-то странное
        diff = "A"

    tbl = tables[diff]
    thresholds = sorted(tbl.keys())

    # Находим наибольший порог, который не превышает pts
    effective_threshold = max(t for t in thresholds if t <= pts)
    rel = tbl[effective_threshold]

    max_threshold = thresholds[-1]

    # Если ещё не достигли максимального порога (12 очков) — дополнительных уровней нет
    if effective_threshold < max_threshold:
        return attr_value + rel

    # Свыше 12 очков: каждые полные 4 дают +1 уровень
    extra_pts = pts - max_threshold
    extra_lvls = extra_pts // 4
    return attr_value + rel + extra_lvls


def spend_remaining_points(
    char: Character,
    tl: int,
    allow_super: bool,
    allow_supernatural: bool,
    max_attr: int = 16,
):
    """
    Пытается максимально потратить оставшиеся очки.
    Алгоритм:
    1) Пока можем, поднимаем характеристики (ST/HT/DX/IQ) в разумных пределах.
    2) Иначе вливаем очки в навыки:
       - если навыков нет — создаём новый из доступных SKILLS с 1 очком
       - иначе добавляем по 1 очку в случайный навык.
    """
    attr_costs = {
        "ST": 10, "DX": 20, "IQ": 20, "HT": 10,
        "Will": 5, "Per": 5,
    }

    safety = 0
    while char.remaining_points() > 0 and safety < 1000:
        safety += 1
        rem = char.remaining_points()

        # 1. Пытаемся поднять какой-нибудь атрибут
        viable_attrs = [
            attr_name
            for attr_name, cost in attr_costs.items()
            if cost <= rem and getattr(char, attr_name) < max_attr
        ]
        if viable_attrs:
            attr = random.choice(viable_attrs)
            cost = attr_costs[attr]
            setattr(char, attr, getattr(char, attr) + 1)
            char.points_spent += cost
            continue

        # 2. Если атрибуты поднять нельзя, работаем с навыками
        if not char.skills:
            # Навыков пока нет — создаём хотя бы один
            pool = filter_by_options(SKILLS, tl, allow_super, allow_supernatural)
            if not pool:
                # Совсем нечего взять — выходим
                break
            tmpl = random.choice(pool)
            new_skill = Skill(
                name=tmpl.name,
                base_attr=tmpl.base_attr,
                difficulty=tmpl.difficulty,
                tags=tmpl.tags,
                min_tl=tmpl.min_tl,
                max_tl=tmpl.max_tl,
                points=0,
                categories=list(tmpl.categories),
                base_weight=tmpl.base_weight,
            )
            char.skills.append(new_skill)

        # Теперь точно есть хотя бы один навык
        if rem < 1:
            break

        skill = random.choice(char.skills)
        skill.points += 1
        char.points_spent += 1

    # На выходе либо очков нет, либо мы упёрлись в какие-то жёсткие ограничения


def format_character(char: Character) -> str:
    """Вернуть лист персонажа как одну строку."""
    lines = []
    lines.append("=" * 40)
    lines.append(f"Имя: {char.name}")
    lines.append(f"TL: {char.tl}")
    lines.append(
        f"Очки: {char.points_spent}/{char.total_points} "
        f"(остаток: {char.remaining_points()})"
    )
    lines.append("-" * 40)
    lines.append(f"ST {char.ST}  DX {char.DX}  IQ {char.IQ}  HT {char.HT}")
    lines.append("-" * 40)
    lines.append(f"Архетип: {char.archetype}")
    lines.append("Преимущества:")
    if char.advantages:
        for a in char.advantages:
            lines.append(f"  {a.name} [{a.cost}]")
    else:
        lines.append("  —")

    lines.append("Недостатки:")
    if char.disadvantages:
        for d in char.disadvantages:
            lines.append(f"  {d.name} [{d.cost}]")
    else:
        lines.append("  —")

    lines.append("Навыки:")
    if char.skills:
        for s in char.skills:
            lvl = compute_skill_level(s, char)
            lines.append(
                f"  {s.name} ({s.base_attr}, {s.difficulty}) — "
                f"{s.points} очк., уровень {lvl}"
            )
    else:
        lines.append("  —")

    lines.append("=" * 40)
    return "\n".join(lines)
