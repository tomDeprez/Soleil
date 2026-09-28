# 01 — Game Design Document

## 1. Vision

**SOLEIL** est un Hack'n Slash 2D top-down en pixel art, multijoueur mondial, jouable dans le navigateur.
Le joueur incarne un unique personnage, l'**Éveillé**, qui peut maîtriser progressivement dix
évolutions radicalement différentes. Le jeu vise des centaines, voire des milliers d'heures de
progression, portées par le loot, la construction de builds, les boss exigeants et la coopération.

### Piliers

| Pilier | Traduction concrète |
|---|---|
| **Skill** | Attaques télégraphiées, esquive à i-frames, positionnement, fenêtres de vulnérabilité. Un bon joueur survit à un contenu « trop dur » pour son équipement. |
| **Profondeur** | 10 évolutions × (10 compétences × 15 améliorations + 5 uniques), objets à affixes, runes, 5 Soleils, 5 Lunes, synergies Soleil × Lune. |
| **Un seul personnage** | Changer d'évolution ne demande jamais de recréer un personnage : niveau, équipement, collection et Soleils sont partagés. |
| **Loot désirable** | 9 raretés lisibles instantanément, drops spectaculaires, fusion, chasse aux Soleils avec filet de sécurité anti-malchance. |
| **Long terme** | 60 → 90 représente ~1 700 heures de farm optimal ; saisons, classements, collection. |
| **Fluidité** | 60 FPS navigateur, latence masquée, aucune donnée inutile sur le réseau. |

### Public et plateforme

- Desktop (Chrome, Edge, Firefox, Safari récents), clavier + souris, manette en option.
- Sessions de 20 minutes (quelques boss, une fusion) à plusieurs heures (farm, donjons de groupe).

## 2. Boucle de jeu

```text
Explorer → Combattre → Tuer → XP → Niveau → Débloquer compétences → Construire le build
   ↑                                                                          ↓
Builds encore plus puissants ← Objets très rares ← Boss ← Nouvelles régions ← Loot / équipement
```

Trois boucles imbriquées maintiennent l'intérêt :

| Boucle | Durée | Contenu | Récompense |
|---|---|---|---|
| Micro | 5–30 s | Pack de monstres, esquive, combo de compétences | Explosion de loot, XP, sensation de puissance |
| Méso | 10–60 min | Événement de zone, élite rare, mini-boss, donjon, fusion | Objet ciblé, rune, niveau, amélioration de compétence |
| Macro | Jours–mois | Nouvelle évolution, nouvelle région, Soleil, Lune, classement saisonnier | Changement profond du build, prestige |

## 3. Le monde

### 3.1 Structure

Le monde, **Héliaque**, est un continent découpé en **régions**, chacune composée de **zones**
(cartes de 256×256 tuiles de 32 px au maximum). Les zones sont reliées par des transitions
sans écran de chargement bloquant (préchargement des voisines, voir client §Streaming).
Chaque zone peut exister en plusieurs **canaux** (instances parallèles plafonnées, voir serveur).

Types d'espaces :

- **Sanctuaires** (villes) : pas de combat, marchands, forge de fusion, autel runique, écurie, tableau de groupe, changement d'évolution.
- **Zones ouvertes** : farm, événements, élites, mini-boss, ressources, partagées entre joueurs du canal.
- **Donjons** : instanciés pour un joueur ou un groupe (1–4), boss final, loot amélioré.
- **Arènes de boss** : instanciées, accès par clé ou par événement.
- **Zones dangereuses** : sous-zones à affixes permanents (brouillard toxique, nuit éternelle), loot × 1,5.

### 3.2 Régions

