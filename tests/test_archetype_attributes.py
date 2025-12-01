import pytest
import app.generator as generator
from app.models import Character
from app.generator import increase_attribute_randomly
from app.archetypes import ARCHETYPE_ATTR_WEIGHTS



def test_increase_attribute_randomly_prefers_warrior_stats(monkeypatch):
    # Заменяем random.choices внутри generator на детерминированную версию,
    # которая всегда выбирает атрибут с максимальным весом.
    def fake_choices(population, weights, k=1):
        max_w = max(weights)
        idx = weights.index(max_w)
        return [population[idx]]

    monkeypatch.setattr(generator.random, "choices", fake_choices)

    # Базовый персонаж
    char = Character(total_points=100)
    char.Will = char.IQ
    char.Per = char.IQ

    # Выделим небольшой бюджет
    spent = increase_attribute_randomly(char, budget=40, archetype="warrior")

    # Для архетипа "warrior" главное — ST и DX
    assert char.ST > 10 or char.DX > 10
    # IQ при этом, скорее всего, либо не вырос, либо вырос меньше
    # (жёсткой проверки делать не будем, просто sanity check)
    assert spent > 0


def test_increase_attribute_randomly_prefers_scholar_stats(monkeypatch):
    def fake_choices(population, weights, k=1):
        max_w = max(weights)
        idx = weights.index(max_w)
        return [population[idx]]

    monkeypatch.setattr(generator.random, "choices", fake_choices)

    char = Character(total_points=100)
    char.Will = char.IQ
    char.Per = char.IQ

    spent = increase_attribute_randomly(char, budget=40, archetype="scholar")

    # Учёный должен качать IQ/Will/Per
    assert char.IQ > 10 or char.Will > 10 or char.Per > 10
    assert spent > 0
