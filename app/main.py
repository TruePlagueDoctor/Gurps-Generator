import random
from dataclasses import dataclass, field
from typing import List, Literal

import tkinter as tk
from tkinter import ttk, messagebox


Tag = Literal["mundane", "super", "supernatural"]


# ==== МОДЕЛИ ДАННЫХ ==== #

@dataclass
class Advantage:
    name: str
    cost: int
    tags: List[Tag]
    min_tl: int = 0
    max_tl: int = 12


@dataclass
class Disadvantage:
    name: str
    cost: int  # отрицательное число
    tags: List[Tag]
    min_tl: int = 0
    max_tl: int = 12


@dataclass
class Skill:
    name: str
    base_attr: str  # "ST", "DX", "IQ", "HT"
    difficulty: Literal["E", "A", "H", "VH"]
    tags: List[Tag]
    min_tl: int = 0
    max_tl: int = 12
    points: int = 0

    # НОВОЕ:
    categories: List[str] = field(default_factory=list)  # тип навыка
    base_weight: int = 1  # базовый "вес" при выборе


@dataclass
class Character:
    name: str = "Генерик"
    tl: int = 3
    total_points: int = 100

    ST: int = 10
    DX: int = 10
    IQ: int = 10
    HT: int = 10

    advantages: List[Advantage] = field(default_factory=list)
    disadvantages: List[Disadvantage] = field(default_factory=list)
    skills: List[Skill] = field(default_factory=list)

    points_spent: int = 0

    def remaining_points(self) -> int:
        return self.total_points - self.points_spent


# ==== УПРОЩЁННЫЕ ТАБЛИЦЫ ==== #

ADVANTAGES: List[Advantage] = [
    Advantage("Хорошее здоровье (Fit)", 5, ["mundane"]),
    Advantage("Боевой рефлекс", 15, ["mundane"]),
    Advantage("Везучий", 10, ["mundane"]),
    Advantage("Магия 1", 15, ["supernatural"]),
    Advantage("Телепатия 1", 15, ["super"]),
]

DISADVANTAGES: List[Disadvantage] = [
    Disadvantage("Хромота", -10, ["mundane"]),
    Disadvantage("Кодекс чести", -10, ["mundane"]),
    Disadvantage("Страх темноты", -5, ["mundane"]),
    Disadvantage("Проклят", -15, ["supernatural"]),
]

SKILLS: List[Skill] = [
    # ==== БЛИЖНИЙ БОЙ (исторические клинки) ====
    Skill("Короткий меч", "DX", "A", ["mundane"],
          min_tl=1, max_tl=6,
          categories=["melee_blade_old"], base_weight=3),
    Skill("Палаш / Шпага", "DX", "A", ["mundane"],
          min_tl=3, max_tl=7,
          categories=["melee_blade_old"], base_weight=3),
    Skill("Рапира", "DX", "A", ["mundane"],
          min_tl=3, max_tl=7,
          categories=["melee_blade_old"], base_weight=2),
    Skill("Сабля", "DX", "A", ["mundane"],
          min_tl=3, max_tl=7,
          categories=["melee_blade_old"], base_weight=2),

    # ==== БЛИЖНИЙ БОЙ (универсальный) ====
    Skill("Драка (Brawling)", "DX", "E", ["mundane"],
          categories=["melee_unarmed"], base_weight=4),
    Skill("Борьба (Wrestling)", "DX", "A", ["mundane"],
          categories=["melee_unarmed"], base_weight=3),
    Skill("Judo", "DX", "H", ["mundane"],
          categories=["melee_unarmed"], base_weight=2),
    Skill("Нож (Knife)", "DX", "E", ["mundane"],
          categories=["melee_knife"], base_weight=3),

    # ==== ДАЛЬНИЙ БОЙ — ЛУКИ / АРБАЛЕТЫ ====
    Skill("Лук (Bow)", "DX", "A", ["mundane"],
          min_tl=1, max_tl=8,
          categories=["ranged_bow"], base_weight=3),
    Skill("Арбалет (Crossbow)", "DX", "E", ["mundane"],
          min_tl=2, max_tl=7,
          categories=["ranged_bow"], base_weight=2),

    # ==== ДАЛЬНИЙ БОЙ — ОГНЕСТРЕЛ ====
    Skill("Пистолеты (Guns/Pistol)", "DX", "E", ["mundane"],
          min_tl=5,
          categories=["ranged_firearm"], base_weight=4),
    Skill("Винтовки (Guns/Rifle)", "DX", "E", ["mundane"],
          min_tl=5,
          categories=["ranged_firearm"], base_weight=4),
    Skill("Автоматы (Guns/SMG)", "DX", "E", ["mundane"],
          min_tl=6,
          categories=["ranged_firearm"], base_weight=3),

    # ==== ОБЩИЕ ПОЛЕЗНЫЕ ====
    Skill("Скрытность (Stealth)", "DX", "A", ["mundane"],
          categories=["stealth"], base_weight=3),
    Skill("Взлом (Lockpicking)", "IQ", "A", ["mundane"],
          min_tl=4,
          categories=["tech"], base_weight=3),
    Skill("Первая помощь (First Aid)", "IQ", "E", ["mundane"],
          categories=["med"], base_weight=3),

    # ==== СВЕРХЪЕСТЕСТВЕННОЕ ====
    Skill("Заклинания (общие)", "IQ", "H", ["supernatural"],
          categories=["magic"], base_weight=4),
    Skill("Пси-атака", "IQ", "H", ["super"],
          categories=["psi"], base_weight=3),
]



