"""Génère la courbe d'XP et les taux de drop des Soleils (voir docs/01-game-design.md §6-7 et docs/05-soleils-lunes.md).

Usage : python3 tools/balance/xp_curve.py

Les valeurs produites sont des valeurs *par défaut* ; en production elles vivent
dans config/balance/*.toml et sont rechargeables côté serveur.
"""
import math

KILLS_PER_HOUR = 720  # farm solo optimal : ~12 monstres normaux / minute


def xp_per_kill(level: int) -> int:
    """XP d'un monstre normal du niveau donné."""
    return round(10 * 1.075 ** (level - 1))


def hours_for_level(level: int) -> float:
    """Temps cible (heures de farm optimal) pour passer de `level` à `level + 1`."""
    if level < 10:
        return 0.05 + (level - 1) * (0.35 / 8)
    if level < 20:
        return 0.5 + (level - 10) * (0.7 / 9)
    if level < 40:
        return 1.5 + (level - 20) * (3.5 / 19)
    if level < 60:
        return 6 + (level - 40) * (9 / 19)
    return 18 * math.exp(math.log(120 / 18) * (level - 60) / 28)


def xp_to_next(level: int) -> int:
    xp = hours_for_level(level) * KILLS_PER_HOUR * xp_per_kill(level)
    return int(round(xp, -1 if level < 20 else -2))


def sun_drop_rate(boss_index: int) -> float:
    """Taux de drop direct du Soleil pour le boss i (0 = niveau 60, 14 = niveau 90)."""
    return 1e-4 * 0.3 ** (boss_index / 14)


def sun_boss_level(boss_index: int) -> int:
    return 60 + round(boss_index * 30 / 14)


if __name__ == "__main__":
    total = 0.0
    print("| Niveau | XP/monstre | XP requise | Temps cible | Cumul |")
    print("|---|---|---|---|---|")
    for lvl in range(1, 90):
        total += hours_for_level(lvl)
        print(f"| {lvl} → {lvl + 1} | {xp_per_kill(lvl)} | {xp_to_next(lvl):,} | "
              f"{hours_for_level(lvl):.2f} h | {total:.0f} h |".replace(",", " "))
    print()
    print("| Boss | Niveau | Taux direct | 1 chance sur |")
    print("|---|---|---|---|")
    for i in range(15):
        p = sun_drop_rate(i)
        print(f"| {i + 1} | {sun_boss_level(i)} | {p * 100:.4f} % | {round(1 / p)} |")
