# 05 — Soleils et Lunes

## Soleils

### 1. Définition

Un **Soleil** est un objet unique, extrêmement rare, qui définit un build.

- **Statistiques fixes** (pas de tirage aléatoire : un Soleil donné est identique pour tous).
- **Passif unique** (modificateur permanent).
- **Mécanique spéciale** (déclencheur ou comportement nouveau).
- **Aspects** : tags propres aux Soleils (`Rythme, Soin, Explosion, Aura, Invocation, Critique, Défense, Mouvement, Feu, Givre, Foudre, Ombre, Lumière`) utilisés par les Lunes.
- **Ascension** 0 à 5 étoiles (doublons) : chaque étoile améliore les statistiques fixes de 8 % et, à 3 et 5 étoiles, la mécanique.
- Lié au compte, non échangeable. Un même Soleil ne peut être équipé qu'une fois.

### 2. Emplacements

| Emplacement | Déblocage |
|---|---|
| 1 | Niveau 60 (quête « Le Premier Astre ») |
| 2 | Niveau 65 |
| 3 | Niveau 72 |
| 4 | Niveau 80 |
| 5 | Niveau 88 |

### 3. Catalogue

15 boss de haut niveau × 3 Soleils = **45 Soleils** au lancement, + 1 Soleil saisonnier par saison.
Exemples :

| Boss | Soleil | Stats fixes | Passif | Mécanique | Aspects |
|---|---|---|---|---|---|
| Colosse de Basalte (60) | Cœur de Magma | +12 % PV, +20 armure | +15 % dégâts de Feu | Toutes les 10 s, prochaine compétence de zone crée une fissure de lave (6 s) | Rythme, Feu, Explosion |
| Colosse de Basalte (60) | Soleil de Sève | +10 % PV, +2 % régénération | Soins reçus +20 % | **Toutes les 10 secondes, soin de 35 % des PV max** (ne se déclenche pas au-dessus de 90 % PV, reporte alors d'1 s) | Rythme, Soin |
| Reine Tempête (62) | Œil du Cyclone | +10 % vitesse de déplacement | +1 charge d'esquive | Chaque esquive déclenche une tornade qui aspire et frappe | Mouvement, Foudre |
| Jumeau Divisé (64) | Astre Double | +6 % chance crit | +25 % dégâts crit | Les crits frappent une 2ᵉ fois à 40 % sur une cible proche | Critique |
| Archiviste (66) | Mémoire Solaire | +10 % réduction de recharge | — | La dernière compétence unique utilisée peut être relancée une fois à 50 % pendant 8 s | Rythme |
| Veilleur du Vide (71) | Soleil Noir | +15 % dégâts d'Ombre | −30 % soins reçus | Chaque kill à moins de 50 % PV octroie 10 % PV en bouclier | Ombre, Défense |
| Mangeur d'Étoiles (73) | Cœur de Supernova | +8 % chance crit | — | Les crits ont 10 % de chance (ICD 0,5 s) de faire exploser la cible (120 % dégâts, zone 3 tuiles) | Critique, Explosion |
| Titan Enchaîné (79) | Chaîne d'Aurore | +20 % armure | Contrôles subis −30 % | Les monstres étourdis sont liés : 30 % des dégâts qu'ils subissent sont partagés | Défense, Aura |
| Seigneur Éclipse (86) | Couronne Éclipse | +10 % tous dégâts | — | Alterne toutes les 12 s entre Zénith (+30 % dégâts) et Nadir (+30 % réduction de dégâts) | Rythme, Lumière, Ombre |
| Soleil Mort (90) | Dernier Soleil | +15 % toutes stats | +1 emplacement de Lune « libre » | Au premier coup mortel toutes les 180 s : renaissance à 50 % PV, explosion solaire | Soin, Explosion, Lumière |

### 4. Drop

Taux **direct** par victoire (par joueur, loot personnel), configurables côté serveur
(`config/balance/suns.toml`), générés par `tools/balance/xp_curve.py` :

| Boss | Niveau | Taux direct | Soit 1 chance sur |
|---|---|---|---|
| 1 | 60 | 0,0100 % | 10 000 |
| 2 | 62 | 0,0092 % | 10 898 |
| 3 | 64 | 0,0084 % | 11 877 |
| 4 | 66 | 0,0077 % | 12 943 |
| 5 | 69 | 0,0071 % | 14 106 |
| 6 | 71 | 0,0065 % | 15 372 |
| 7 | 73 | 0,0060 % | 16 753 |
| 8 | 75 | 0,0055 % | 18 257 |
| 9 | 77 | 0,0050 % | 19 897 |
| 10 | 79 | 0,0046 % | 21 684 |
| 11 | 81 | 0,0042 % | 23 631 |
| 12 | 84 | 0,0039 % | 25 753 |
| 13 | 86 | 0,0036 % | 28 066 |
| 14 | 88 | 0,0033 % | 30 587 |
| 15 | 90 | 0,0030 % | 33 333 |

Formule : `taux(i) = 0,0001 × 0,3^(i/14)`, i = 0…14.

### 5. Ne pas dépendre de la chance : quatre filets de sécurité

Avec ces taux, compter uniquement sur le drop direct serait injuste. Quatre mécaniques parallèles
donnent une progression **garantie et visible** :

1. **Éclats solaires (progression déterministe)**
   Chaque victoire donne des éclats propres à ce boss : 1 de base, +1 sans mort, +1 si temps < temps de référence, +2 à la première victoire hebdomadaire.
   La **Forge Solaire** permet de fabriquer **le Soleil de son choix** parmi les 3 du boss :

   | Boss | Coût en éclats | Victoires ≈ (2,5 éclats/victoire) |
   |---|---|---|
   | 1 (60) | 800 | 320 |
   | 8 (75) | 1 150 | 460 |
   | 15 (90) | 1 500 | 600 |

   Coût linéaire entre les bornes. C'est long (dizaines d'heures) mais **certain**.

