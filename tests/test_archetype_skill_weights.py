import pytest

from app.models import Skill
from app.generator import get_skill_weight



def make_skill(categories, base_weight=1):
    return Skill(
        name="Тестовый навык",
        base_attr="DX",
        difficulty="A",
        tags=["mundane"],
        min_tl=0,
        max_tl=12,
        points=0,
        categories=categories,
        base_weight=base_weight,
    )


def test_warrior_prefers_melee_over_scholar():
    tl = 3
    sword_skill = make_skill(categories=["melee_blade"])

    w_warrior = get_skill_weight(sword_skill, tl=tl, archetype="warrior")
    w_scholar = get_skill_weight(sword_skill, tl=tl, archetype="scholar")

    assert w_warrior > w_scholar


def test_scholar_prefers_science():
    tl = 8
    science_skill = make_skill(categories=["science"])

    w_scholar = get_skill_weight(science_skill, tl=tl, archetype="scholar")
    w_warrior = get_skill_weight(science_skill, tl=tl, archetype="warrior")

    assert w_scholar > w_warrior


def test_negotiator_prefers_social():
    tl = 8
    social_skill = make_skill(categories=["social"])

    w_negotiator = get_skill_weight(social_skill, tl=tl, archetype="negotiator")
    w_warrior = get_skill_weight(social_skill, tl=tl, archetype="warrior")

    assert w_negotiator > w_warrior
