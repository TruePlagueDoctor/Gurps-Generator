import re
from pathlib import Path


# === Маппинги сокращений -> GURPS-атрибуты и сложности ===

ATTR_MAP = {
    "ЛВ": "DX",      # Ловкость
    "ИН": "IQ",      # Интеллект
    "ЗД": "HT",      # Здоровье
    "Воля": "Will",  # Воля
    "Восп": "Per",   # Восприятие
    "ИН/ЛВ": "IQ",   # проф/хобби: берём IQ как базовое
}

DIFF_MAP = {
    "Л": "E",        # Лёгкое
    "С": "A",        # Среднее
    "Т": "H",        # Трудное
    "ОТ": "VH",      # Очень трудное
    "Разл.": "A",    # «Различная сложность» — считаем как среднюю
}

# Ищем кусок вида "ИН С" / "ЛВ Т" / "Воля Т" и т.п.
ATTR_DIFF_RE = re.compile(
    r"\b(ЛВ|ИН|ЗД|Воля|Восп|ИН/ЛВ)\s+(Л|С|Т|ОТ|Разл\.)\b"
)


def is_english_token(tok: str) -> bool:
    """Признак английского токена (для отрезания оригинального имени)."""
    return re.search(r"[A-Za-z]", tok) is not None


def parse_skills(raw_text: str):
    """
    Парсим твой skills_raw.txt:
    - выдёргиваем русское имя
    - определяем базовый атрибут и сложность
    """
    skills = []

    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("умение") or line.startswith("Skill"):
            continue

        m = ATTR_DIFF_RE.search(line)
        if not m:
            # Скорее всего продолжение строки "по умолчанию" — пропускаем
            continue

        attr_code = m.group(1)
        diff_code = m.group(2)

        base_attr = ATTR_MAP.get(attr_code)
        difficulty = DIFF_MAP.get(diff_code)
        if base_attr is None or difficulty is None:
            continue

        left = line[:m.start()].strip()
        tokens = left.split()

        # Убираем крестики "†"
        tokens = [t for t in tokens if t != "†"]

        # Русское имя — всё до первого английского токена
        name_tokens = []
        for t in tokens:
            if is_english_token(t):
                break
            name_tokens.append(t)

        if not name_tokens:
            # На всякий случай — хотя бы что-то
            name_tokens = [tokens[0]]

        name = " ".join(name_tokens)
        skills.append((name, base_attr, difficulty))

    return skills


# === Определяем категории и TL по имени ===