# ==== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ГЕНЕРАЦИИ ==== #

def filter_by_options(items, tl: int, allow_super: bool, allow_supernatural: bool):
    """Фильтр по TL и тегам."""
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


def increase_attribute_randomly(char: Character, budget: int) -> int:
    """
    Простейшее распределение очков по атрибутам.
    Допустим: ST/HT +10 очков за +1, DX/IQ +20 за +1.
    """
    costs = {"ST": 10, "DX": 20, "IQ": 20, "HT": 10}
    spent = 0
    attrs = ["ST", "DX", "IQ", "HT"]

    target_spend = int(budget * random.uniform(0.3, 0.5))

    while spent < target_spend:
        attr = random.choice(attrs)
        cost = costs[attr]
        if spent + cost > budget:
            break
        if getattr(char, attr) >= 14:
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


def pick_random_skills(char: Character, tl: int, allow_super: bool,
                       allow_supernatural: bool, budget: int) -> int:
    pool = filter_by_options(SKILLS, tl, allow_super, allow_supernatural)
    if not pool:
        return 0

    # Считаем веса для каждого навыка в пуле
    weights = [get_skill_weight(s, tl) for s in pool]

    spent = 0

    # Чтобы не зациклиться: ограничим количество итераций
    max_iterations = len(pool) * 3

    for _ in range(max_iterations):
        if spent >= budget:
            break
        if not pool:
            break

        # Выбираем один навык с учётом весов
        skill_template = random.choices(pool, weights=weights, k=1)[0]

        # Ищем ему индекс, чтобы можно было при необходимости удалить
        idx = pool.index(skill_template)

        # Создаём копию
        skill = Skill(
            name=skill_template.name,
            base_attr=skill_template.base_attr,
            difficulty=skill_template.difficulty,
            tags=skill_template.tags,
            min_tl=skill_template.min_tl,
            max_tl=skill_template.max_tl,
            points=0,
            base_weight=skill_template.base_weight,
        )

        # Сколько очков вложим в этот навык
        pts = random.choice([1, 2, 4])
        if spent + pts > budget:
            # если не влезает, выбрасываем этот навык из пула
            pool.pop(idx)
            weights.pop(idx)
            continue

        # Не хотим дубликатов навыков
        if any(s.name == skill.name for s in char.skills):
            # уже есть — тоже удаляем из пула, чтобы не пытаться ещё раз
            pool.pop(idx)
            weights.pop(idx)
            continue

        skill.points = pts
        char.skills.append(skill)
        spent += pts

        # Убираем навык из пула, чтобы не добавлять ещё раз
        pool.pop(idx)
        weights.pop(idx)

    return spent



def generate_character(
    total_points: int,
    tl: int,
    allow_super: bool,
    allow_supernatural: bool,
    name: str = "Безымянный",
) -> Character:
    char = Character(name=name, tl=tl, total_points=total_points)

    # 1. Атрибуты
    attr_budget = int(total_points * 0.4)
    spent_attrs = increase_attribute_randomly(char, attr_budget)
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
        char, tl, allow_super, allow_supernatural, skills_budget
    )
    char.points_spent += spent_skills

    return char


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
            lines.append(f"  {s.name} ({s.base_attr}, {s.difficulty}) — {s.points} очк.")
    else:
        lines.append("  —")

    lines.append("=" * 40)
    return "\n".join(lines)


