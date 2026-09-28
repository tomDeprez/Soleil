# 04 — Runes

## 1. Fonctionnement

- Les objets possèdent 0 à 4 **sockets** (selon la rareté, voir [03](03-loot-objets-fusion.md)).
- Une rune insérée ajoute un **modificateur** (et, à haut niveau, un déclencheur) à l'objet.
- Les runes ont **8 niveaux**. Le niveau augmente la valeur et, aux niveaux 5 et 8, ajoute un effet.
- Retrait : gratuit pour les niveaux 1–4 ; au-delà, coût en poussière runique (évite l'échange gratuit permanent entre builds, mais sans destruction).
- Couleurs de socket : **Rouge** (offensif), **Bleu** (défensif), **Vert** (utilitaire), **Prismatique** (toute rune, rare). Une rune dans un socket de sa couleur gagne +25 %.

## 2. Familles (exemples, 30 familles au lancement)

| Famille | Couleur | Niv. 1 | Niv. 4 | Niv. 5 (effet) | Niv. 8 (effet majeur) |
|---|---|---|---|---|---|
| Rune de Critique | Rouge | +2 % chance crit | +8 % | Les crits génèrent 1 Lumen | Les crits ont 5 % de chance de réinitialiser la recharge la plus courte (ICD 2 s) |
| Rune de Braise | Rouge | +4 % dégâts de Feu | +16 % | Brûlure +20 % durée | Les cibles en Brûlure explosent à la mort (40 % dégâts) |
| Rune de Rempart | Bleu | +3 % armure | +12 % | Bloquer rend 1 % PV | Bouclier de 10 % PV max toutes les 20 s |
| Rune de Vif-argent | Vert | +2 % vitesse de déplacement | +8 % | +1 charge d'esquive | Esquiver laisse un leurre qui provoque 2 s |
| Rune d'Écho | Vert | +2 % réduction de recharge | +8 % | — | 5 % de chance de relancer une compétence (`Déclenché`) |
| Rune de Moisson | Vert | +3 % poussière | +12 % | +1 % Fortune | Les élites lâchent 1 rune supplémentaire (5 %) |

Valeurs par niveau (multiplicateur de la valeur de niv. 1) : 1 ×1, 2 ×1,8, 3 ×2,6, 4 ×4, 5 ×5,5, 6 ×7,5, 7 ×10, 8 ×14.
La croissance est volontairement plus forte en fin d'échelle pour valoriser les runes 7–8.

## 3. Obtention

| Source | Niveaux possibles |
|---|---|
| Monstres normaux (régions 1–4) | 1 |
| Élites / régions 5–6 | 1–2 |
| Boss de région, donjons | 1–3 |
| Boss 60+ | 2–4 |
| Niveaux 5–8 | **Uniquement par fusion** |

## 4. Fusion de runes

```text
4 × Rune de niveau N (même famille) + poussière runique + or  →  1 × Rune de niveau N+1
```

| Fusion | Poussière runique | Réussite | Échec |
|---|---|---|---|
| 1 → 2 | 10 | 100 % | — |
| 2 → 3 | 40 | 100 % | — |
| 3 → 4 | 150 | 100 % | — |
| 4 → 5 | 600 | 100 % | — |
| 5 → 6 | 2 500 | 100 % | — |
| 6 → 7 | 10 000 + 1 Pierre d'Écho (boss 60+) | 100 % | — |
| 7 → 8 | 40 000 + 1 Cœur Runique (boss 75+) | 100 % | — |

Choix de conception : **pas d'échec destructeur**. La lenteur vient du volume (une rune de niveau 8 =
4⁷ = **16 384 runes de niveau 1**) et des composants de boss, pas de la frustration aléatoire.

- **Fusion croisée** : 4 runes de même niveau mais de familles différentes → rune de même niveau d'une famille aléatoire (permet de recycler les familles inutiles).
- **Transmutation** : changer la famille d'une rune coûte 1 rune de même niveau + poussière (ciblage tardif, cher).
- Garde-fou d'équilibrage : le niveau de rune insérable est plafonné par le niveau de l'objet (ilvl 60+ pour le niveau 7, ilvl 80+ pour le niveau 8).

## 5. Stockage et données

Les runes sont empilables : on ne stocke pas 16 000 lignes mais un **compteur** par (famille, niveau).

```text
rune_stack   (character_id, family_id, level, quantity)         -- runes libres
item_socket  (item_id, socket_index, color, rune_family_id?, rune_level?)
```

Fusion en masse : « fusionner tout jusqu'au niveau N » est une seule requête serveur (transaction unique, calcul arithmétique sur les compteurs).

## 6. Interactions

- Les runes produisent des `Modifier`/`Trigger` du même format que tous les autres systèmes ([02 §6](02-classe-evolutions-competences.md)).
- Certains Soleils agissent sur les runes (ex. « les runes Rouges comptent comme Prismatiques »).
- Certaines Lunes amplifient une couleur de socket selon leur phase.
- Classement de collection : familles × niveaux obtenus.

## 7. Performance et sécurité

- Les modificateurs de runes sont agrégés dans la `CompiledLoadout` au changement d'équipement, jamais par tick.
- Toutes les opérations (insertion, retrait, fusion, transmutation) sont des transactions serveur avec vérification de quantité (`quantity >= 4` dans un `UPDATE ... WHERE`) → impossible de dupliquer par requêtes concurrentes.