def classify_categories(name: str):
    """
    Присваиваем категории по ключевым словам.
    Это приближённо, но близко к канону GURPS.
    """
    n = name.lower()
    cats = []

    # Ближний бой — клинки, топоры, булавы, посохи
    if any(w in n for w in ["меч", "сабля", "рапира", "шпага", "палаша", "палаш",
                            "топор", "булава", "дубина", "цеп", "посох", "копье",
                            "пика", "тонфа", "дага", "нож", "кинжал", "smallsword",
                            "broadsword", "rapier", "saber", "axe/mace", "staff"]):
        cats.append("melee_blade")

    # Рукопашка / борьба / единоборства
    if any(w in n for w in ["драка", "борьба", "дзюдо", "дзитте", "сумо",
                            "каратэ", "боевое единоборство", "combat", "boxing",
                            "wrestling", "judo"]):
        cats.append("melee_unarmed")

    # Метательное и дистанционное древнее оружие
    if any(w in n for w in ["лук", "арбалет", "праща", "лассо", "копьеметалка",
                            "духовая трубка", "blowpipe", "sling", "bow", "crossbow"]):
        cats.append("ranged_primitive")

    # Огнестрел и тяжёлое оружие
    if any(w in n for w in ["огнестрельное оружие", "guns", "gunner",
                            "тяжелое оружие", "распылители", "liquid projector"]):
        cats.append("firearms")

    # Лучевое/силовое/футуристическое оружие
    if any(w in n for w in ["лучевое", "beam", "силовой меч", "силовой кнут",
                            "мономолекулярный", "monowire"]):
        cats.append("firearms_hi_tech")

    # Навигация, вождение, пилотирование
    if any(w in n for w in ["вождение", "пилотирование", "полет",
                            "подводная лодка", "подводник", "летчик", "малые корабли",
                            "кораблевождение", "pilot", "driving", "boating",
                            "airshipman", "submarine", "submariner"]):
        cats.append("vehicle")

    # Suit'ы, скафандры
    if any(w in n for w in ["скафандр", "environment suit", "vacc", "боевой скафандр",
                            "костюм химзащиты", "подводный костюм"]):
        cats.append("protective_suit")

    # Компьютеры / IT
    if any(w in n for w in ["компьютер", "computer", "программирование", "хакер"]):
        cats.append("computer")

    # Электроника / электричество / техника
    if any(w in n for w in ["электрон", "electric", "электрик", "electronics"]):
        cats.append("electronics")

    # Медицина, биология
    if any(w in n for w in ["врачебное дело", "диагностика", "хирургия", "ветеринария",
                            "психология", "фармакология", "физиология", "биология",
                            "анатомия", "алхимия", "poisons", "яд", "pharmacy"]):
        cats.append("medicine")

    # Научные / инженерные
    if any(w in n for w in ["инженерия", "физика", "математика", "геология",
                            "география", "астрономия", "металлургия", "chemistry",
                            "химия"]):
        cats.append("science")

    # Социальные / разговорные / влияние
    if any(w in n for w in ["дипломатия", "политика", "заговаривание зубов",
                            "харизма", "запугивание", "торговое дело", "sex appeal",
                            "выступление", "публичное выступление", "лидерство",
                            "попрошайничество", "хорошие манеры", "savoir-faire",
                            "fast-talk", "diplomacy", "merchant"]):
        cats.append("social")

    # Магия / эзотерика / ритуалы
    if any(w in n for w in ["ритуальная магия", "тауматология", "оккульт",
                            "экзорцизм", "ритуал", "заклинания"]):
        cats.append("magic")

    # Выживание / природа
    if any(w in n for w in ["выживание", "натуралист", "следопыт", "рыбная ловля",
                            "охота", "falconry", "садовод", "сельское хозяйство"]):
        cats.append("survival")

    # Воровство / скрытность
    if any(w in n for w in ["кража", "карманное воровство", "ловкость рук",
                            "скрытность", "маскировка", "замки", "взлом"]):
        cats.append("stealth")

    return cats


def guess_tl(name: str, categories):
    """
    Примерно каноничные TL для GURPS.
    Подход:
      - по умолчанию большинство умений: TL0–8
      - hi-tech/компы/электроника/скафандры: выше TL7
      - огнестрел: с TL4–5
      - транспорт/движки: TL6+
    Это приближённо, но для генератора более чем достаточно.
    """
    n = name.lower()

    # По умолчанию — с каменного века до современности
    min_tl = 0
    max_tl = 8

    # Компьютерные навыки: только TL7+
    if any(c in categories for c in ["computer"]):
        min_tl = 7
        max_tl = 12

    # Электроника, электричество: TL6/7+
    if any(c in categories for c in ["electronics"]):
        min_tl = max(min_tl, 6)
        max_tl = 12

    # Огнестрел
    if any(c in categories for c in ["firearms"]):
        # Порошковое оружие появляется примерно с TL4,
        # но массовое применение и «огнестрельное» в классическом виде — TL4–5
        min_tl = max(min_tl, 4)
        max_tl = 12

    # Лучевое/силовое оружие — явно высокотехнологичное
    if any(c in categories for c in ["firearms_hi_tech"]):
        min_tl = max(min_tl, 9)
        max_tl = 12

    # Транспорт: автомобили, самолёты, лодки с двигателем
    if any(c in categories for c in ["vehicle"]):
        # Управление лошадьми/повозками тоже бывает, но в твоём наборе это уже
        # в основном про технику, так что ставим TL6+
        min_tl = max(min_tl, 6)
        max_tl = 12

    # Скафандры, боевые костюмы и прочие hi-tech костюмы
    if any(c in categories for c in ["protective_suit"]):
        min_tl = max(min_tl, 8)
        max_tl = 12

    # Ультрасовременные науки (физика, биоинженерия и т.п.) — TL6+
    if any(c in categories for c in ["science", "medicine"]):
        min_tl = max(min_tl, 5)
        max_tl = 12

    # Магия не завязана на TL — оставляем 0–8 (сеттинг решает)
    # Социальные, выживание, скрытность — тоже в любом TL

    return min_tl, max_tl


