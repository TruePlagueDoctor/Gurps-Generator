import random
from dataclasses import dataclass, field
from typing import List, Literal


# Тип для "сеттинговых" тегов
Tag = Literal["mundane", "super", "supernatural"]


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

    # Добавляем "умный" слой:
    categories: List[str] = field(default_factory=list)  # тип навыка (melee_blade_old, etc.)
    base_weight: int = 1  # базовый вес для рандомайзера


@dataclass
class Character:
    name: str = "Генерик"
    tl: int = 3
    total_points: int = 100

    ST: int = 10
    DX: int = 10
    IQ: int = 10
    HT: int = 10

    Will: int = 10   # +0 означает "равно IQ"
    Per: int = 10    # +0 означает "равно IQ"

    archetype: str = "generalist" 

    advantages: List[Advantage] = field(default_factory=list)
    disadvantages: List[Disadvantage] = field(default_factory=list)
    skills: List[Skill] = field(default_factory=list)

    points_spent: int = 0

    def remaining_points(self) -> int:
        return self.total_points - self.points_spent