def get_skill_weight(skill: Skill, tl: int) -> int:
    """
    Возвращает эффективный вес навыка для данного TL.
    Основано на categories: melee_blade_old, melee_unarmed, ranged_bow, ranged_firearm и т.д.
    """
    w = skill.base_weight
    cats = set(skill.categories)

    # Исторические клинки — круто на низких TL, почти редкость на TL 8
    if "melee_blade_old" in cats:
        if tl <= 4:
            w *= 3
        elif tl <= 6:
            w *= 1
        else:  # TL 7+
            w = max(1, w // 3)

    # Драка/борьба — актуальны всегда
    if "melee_unarmed" in cats:
        # Можно слегка бустить, чтобы чаще выпадали
        w *= 2

    # Нож — полезен на всех TL, но особенно в современности/уличных сеттингах
    if "melee_knife" in cats:
        if tl >= 5:
            w *= 2

    # Луки/арбалеты — более важны на низких TL
    if "ranged_bow" in cats:
        if tl <= 3:
            w *= 3
        elif tl <= 5:
            w *= 2
        else:
            w = max(1, w // 2)

    # Огнестрел — становится мастхэв начиная с TL 5+
    if "ranged_firearm" in cats:
        if tl >= 5:
            w *= 3
        else:
            w = max(1, w // 3)

    # Магия/пси можно вообще не связывать с TL,
    # а крутить отдельно "жанром" кампании, если такое поле появится.
    return max(w, 1)


# ==== TKINTER GUI ==== #

class GurpsGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("GURPS генератор персонажа")
        self.geometry("800x600")

        # Основной фрейм параметров
        params_frame = ttk.LabelFrame(self, text="Параметры генерации")
        params_frame.pack(fill="x", padx=10, pady=10)

        # Имя
        ttk.Label(params_frame, text="Имя персонажа:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_var = tk.StringVar(value="Безымянный")
        ttk.Entry(params_frame, textvariable=self.name_var, width=25).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Очки
        ttk.Label(params_frame, text="Очки персонажа:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.points_var = tk.StringVar(value="100")
        ttk.Entry(params_frame, textvariable=self.points_var, width=10).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # TL
        ttk.Label(params_frame, text="Технический уровень (TL):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.tl_var = tk.StringVar(value="3")
        ttk.Entry(params_frame, textvariable=self.tl_var, width=10).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Чекбоксы
        self.allow_super_var = tk.BooleanVar(value=False)
        self.allow_supernatural_var = tk.BooleanVar(value=False)

        ttk.Checkbutton(
            params_frame,
            text="Разрешить суперспособности",
            variable=self.allow_super_var,
        ).grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=2)

        ttk.Checkbutton(
            params_frame,
            text="Разрешить сверхъестественные черты/магия",
            variable=self.allow_supernatural_var,
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=2)

        # Кнопка генерации
        generate_button = ttk.Button(params_frame, text="Сгенерировать персонажа",
                                     command=self.on_generate)
        generate_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Растягивание по сетке
        for i in range(2):
            params_frame.columnconfigure(i, weight=1)

        # Поле вывода листа персонажа
        output_frame = ttk.LabelFrame(self, text="Лист персонажа")
        output_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.output_text = tk.Text(output_frame, wrap="word", font=("Consolas", 10))
        self.output_text.pack(fill="both", expand=True, side="left")

        # Скроллбар
        scrollbar = ttk.Scrollbar(output_frame, command=self.output_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.output_text.configure(yscrollcommand=scrollbar.set)

    def on_generate(self):
        """Обработчик кнопки 'Сгенерировать персонажа'."""
        try:
            total_points = int(self.points_var.get())
            tl = int(self.tl_var.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Очки персонажа и TL должны быть целыми числами.")
            return

        if total_points <= 0:
            messagebox.showerror("Ошибка", "Количество очков должно быть больше нуля.")
            return

        name = self.name_var.get().strip() or "Безымянный"
        allow_super = self.allow_super_var.get()
        allow_supernatural = self.allow_supernatural_var.get()

        char = generate_character(
            total_points=total_points,
            tl=tl,
            allow_super=allow_super,
            allow_supernatural=allow_supernatural,
            name=name,
        )

        sheet = format_character(char)

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, sheet)


if __name__ == "__main__":
    app = GurpsGeneratorApp()
    app.mainloop()