| # | Région | Niveaux | Thème | Mécanique de zone | Boss de région |
|---|---|---|---|---|---|
| 1 | Plaines de l'Aube | 1–10 | Prairies, ruines solaires | Tutoriel intégré, aucun malus | Garde-Soleil Rouillé |
| 2 | Forêt des Murmures | 10–20 | Forêt dense, fées corrompues | Brouillard réduisant la vision | La Mère-Racine |
| 3 | Marais de Cendre | 20–30 | Marécage volcanique | Sols brûlants (DoT si immobile) | Hydre de Tourbe |
| 4 | Désert d'Obsidienne | 30–40 | Désert de verre noir | Tempêtes de sable périodiques | Le Scarabée-Éclipse |
| 5 | Cités Englouties | 40–50 | Ruines sous-marines à marée | Marée montante qui change la carte | Léviathan Captif |
| 6 | Pics Givrés | 50–60 | Montagnes, blizzards | Froid cumulatif, feux de camp | Wyrm de Givre |
| 7 | Terres Brisées | 60–70 | Îles flottantes | Chutes, vent, gravité variable | 5 boss Soleil (60–70) |
| 8 | Abysse Astral | 70–80 | Vide cosmique | Zones d'ombre (soins réduits) | 5 boss Soleil (71–81) |
| 9 | Couronne du Soleil Mort | 80–90 | Soleil éteint, ruines divines | Cycle Éclipse/Zénith global | 5 boss Soleil (84–90) |
| 10 | Le Zénith (endgame) | 90 | Failles saisonnières | Affixes de saison, échelle infinie | Rotation saisonnière |

Chaque région définit dans sa configuration : niveau recommandé, familles de monstres, variantes,
affixes autorisés, tables de loot, ressources (minerais, herbes, éclats), événements, élites,
mini-boss, boss et événements rares.

### 3.3 Événements

| Type | Fréquence | Exemple | Récompense |
|---|---|---|---|
| Événement de zone | Toutes les 10–20 min par zone | « Invasion de cendre » : vagues + élite | XP × 2 pendant l'événement, coffre |
| Élite rare nommée | Réapparition 30–90 min, position aléatoire | « Grisecroc l'Affamé » | Loot garanti rareté ≥ 4 |
| Événement mondial | Planifié / admin | « Nuit sans Lune » : Lunes drop × 3 | Lunes, titres |
| Événement rare | 0,5 % par heure et par zone | « Comète errante » | Matériaux de fusion rares |

### 3.4 Ressources

