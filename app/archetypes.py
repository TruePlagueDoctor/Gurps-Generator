from typing import Literal

Archetype = Literal["generalist", "warrior", "scholar", "negotiator", "scout"]

ARCHETYPE_ATTR_WEIGHTS: dict[Archetype, dict[str, int]] = {
    "generalist": {"ST": 1, "DX": 1, "IQ": 1, "HT": 1, "Will": 1, "Per": 1},
    "warrior":    {"ST": 3, "DX": 3, "IQ": 1, "HT": 2, "Will": 1, "Per": 1},
    "scholar":    {"ST": 1, "DX": 1, "IQ": 3, "HT": 1, "Will": 3, "Per": 2},
    "negotiator": {"ST": 1, "DX": 1, "IQ": 2, "HT": 1, "Will": 3, "Per": 2},
    "scout":      {"ST": 1, "DX": 3, "IQ": 1, "HT": 2, "Will": 1, "Per": 3},
}

ARCHETYPE_CATEGORY_WEIGHTS: dict[Archetype, dict[str, int]] = {
    "generalist": {},
    "warrior": {
        "melee_blade": 3,
        "melee_unarmed": 3,
        "ranged_primitive": 2,
        "firearms": 2,
        "survival": 2,
        "stealth": 2,
    },
    "scholar": {
        "science": 3,
        "medicine": 2,
        "magic": 2,
        "computer": 2,
        "electronics": 2,
    },
    "negotiator": {
        "social": 4,
        "stealth": 2,
        "magic": 1,
    },
    "scout": {
        "stealth": 3,
        "survival": 3,
        "ranged_primitive": 3,
        "firearms": 2,
        "melee_unarmed": 2,
    },
}