2. **Protection contre la malchance (pity doux)** : après `N = 1 / taux / 4` victoires sans Soleil de ce boss, le taux est multiplié par `1 + (victoires − N) / N`, plafonné à ×10. Réinitialisation au drop. Compteur invisible pour préserver la surprise, mais documenté.

3. **Collection et doublons** : un doublon donne une étoile d'Ascension ; au-delà de 5 étoiles, il est converti en 60 % du coût en éclats (jamais « perdu »).

4. **Codex des Astres** : chaque boss vaincu N fois (10/100/500) débloque des bonus permanents mineurs du compte (+1 % Fortune sur ce boss, titre, cosmétique), et le classement « Collection ».

Toutes les valeurs (taux, coûts, bonus, plafonds) sont de la configuration serveur rechargeable à chaud et versionnée ; chaque changement est journalisé dans l'audit admin.

### 6. Données

```text
SunDef       { id, boss_id, name, fixed_stats[], passive: Modifier[], mechanic: Trigger|Behavior,
               aspects[], ascension_bonus[5], sprite, fx }
SunOwned     { account_id, sun_id, stars 0..5, obtained_at, source: Drop|Forge|Event }
SunSlot      { character_id, slot 1..5, sun_id? }
BossProgress { account_id, boss_id, kills, kills_since_sun, shards, best_time_ms, weekly_bonus_claimed_at }
```

### 7. Sécurité et performance

- Drop tiré exclusivement par le serveur ; écriture **synchrone** en base (transaction) avant l'annonce à quiconque.
- Les compteurs de pity et d'éclats sont en base (ligne par compte × boss), mis à jour à chaque victoire dans la même transaction que la récompense.
- La mécanique d'un Soleil est compilée dans la `CompiledLoadout` : zéro coût supplémentaire par tick sauf ses propres déclencheurs.

---

## Lunes

### 1. Différence fondamentale avec les Soleils

| | Soleil | Lune |
|---|---|---|
| Nature | Pouvoir fixe et autonome | **Modulateur** : altère un Soleil |
| Rareté | Extrême (boss 60+) | Rare (dès le niveau 50, sources variées) |
| Statistiques | Fixes | Aucune stat brute ; effet dépendant de la **phase** |
| Dynamique | Constante | Cyclique pendant le combat |
| Progression | Ascension par doublons | Niveau (1–10) via éclats lunaires |

### 2. Orbites

- Chaque emplacement de Soleil possède une **orbite** : on y place au plus **1 Lune**, qui n'agit que sur le Soleil de cet emplacement.
- 5 Soleils → jusqu'à 5 Lunes (le Soleil « Dernier Soleil » ajoute une Lune libre qui affecte tous les Soleils à 40 %).

### 3. Phases

Une Lune accumule de la **Clarté** en combat (dégâts infligés, esquives, temps) et traverse un cycle :

```text
Nouvelle (0–25 %) → Croissante (25–75 %) → Pleine (75–100 %, 6 s) → Décroissante (retour à 0 en 10 s)
```

L'effet dépend de la phase ; la **Pleine Lune** déclenche une **Marée** (effet ponctuel fort).
Hors combat, la Lune revient à Nouvelle en 20 s. Durée d'un cycle typique : 30–60 s → rythme de
combat lisible, visible dans le HUD.

### 4. Influences

