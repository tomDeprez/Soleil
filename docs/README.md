# SOLEIL — Dossier de conception

Hack'n Slash 2D top-down pixel art, multijoueur en ligne mondial, jouable dans le navigateur.

Ce dossier constitue la conception complète exigée **avant** le début du développement.
Chaque système est décrit selon la même grille : fonctionnement, architecture, données,
interactions, performances, sécurité, scalabilité, difficultés et solutions.

## Index des documents

| # | Document demandé | Fichier |
|---|---|---|
| 1 | Game Design Document complet | [01-game-design.md](01-game-design.md) |
| 2 | Architecture technique (choix technologiques) | [10-architecture-technique.md](10-architecture-technique.md) |
| 3 | Architecture réseau | [11-architecture-reseau.md](11-architecture-reseau.md) |
| 4 | Architecture serveur | [12-architecture-serveur.md](12-architecture-serveur.md) |
| 5 | Architecture client | [13-architecture-client.md](13-architecture-client.md) |
| 6 | Schéma de base de données | [14-base-de-donnees.md](14-base-de-donnees.md) |
| 7 | Modèle de données des personnages | [14-base-de-donnees.md#modèle-personnage](14-base-de-donnees.md#modèle-personnage) |
| 8 | Modèle de données des objets | [14-base-de-donnees.md#modèle-objet](14-base-de-donnees.md#modèle-objet) |
| 9 | Système de compétences | [02-classe-evolutions-competences.md](02-classe-evolutions-competences.md) |
| 10 | Système de loot (+ fusion) | [03-loot-objets-fusion.md](03-loot-objets-fusion.md) |
| 11 | Système de runes | [04-runes.md](04-runes.md) |
| 12 | Système de Soleils | [05-soleils-lunes.md](05-soleils-lunes.md) |
| 13 | Système de Lunes | [05-soleils-lunes.md#lunes](05-soleils-lunes.md#lunes) |
| 14 | Système de montures | [06-montures.md](06-montures.md) |
| 15 | Système de groupes | [07-social.md#groupes](07-social.md#groupes) |
| 16 | Système d'amis | [07-social.md#amis](07-social.md#amis) |
| 17 | Système de chat | [07-social.md#chat](07-social.md#chat) |
| 18 | Système de classement | [07-social.md#classements](07-social.md#classements) |
| 19 | Système de sécurité | [15-securite-anticheat.md](15-securite-anticheat.md) |
| 20 | Système anti-cheat | [15-securite-anticheat.md#anti-cheat](15-securite-anticheat.md#anti-cheat) |
| 21 | Système de monitoring | [16-monitoring-administration.md](16-monitoring-administration.md) |
| 22 | Système d'administration | [16-monitoring-administration.md#administration](16-monitoring-administration.md#administration) |
| 23 | Stratégie de scaling | [12-architecture-serveur.md#scaling](12-architecture-serveur.md#scaling) |
| 24 | Stratégie d'optimisation client | [13-architecture-client.md#optimisation](13-architecture-client.md#optimisation) |
| 25 | Stratégie d'optimisation réseau | [11-architecture-reseau.md](11-architecture-reseau.md) |
| 26 | Plan de tests de charge et objectifs de performance | [17-performance-tests-charge.md](17-performance-tests-charge.md) |
| 27 | Roadmap de développement | [18-roadmap.md](18-roadmap.md) |

## Stack retenue (résumé)

| Couche | Choix | Raison principale |
|---|---|---|
| Client | TypeScript + PixiJS v8 (WebGL2, WebGPU opportuniste) + Vite | Meilleur moteur 2D batché du web, écosystème mature, WebGPU sans réécriture |
| Transport | WebSocket binaire (MVP) → WebTransport datagrammes (phase scaling) | Universel aujourd'hui, chemin vers UDP-like demain |
| Protocole | Schéma binaire maison, bit-packing, code généré Rust ↔ TS | Taille minimale, zéro JSON dans la boucle |
| Game server | Rust (tokio + ECS maison orienté données) | Latence prévisible sans GC, mémoire maîtrisée, sécurité mémoire |
| Services méta | Rust (axum) — même workspace que le game server | Types et formules partagés, une seule chaîne d'outils |
| Bus interne | NATS | Pub/sub léger, faible latence, request/reply |
| Cache / état chaud | Redis (Valkey compatible) | Sessions, présence, classements (sorted sets), rate limiting |
| Persistance | PostgreSQL 16 | Transactions ACID pour objets/échanges, JSONB pour données flexibles |
| Observabilité | OpenTelemetry → Prometheus, Grafana, Loki, Tempo | Standard ouvert, métriques + logs + traces corrélés |
| Déploiement | Docker + Compose (MVP) → Kubernetes + Agones (scaling) | Simple au début, orchestrateur de game servers ensuite |

Le détail et la justification de chaque choix sont dans [10-architecture-technique.md](10-architecture-technique.md).

## Principes non négociables

1. Ne jamais sacrifier les performances pour une fonctionnalité.
2. Ne jamais faire confiance au client.
3. Ne jamais envoyer au client une information inutile.
4. Ne jamais mettre la logique de jeu dans le frontend.
5. Ne jamais faire dépendre la boucle de gameplay d'une base SQL.
6. Ne jamais charger tout le monde ni tous les assets simultanément.

Priorité permanente : **performance + gameplay + profondeur + sécurité + scalabilité**.

## Outils

- `tools/balance/xp_curve.py` : génère la courbe d'XP et les taux de drop des Soleils utilisés dans ce dossier.