Récoltables sans mini-jeu (maintien d'une touche 1 s), instanciées par joueur (pas de vol de ressource).
Utilisées pour : fusion, craft de clés de donjon, consommables, personnalisation de monture.

## 4. Difficulté

La difficulté est **asymétrique** : accessible au début, puis de plus en plus exigeante.

| Tranche | Temps cible | Ressenti | Ce que le jeu exige |
|---|---|---|---|
| 1 → 10 | ~2 h | Apprentissage | Déplacement, esquive, 3 premières compétences, ramasser et équiper |
| 10 → 20 | ~8 h | Montée en tension | Utiliser les éléments, gérer la ressource, lire les télégraphes |
| 20 → 40 | ~65 h | Difficile | Optimiser équipement et runes, première évolution, montures |
| 40 → 60 | ~210 h | Hardcore | Build cohérent, synergies, esquive parfaite contre les élites, groupes |
| 60 → 90 | ~1 700 h | Endgame extrême | Soleils/Lunes, boss à mécaniques, classements |

Leviers de difficulté (tous pilotés par configuration serveur) :

- **Dégâts des monstres** : croissent plus vite que les PV du joueur sans équipement adapté (`dmg = base × 1,09^niveau`).
- **Densité et affixes** : nombre d'affixes par élite = 1 (L < 20), 2 (20–40), 3 (40–60), 4 (60+).
- **Pénalité de mort** : 0 % (L < 10) ; au-delà, perte de 5 % de la barre d'XP du niveau courant (jamais de perte de niveau), plus une durabilité réduite sur l'équipement. Aucun objet n'est jamais perdu.
- **Résistances** : chaque région majeure demande une résistance élémentaire (−20 % par région au-delà de la 3ᵉ), incitant à adapter le build.

## 5. Expérience

### 5.1 Courbe

Référence : farm solo optimal ≈ 720 monstres normaux par heure. Courbe générée par
`tools/balance/xp_curve.py` (valeurs par défaut, configurables).

| Niveau | XP / monstre du niveau | XP requise | Temps cible | Cumul |
|---|---|---|---|---|
| 1 → 2 | 10 | 360 | 0,05 h | 0 h |
| 5 → 6 | 13 | 2 110 | 0,22 h | 1 h |
| 9 → 10 | 18 | 5 180 | 0,40 h | 2 h |
| 15 → 16 | 28 | 17 920 | 0,89 h | 6 h |
| 19 → 20 | 37 | 31 970 | 1,20 h | 11 h |
| 25 → 26 | 57 | 99 400 | 2,42 h | 22 h |
| 30 → 31 | 81 | 194 900 | 3,34 h | 37 h |
| 39 → 40 | 156 | 561 600 | 5,00 h | 76 h |
| 45 → 46 | 241 | 1 452 100 | 8,37 h | 119 h |
| 50 → 51 | 346 | 2 674 800 | 10,74 h | 168 h |
| 59 → 60 | 663 | 7 160 400 | 15,00 h | 286 h |
| 60 → 61 | 713 | 9 240 500 | 18,00 h | 304 h |
| 65 → 66 | 1 024 | 18 622 200 | 25,26 h | 414 h |
| 70 → 71 | 1 470 | 37 512 500 | 35,44 h | 570 h |
| 75 → 76 | 2 110 | 75 555 700 | 49,73 h | 788 h |
| 80 → 81 | 3 029 | 152 198 600 | 69,79 h | 1 094 h |
| 85 → 86 | 4 348 | 306 568 400 | 97,93 h | 1 524 h |
| 89 → 90 | 5 807 | 536 896 900 | 128,41 h | 1 989 h |

Total 1 → 90 : ≈ 4,1 milliards d'XP. Ces temps sont des temps de **farm optimal** : événements,
donjons et groupe les réduisent de 30 à 50 %, ce qui rend la progression dure mais jamais absurde.
L'XP est stockée en `i64`.

### 5.2 Sources d'XP

| Source | Multiplicateur (base : monstre normal de même niveau) |
|---|---|
| Monstre normal / rapide / distance / magique | × 1 |
| Tank | × 1,5 |
| Élite (par affixe) | × 3 + 1 par affixe |
| Rare nommé | × 15 |
| Mini-boss | × 40 |
| Boss de région | × 300 (première victoire de la semaine × 3) |
| Événement de zone | 3 % d'un niveau (plafonné à 1 % au-delà de 60) |
| Quêtes | Fixe, dégressif après première complétion |
| Donjon | Bonus de complétion = 20 % de l'XP gagnée dedans |

Écart de niveau (joueur − monstre) :

| Écart | XP |
|---|---|
| Monstre ≥ +5 | × 1,2 (plafonné, pour éviter le « dive » suicidaire rentable) |
| −4 à +4 | × 1 |
| −5 à −9 | × 0,5 |
| ≤ −10 | × 0,05 |

### 5.3 Au-delà de 90

Le niveau 90 est le plafond. L'XP gagnée ensuite alimente les **Rangs d'Apogée** (compteur
saisonnier, purement cosmétique + classement) pour ne jamais créer d'inflation de puissance.

## 6. Personnage

- Une seule classe de base : **l'Éveillé**. Dix évolutions (voir [02](02-classe-evolutions-competences.md)).
- Statistiques primaires : **Force**, **Agilité**, **Intellect**, **Vigueur**, **Esprit**. 5 points par niveau, redistribuables en sanctuaire (coût en or croissant).
- Statistiques dérivées : PV, ressource (**Lumen**), armure, résistances (feu, givre, foudre, ombre, lumière, poison), chance critique, dégâts critiques, vitesse d'attaque, vitesse de lancement, vitesse de déplacement, réduction de temps de recharge, régénération, vol de vie.
- **Esquive** (Espace par défaut) : roulade de 4 tuiles, 0,25 s d'invulnérabilité, 2 charges, recharge 3 s. Toutes les évolutions l'ont, certaines la modifient.

## 7. Monstres

### 7.1 Catégories

| Catégorie | Rôle | Comportement IA (arbre de comportement serveur) |
|---|---|---|
| Normal | Masse | Poursuite directe, attaque au contact, fuit à 10 % PV (certaines familles) |
| Rapide | Pression | Encercle, attaques éclair, recul après frappe |
| Tank | Obstacle | Lent, bouclier frontal, charge télégraphiée |
| Distance | Positionnement | Maintient 6–9 tuiles, repositionnement si ligne de vue coupée |
| Magique | Zone | Cercles télégraphiés au sol, buffs d'alliés, invocations mineures |
| Élite | Pic de difficulté | Base de catégorie + 1–4 affixes, aura visible, PV × 6 |
| Rare nommé | Chasse | Kit unique, escorte de 3–6 serviteurs, loot garanti |
| Mini-boss | Test de build | 2 phases, 3–4 attaques, apparition sur événement |
| Boss | Examen de skill | Voir §8 |

### 7.2 Affixes

Les affixes génèrent des variantes combinables. Exemples (pool de départ : 24 affixes) :

| Affixe | Effet | Contre-jeu |
|---|---|---|
| Ardent | Laisse une traînée de feu | Ne pas suivre sa trajectoire |
| Gelé | Orbes de givre qui explosent après 1,5 s | Sortir du cercle |
| Vampirique | Se soigne de 30 % des dégâts infligés | Dégâts en rafale, anti-soin |
| Blindé | −60 % dégâts de face | Contourner |
| Téléporteur | Se téléporte au contact du joueur à distance | Rester groupé |
| Miroir | Renvoie 20 % des projectiles | Mêlée ou zone |
| Frénétique | +50 % vitesse sous 50 % PV | Burst final |
| Invocateur | Invoque 3 larves toutes les 8 s | Prioriser la cible |
| Éclipse | Zone d'ombre : soins joueurs −50 % | Tirer la cible hors de la zone |
| Chaîné | Lié à un autre élite : partage 50 % des dégâts | Tuer les deux ensemble |

Contraintes : combinaisons interdites définies en données (ex. Miroir + Blindé + Vampirique),
un budget de difficulté par affixe, affixes tirés par le serveur avec seed.

### 7.3 Données

```text
MonsterTemplate { id, family, category, base_stats, behavior_tree_id, skills[], loot_table_id, sprite_set_id, size, xp_mult }
MonsterAffix    { id, budget, incompatible[], behavior_modifiers[], aura_fx_id }
SpawnRule       { zone_id, template_ids[], density, respawn_s, elite_chance, rare_chance, level_range }
```

## 8. Boss

### 8.1 Principes

Un boss n'est jamais un sac à PV. Chaque boss possède :

- **Attaques télégraphiées** : forme au sol (cercle, cône, ligne, anneau, damier), durée d'annonce 0,6–1,5 s, couleur codant le type (rouge = dégâts, violet = contrôle, jaune = soignable/esquivable en groupe).
- **Patterns** : séquences scriptées par phase avec variations tirées par seed (pas d'aléatoire pur illisible).
- **Phases** : 2 à 4, seuils de PV, transitions invulnérables avec changement d'arène.
- **Capacités spéciales** : une mécanique signature par boss.
- **Déplacement** : sauts, charges, téléportations, poursuites.
- **Fenêtres de vulnérabilité** : après certaines attaques, le boss est **Exposé** (dégâts subis × 1,5 à × 3) pendant 2–5 s ; récompense le joueur qui a esquivé au lieu de fuir.
- **Enrage** : minuterie douce (dégâts +10 % toutes les 30 s après le temps cible) plutôt qu'un mur instantané.
- **Récompenses spécifiques** : tables propres, objets de signature, Soleils (boss 60+), Lunes, cosmétiques.

### 8.2 Machine d'état serveur

```text
BossController
  ├── Phase[n] : { hp_threshold, pattern_pool[], arena_modifier, music_stem }
  ├── Pattern  : suite d'Actions { telegraph(shape, dur), move(kind), cast(skill), wait(t), expose(dur) }
  └── Sélecteur: poids + cooldowns par pattern + règle « pas deux fois le même d'affilée »
```

Le serveur envoie les télégraphes **au début** de l'annonce (forme, position, instant de
résolution en tick serveur) ; le client les dessine et les fait se remplir. La résolution des
dégâts est faite par le serveur au tick annoncé, avec les positions serveur.

### 8.3 Boss du vertical slice : le Garde-Soleil Rouillé (niveau 10)

| Phase | PV | Patterns |
|---|---|---|
| 1 | 100–60 % | Balayage en cône (1 s), Frappe au sol en anneau (1,2 s), Charge en ligne puis **Exposé 3 s** en percutant un pilier |
| 2 | 60–25 % | Les piliers s'effondrent ; ajoute « Rayon solaire » en rotation ; invoque 4 automates rapides |
| 3 | 25–0 % | Cœur à nu : dégâts subis × 1,5 mais télégraphes raccourcis de 20 %, damier de lumière |

### 8.4 Les 15 boss Soleil (60–90)

| # | Niveau | Boss | Mécanique signature |
|---|---|---|---|
| 1 | 60 | Colosse de Basalte | Ses pas fissurent l'arène, cases qui s'effondrent |
| 2 | 62 | Reine Tempête | Vents qui poussent le joueur, projectiles déviés |
| 3 | 64 | Le Jumeau Divisé | Deux corps à PV partagés, doivent mourir à < 5 s d'écart |
| 4 | 66 | Archiviste Sans-Visage | Copie les 2 dernières compétences du joueur |
| 5 | 69 | Hydre Céleste | Chaque tête tranchée repousse sauf si brûlée |
| 6 | 71 | Veilleur du Vide | Arène obscure, lumière autour du joueur uniquement |
| 7 | 73 | Mangeur d'Étoiles | Absorbe les projectiles, les renvoie en phase 2 |
| 8 | 75 | Horloge Brisée | Rembobine le combat de 5 s toutes les 30 s |
| 9 | 77 | Dame des Miroirs | Reflets illusoires, seul le vrai a une ombre |
| 10 | 79 | Titan Enchaîné | Chaînes à briser pour ouvrir la fenêtre d'Exposé |
| 11 | 81 | Chœur des Noyés | Mécanique de rythme : attaques sur la musique |
| 12 | 84 | L'Astre Froid | Gel progressif, se réchauffer dans ses propres rayons |
| 13 | 86 | Seigneur Éclipse | Alterne Soleil/Lune, immunités inversées |
| 14 | 88 | Dévoreur de Couronnes | Vole un Soleil équipé du joueur pendant la phase 2 |
| 15 | 90 | Le Soleil Mort | 4 phases reprenant les mécaniques des 14 autres |

## 9. Économie

| Monnaie | Source | Puits |
|---|---|---|
| **Or** | Monstres, ventes | Réparations, redistribution de stats, fusion, respec, frais d'échange (5 %) |
| **Poussière d'étoile** | Démontage d'objets | Fusion, reroll d'affixes |
| **Poussière runique** | Démontage de runes | Fusion de runes, ouverture de sockets |
| **Éclats solaires** (par boss) | Chaque victoire sur un boss Soleil | Forge de Soleil ciblée (anti-malchance) |
| **Éclats lunaires** | Événements nocturnes, démontage de Lunes | Forge de Lune, réglage de phase |

Toutes les monnaies sont des entiers `i64` gérés exclusivement par le serveur ; chaque mouvement
est journalisé dans un grand livre (`currency_ledger`, voir base de données).

## 10. Interface

Principes : lisibilité en combat, HUD minimal, menus plein écran en sanctuaire, tout en DOM
superposé au canvas (voir client) sauf les éléments liés au monde (barres de vie, nombres).

| Menu | Contenu principal | Raccourci |
|---|---|---|
| Personnage | Stats primaires/dérivées, détails de calcul au survol | C |
| Équipement | 12 emplacements : tête, torse, mains, pieds, ceinture, amulette, 2 anneaux, arme, main gauche, cape, relique | C |
| Inventaire | Grille 10×6 + onglets, tri, filtre, verrouillage, comparaison | I |
| Compétences | 10 compétences, 15 améliorations chacune, barre Q W E R T D F | K |
| Arbre d'évolution | 10 évolutions, état de maîtrise, changement en sanctuaire | N |
| Runes | Sockets des objets, autel de fusion | U |
| Soleils | 5 emplacements, codex des 15 boss, compteurs d'éclats | O |
| Lunes | 5 orbites liées aux Soleils, phase courante, synergies découvertes | L |
| Montures | Collection, équipée, personnalisation | M (monter : Z) |
| Groupe | Membres, invitations, recherche de groupe | P |
| Amis | Liste, statut, demandes, bloqués | Shift+O |
| Chat | Onglets par canal | Entrée |
| Classement | Catégories, saison, filtres | J |
| Carte | Carte de région, carte du monde, marqueurs | Tab / Shift+M |
| Quêtes | Journal, suivi | Q (hors combat) → rebind par défaut : H |
| Codex | Monstres, boss, objets découverts, affixes | X |
| Collection | Objets uniques, Soleils, Lunes, montures, cosmétiques, succès | Y |
| Paramètres | Voir §11 | Échap |

Note : Q W E R T D F étant réservées aux compétences, les menus utilisent d'autres touches ; tout est remappable.

HUD : barre PV/Lumen centrale, barre de compétences avec recharges, charges d'esquive, buffs,
mini-carte, suivi de quête, cadres de groupe, flux de loot, indicateurs de boss (barre PV + phase).

## 11. Paramètres

Stockés côté serveur (`account_settings`, JSONB versionné) et en cache local ; appliqués à chaud.

**Graphismes** : préréglage (Ultra/High/Medium/Low/Performance), résolution de rendu (50–100 % + mise à l'échelle entière pixel-perfect), plein écran, VSync, limite FPS (30/60/120/144/illimité), qualité des effets, qualité des particules, lumière dynamique, ombres, post-processing (bloom, aberration, vignette), distance d'affichage des autres joueurs, qualité des sprites (atlas complets / réduits), nombre maximum d'effets affichés, masquer les effets des autres joueurs (0–100 %), secousses d'écran (0–100 %), flashs (réduction photosensibilité).

**Audio** : volume général, musique, effets, voix, ambiance, interface ; son en arrière-plan ; sons des autres joueurs (0–100 %).

**Gameplay** : nombres de dégâts (tous/miens/critiques/aucun), soins, nombres flottants cumulés, indicateurs de télégraphe (contour/remplissage/contraste élevé), noms et barres des joueurs, auto-loot (or et consommables uniquement, filtres de rareté), filtre de loot par rareté, taille de l'interface, disposition du HUD (glisser-déposer), ciblage (souris/auto), mode daltonien (3 profils : couleurs de rareté + télégraphes).

**Contrôles** : remapping complet clavier/souris/manette, deux associations par action, détection de conflit (avertissement et échange proposé), profils, restauration par défaut par catégorie, sensibilité du stick, zone morte, visée assistée manette.

## 12. Direction artistique

- **Pixel art 2D top-down 3/4**, tuiles 32×32, personnages 48×48 (grands boss jusqu'à 256×256), rendu à l'échelle entière (×2, ×3, ×4) pour rester net.
- **Palette** par région (32–48 couleurs) + palette « solaire » commune (or, blanc chaud) réservée aux raretés hautes et aux Soleils → lisibilité immédiate.
- **Silhouette** : chaque évolution a une silhouette et une couleur signature (cape, arme, aura) reconnaissables à distance ; équipement visible sur 5 emplacements (tête, torse, arme, main gauche, cape) via sprites superposés (paper-doll).
- **Animations** (8 directions générées en 5 + miroir) : idle, marche, course, esquive, 3 attaques de base, lancement, canalisation, dégâts, mort, emote ; montures : idle, marche, galop, saut.
- Monstres : 4 directions minimum + miroir, animations d'attaque avec images d'anticipation lisibles (le télégraphe est aussi dans l'animation).

## 13. FX

Les effets sont un pilier mais restent bornés :

- Particules GPU (sprites instanciés), traînées (ribbons), impacts, flashs, distorsion (shader de déplacement sur un buffer séparé), éclairage dynamique 2D (lumière additive sur une texture de lumière basse résolution), explosions en spritesheets.
- Style cohérent : particules « pixel » (pas de dégradés lisses), couleurs quantifiées par un shader final optionnel.

### FX Level of Detail

| Niveau | Particules max | Lumières dynamiques | Distorsion | Post-process | FX des autres joueurs |
|---|---|---|---|---|---|
| Ultra | 20 000 | 64 | Oui | Bloom + LUT + aberration | 100 % |
| High | 10 000 | 32 | Oui | Bloom + LUT | 75 % |
| Medium | 5 000 | 16 | Boss seulement | LUT | 50 % |
| Low | 2 000 | 4 | Non | Non | 25 % |
| Performance | 600 | 0 (lumière cuite) | Non | Non | Silhouettes seulement |

Règles transverses : priorité aux FX du joueur local et aux télégraphes (jamais coupés), budget
par frame, dégradation automatique si la frame dépasse 14 ms pendant 2 s (voir client).

## 14. Audio

- Musique par couches (stems) : exploration / combat / boss par phase, transitions en fondu synchronisées au tempo.
- Chaque rareté ≥ 4 a un son de drop propre ; raretés 7–9 : son « unique » audible à distance.
- Budget de voix audio : 32 sons simultanés, priorité par distance et importance ; spatialisation stéréo simple (panoramique + atténuation).

## 15. Saisons

- Durée : 12 semaines. Personnages saisonniers optionnels (nouveau départ, classement dédié) ; à la fin, le personnage saisonnier rejoint le royaume permanent avec tout son contenu.
- Chaque saison ajoute un thème (affixe global), une Lune saisonnière, un classement et des cosmétiques.
- Aucune puissance permanente exclusive payante ; monétisation éventuelle limitée aux cosmétiques.
