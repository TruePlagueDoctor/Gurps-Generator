from typing import List

from app.models import Advantage, Disadvantage


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