def classify_tags(name: str) -> list[str]:
    """
    Возвращает список тегов для навыка:
      - ["mundane"]         — обычный навык
      - ["supernatural"]    — магия, оккультизм, ритуалы, странная эзотерика
      - ["super"]           — ци-трюки, ки-ай, «супергеройские» штуки

    Этого достаточно, чтобы заработали флаги allow_super / allow_supernatural.
    """
    n = name.lower()

    # Явно магические / оккультные / ритуальные
    magic_keywords = [
        "магия", "тауматология", "ритуальная магия", "ритуальный обряд",
        "ритуал", "заклинан", "экзорцизм", "оккультизм",
        "fortune telling", "предсказание судьбы", "rune", "symbol drawing",
        "странная наука", "weird science",
    ]

    # Ци-приёмы, ки-ай, прочие «кино-» и сверхчеловеческие трюки
    super_keywords = [
        "киай", "kiai",
        "мощный удар", "power blow",
        "смертельный удар", "pressure secrets",
        "парализующий удар", "pressure points",
        "сокрушительный удар", "breaking blow",
        "парящий прыжок", "flying leap",
        "легкий шаг", "light walk",
        "недвижимая стойка", "immovable stance",
        "искусство невидимости", "invisibility art",
        "искусство метания", "throwing art",
        "контроль тела", "body control",
        "управление дыханием", "breath control",
        "ментальная сила", "mental strength",
        "самогипноз", "autohypnosis",
        "ясный сон", "dreaming",
        "body sense", "чувство тела",
    ]

    # Явная магия/ритуалы
    if any(k in n for k in magic_keywords):
        return ["supernatural"]

    # Ци/супертрюки
    if any(k in n for k in super_keywords):
        return ["super"]

    # Всё остальное — обычные навыки
    return ["mundane"]


# === Генерация кода для data_skills.py ===

HEADER = '''from typing import List

from models import Skill


# Сгенерировано convert_skills.py — дальше можно править вручную
SKILLS: List[Skill] = [
'''

FOOTER = ''']
'''


def generate_data_skills_py(skills, output_path: Path):
    lines = [HEADER]

    for name, attr, diff in skills:
        cats = classify_categories(name)
        min_tl, max_tl = guess_tl(name, cats)

        # базовый вес
        base_weight = 1
        if "firearms" in cats or "melee_blade" in cats or "melee_unarmed" in cats:
            base_weight = 3
        if "computer" in cats or "electronics" in cats or "science" in cats:
            base_weight = 2

        cats_repr = "[" + ", ".join(f'"{c}"' for c in cats) + "]"

        tags = classify_tags(name)
        tags_repr = "[" + ", ".join(f'"{t}"' for t in tags) + "]"

        line = (
            f'    Skill('
            f'name="{name}", '
            f'base_attr="{attr}", '
            f'difficulty="{diff}", '
            f'tags={tags_repr}, '
            f'min_tl={min_tl}, max_tl={max_tl}, '
            f'points=0, '
            f'categories={cats_repr}, '
            f'base_weight={base_weight}'
            f'),\n'
        )

        lines.append(line)

    lines.append(FOOTER)
    output_path.write_text("".join(lines), encoding="utf-8")
    print(f"[OK] Сгенерирован {output_path}")


def main():
    raw_path = Path("skills_raw.txt")
    if not raw_path.exists():
        print("Не найден файл skills_raw.txt. Положи туда исходный текст таблицы.")
        return

    raw_text = raw_path.read_text(encoding="utf-8")
    skills = parse_skills(raw_text)

    # Можно минимально подчистить дубликаты и «чисто английские» записи
    cleaned = []
    seen_names = set()
    for name, attr, diff in skills:
        # убираем чисто английские имена, если у нас уже есть русская версия с тем же смыслом
        if re.search(r"[A-Za-z]", name) and not re.search(r"[А-Яа-яЁё]", name):
            continue
        if name in seen_names:
            continue
        seen_names.add(name)
        cleaned.append((name, attr, diff))

    print(f"Найдено умений после очистки: {len(cleaned)}")

    out_path = Path("data_skills.py")
    generate_data_skills_py(cleaned, out_path)


if __name__ == "__main__":
    main()