Chaque Lune porte une **Influence** (sa nature) et une **Affinité** (un ou deux Aspects de Soleil qu'elle amplifie).

| Influence | Effet sur le Soleil lié | Marée (Pleine Lune) |
|---|---|---|
| **Écho** | Le Soleil se déclenche une 2ᵉ fois à 30/40/60 % selon la phase | Double déclenchement à 100 % |
| **Inversion** | Les effets positifs du Soleil ont une version négative sur les ennemis (soin → dégâts de Lumière égaux à 50 %) | Inversion à 100 % |
| **Marée** | Les minuteries du Soleil accélèrent selon la phase (−10/−25/−50 %) | Réinitialise la minuterie |
| **Éclipse** | Supprime le Soleil pendant Nouvelle/Croissante et **stocke** sa puissance | Libère la puissance stockée (×3) |
| **Reflet** | Copie le Soleil à 25 % sur le membre du groupe le plus proche | Copie à 60 % sur tout le groupe |
| **Gravité** | Les effets de zone du Soleil attirent les ennemis | Puits gravitationnel 3 s |
| **Sang** | Le Soleil coûte 2 % PV par déclenchement mais +40 % d'effet | +100 % d'effet, sans coût |
| **Givre-Lune** | Les effets du Soleil ralentissent | Gèle 1,5 s les ennemis touchés |

Affinité : si un Aspect du Soleil correspond, l'effet de la Lune est **× 1,5**.

### 5. Synergies (Conjonctions)

Trois niveaux de profondeur :

1. **Synergie générique** (calculée) : Influence × Aspects du Soleil. Exemple : Soleil de Sève (Rythme, Soin) + Lune d'Inversion (affinité Soin) → toutes les 10 s, le soin de 35 % émet aussi une onde infligeant des dégâts de Lumière égaux à 50 % du soin × 1,5.
2. **Conjonctions nommées** (cachées, à découvrir) : ~60 paires précises Soleil × Lune avec un effet unique. Exemple : *Couronne Éclipse* + *Lune d'Éclipse* = « **Éclipse Parfaite** » : pendant Nadir, les dégâts subis sont stockés et renvoyés au passage en Zénith. Découverte → entrée de Codex + annonce Région + classement de collection.
3. **Alignements** (bonus d'ensemble) : conditions sur les 5 orbites. Exemples : 3 Lunes de même Influence → « Triade » (+20 % à cette Influence) ; 5 Lunes toutes différentes → « Conjonction Totale » (la Marée de chaque Lune déclenche un Écho mineur des autres).

Nombre de combinaisons : 45 Soleils × ~30 Lunes × 5 orbites × phases → espace de recherche énorme, mais chaque effet reste explicable par une phrase (Influence) et visible dans l'infobulle calculée.

### 6. Obtention

| Source | Niveau | Taux |
|---|---|---|
| Élites pendant la **Nuit** (cycle jour/nuit de 90 min, nuit = 20 min) | 50+ | 0,2 % |
| Événement mondial « Nuit sans Lune » | 50+ | × 3 |
| Donjons de niveau 55+ (coffre final) | 55+ | 1 % |
| Boss Soleil | 60+ | 1,5 % |
| Forge lunaire | 50+ | 400 éclats lunaires (Lune aléatoire parmi une Influence choisie) |

Éclats lunaires : 1–3 par élite de nuit, 20 par donjon, démontage de Lune (50 %).

### 7. Niveaux

Niveau 1–10, coût en éclats lunaires croissant (20 → 1 500). Chaque niveau : +5 % d'effet, Clarté gagnée +3 %. Niveau 10 : la Marée dure 50 % plus longtemps.

### 8. Données

```text
MoonDef     { id, name, influence, affinity: Aspect[1..2], phase_effects[4], tide: Effect, level_curve }
MoonOwned   { id uuid, account_id, moon_def_id, level 1..10, obtained_at, source }
MoonOrbit   { character_id, slot 1..5, moon_id? }
Conjunction { sun_id, moon_def_id, effect: Trigger|Behavior, discovered_by_first?, first_discovered_at }
AccountDiscovery { account_id, conjunction_id, discovered_at }
```

### 9. Architecture et performance

- Phase et Clarté : état **temporaire** dans le game server (composant ECS `MoonState`), jamais écrit en base.
- Le client reçoit uniquement la phase de ses propres Lunes (1 octet par Lune, sur changement), et les Marées des autres joueurs comme simples événements FX.
- Les conjonctions sont résolues à la compilation du loadout (table de hachage `(sun_id, moon_def_id)`), pas à chaque tick.

### 10. Difficultés et solutions

| Difficulté | Solution |
|---|---|
| Combinaisons trop fortes | Plafonds par Influence, télémétrie par paire, configuration à chaud |
| Illisibilité | Infobulles calculées, HUD de phase, simulateur en sanctuaire |
| « Méta » unique | Conjonctions nommées réparties sur tous les Soleils, rotation d'une Lune saisonnière |
| Spam de la découverte | Découverte validée serveur uniquement quand la conjonction s'est réellement déclenchée en combat |
