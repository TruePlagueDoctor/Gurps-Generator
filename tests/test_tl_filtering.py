import pytest

from app.models import Skill
from app.generator import get_skill_weight



def test_get_skill_weight_respects_tl():
    # Навык, доступный только с TL 7
    hi_tech_skill = Skill(
        name="Фотографирование",
        base_attr="IQ",
        difficulty="A",
        tags=["mundane"],
        min_tl=7,
        max_tl=12,
        points=0,
        categories=["electronics"],
        base_weight=2,
    )

    # Средневековый персонаж TL 3 — вес должен быть 0
    w_tl3 = get_skill_weight(hi_tech_skill, tl=3)
    assert w_tl3 == 0

    # Современный TL 8 — навык уже возможен и что-то должен весить
    w_tl8 = get_skill_weight(hi_tech_skill, tl=8)
    assert w_tl8 > 0
