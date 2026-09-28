# 18 — Roadmap de développement

Règle : ne jamais développer tout le jeu d'un coup. Chaque phase se termine par une version
**jouable, mesurée (benchmarks + tests de charge) et stable** avant d'ajouter la suivante.

## Phase 0 — Fondations (3–4 semaines)

- Monorepo : workspace Cargo, client Vite/TS, CI (lint, tests, format), Docker Compose (Postgres, Redis).
- Schéma de protocole + codegen Rust/TS + test croisé.
- Crates `sim-movement` (compilée native + WASM), `spatial` (grille), `game-data`.
- Pipeline d'assets minimal (Aseprite → atlas).
- Squelette de télémétrie (métriques Prometheus, logs structurés).

**Sortie** : un carré se déplace dans une zone vide, à plusieurs, avec prédiction et interpolation, 30 Hz.

## Phase 1 — Vertical slice (10–14 semaines)

Contenu exact exigé :

| Élément | Portée |
|---|---|
| Personnage | L'Éveillé, sprite 8 directions, animations de base |
| Région | Plaines de l'Aube (3 zones + 1 sanctuaire) |
| Monstres | 5 types (normal, rapide, tank, distance, magique) + élites à 4 affixes |
| Boss | Garde-Soleil Rouillé (3 phases) |
| Compétences | Les 6 compétences de base + esquive |
| Déplacement / combat | Serveur autoritaire, collisions, télégraphes, dégâts, statuts de base |
| XP / niveau | Niveaux 1–10 selon la courbe |
| Objets | ~30 bases, raretés 1–6, affixes, drops au sol avec FX |
| Inventaire | Grille, équipement, démontage |
| Multijoueur | Canaux, AOI, deltas, reconnexion |
| Chat simple | Canaux Région + Privé + Système, rate limit |
| Persistance | Comptes, personnage, inventaire, checkpoints |

**Critères de sortie** : 60 FPS sur la machine de référence, S1–S4 exécutés et capacités mesurées,
aucun objet perdu ni dupliqué en S10, 10 testeurs jouent 2 h sans bug bloquant, retour « le combat est agréable ».

## Phase 2 — Profondeur du build (8–10 semaines)

1. **Arbre de compétences** : structure 5 rangs × 3 nœuds, points, réinitialisation.
2. **Évolutions** : 2 premières évolutions complètes (Lame-Solaire, Arcaniste Prismatique), changement d'évolution, loadouts ; tags/modificateurs/déclencheurs génériques.
3. Régions 2–3, niveaux 10–30.

## Phase 3 — Loot avancé et runes (6–8 semaines)

4. **Loot avancé** : raretés 7–9, FX majeurs, pouvoirs légendaires, fusion avec animation, journal.
5. **Runes** : sockets, 8 niveaux, fusion en masse.
6. Échanges entre joueurs (transactionnels).

## Phase 4 — Boss et montures (8 semaines)

7. **Boss** : framework de patterns/phases data-driven, boss des régions 2–6, donjons instanciés.
8. **Montures** : système complet dès le niveau 20.
9. 4 évolutions supplémentaires.

## Phase 5 — Endgame (10–12 semaines)

10. **Soleils** : 5 premiers boss Soleil, éclats, forge, pity, Codex.
11. **Lunes** : phases, influences, conjonctions, alignements.
12. Régions 7–9, 15 boss Soleil au total, 4 dernières évolutions.

## Phase 6 — Social et compétition (6 semaines, en parallèle possible dès la phase 3)

13. **Classements** (Leaderboard Service, flux d'événements).
14. **Groupes** complets (XP, synchronisation mentor, recherche de groupe, matchmaking donjons).
15. Amis, blocage, signalement, **guildes**.

## Phase 7 — Exploitation et scaling (continu, jalon avant bêta)

16. **Monitoring avancé** : dashboards complets, alertes, runbooks, panneau d'administration.
17. **Scaling** : extraction des services, NATS, WebTransport, Kubernetes + Agones, multi-régions, S6–S9.
18. Pentest, bug bounty, saisons.

## Jalons

| Jalon | Contenu | Joueurs cibles |
|---|---|---|
| M1 — Vertical slice | Phase 0–1 | Interne (10–30) |
| M2 — Alpha fermée | Phases 2–4 | 200–1 000 |
| M3 — Bêta fermée | Phases 5–6 + monitoring | 2 000–5 000 |
| M4 — Bêta ouverte | Phase 7, tests S6 à 2× | 10 000+ |
| M5 — Lancement + Saison 1 | Contenu complet, 10 évolutions | 10 000–50 000 |

## Risques principaux

| Risque | Mitigation |
|---|---|
| Sous-estimation du volume d'art (10 évolutions, 150 compétences, 15 boss) | Pipeline d'assets et FX data-driven tôt ; priorité au vertical slice ; réutilisation par palettes |
| Équilibrage d'un espace de builds immense | Télémétrie par nœud/combinaison dès l'alpha, simulateur de DPS, configuration à chaud |
| Performance dégradée par empilement de fonctionnalités | Benchmarks en CI, budgets par système, principe « pas de fonctionnalité sans mesure » |
| Complexité d'infrastructure prématurée | Monolithe modulaire jusqu'à l'alpha, extraction guidée par les mesures |
| Triche / bots | Architecture autoritaire dès le jour 1, détection d'anomalies à partir de l'alpha |

## Prochaine étape concrète

Démarrer la **Phase 0** : initialiser le workspace, écrire le schéma de protocole et la crate
`sim-movement`, puis un prototype de déplacement multijoueur mesuré.
