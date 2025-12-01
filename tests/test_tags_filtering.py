import pytest

from app.models import Skill
from app.generator import filter_by_options


def test_filter_block_supernatural_and_super():
    tl = 4

    mundane = Skill(
        name="Повар",
        base_attr="IQ",
        difficulty="A",
        tags=["mundane"],
        min_tl=0,
        max_tl=12,
        points=0,
        categories=["social"],
        base_weight=1,
    )

    magic = Skill(
        name="Тауматология",
        base_attr="IQ",
        difficulty="VH",
        tags=["supernatural"],
        min_tl=0,
        max_tl=12,
        points=0,
        categories=["magic"],
        base_weight=2,
    )

    super_skill = Skill(
        name="Киай",
        base_attr="HT",
        difficulty="H",
        tags=["super"],
        min_tl=0,
        max_tl=12,
        points=0,
        categories=["melee_unarmed"],
        base_weight=2,
    )

    skills = [mundane, magic, super_skill]

    # Магия и суперспособности запрещены
    filtered = filter_by_options(skills, tl=tl, allow_super=False, allow_supernatural=False)
    names = {s.name for s in filtered}
    assert "Повар" in names
    assert "Тауматология" not in names
    assert "Киай" not in names

    # Разрешаем магию, но не суперспособности
    filtered_magic_only = filter_by_options(skills, tl=tl, allow_super=False, allow_supernatural=True)
    names2 = {s.name for s in filtered_magic_only}
    assert "Повар" in names2
    assert "Тауматология" in names2
    assert "Киай" not in names2
