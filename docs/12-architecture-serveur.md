# 12 — Architecture serveur et stratégie de scaling

## 1. Services

| Service | État | Scalabilité | Rôle |
|---|---|---|---|
| **Edge Gateway** | Connexions (état léger) | Horizontal (N instances derrière un load balancer L4) | TLS, auth du jeton, rate limit, routage client ↔ game server, abonnements chat |
| **Game Server** | **Avec état** (simulation) | Horizontal par instances de zone | Simulation autoritaire |
| **World Directory** | Registre (Redis + mémoire) | Actif/passif | Où est chaque personnage, quelles instances existent, placement, création d'instances |
| **Auth Service** | Sans état | Horizontal | Comptes, connexion, jetons |
| **API** | Sans état | Horizontal | Opérations méta HTTP |
| **Chat Service** | Sans état | Horizontal | Filtrage, rate limit, diffusion |
| **Social Service** | Sans état (Redis) | Horizontal | Amis, présence, groupes, guildes |
| **Persistence Service** | File de travail | Horizontal (partitionné par personnage) | Écritures SQL groupées et transactionnelles |
| **Leaderboard Service** | Consommateur de flux | Horizontal (partitionné par catégorie) | Classements |
| **Admin API** | Sans état | 2 instances | Administration, audit |

Au stade prototype, Gateway + Game Server + Chat + World Directory tournent **dans un seul binaire**
(modules séparés, interfaces identiques), puis sont extraits.

## 2. Game Server

### 2.1 Modèle d'exécution

```text
Processus game-server (1 par machine ou par pod, N cœurs)
 ├── Runtime tokio : I/O réseau interne (liens gateways), NATS, persistance asynchrone
 └── Pool de threads de simulation (1 par cœur)
       └── Chaque thread exécute plusieurs instances de zone, chacune mono-thread, share-nothing
            Instance { ECS World, SpatialGrid, file d'inputs, file d'événements sortants, RNG }
```

- **Une instance = un thread à la fois**, aucune synchronisation fine, aucun verrou dans la boucle.
- Les instances communiquent uniquement par messages (transferts de joueurs, événements de groupe).
- Planification : chaque tick, chaque thread traite ses instances ; une instance trop lente est migrée (au prochain vide) ou son canal est fermé aux nouvelles entrées.

### 2.2 Pipeline d'un tick (33,3 ms de budget, cible < 8 ms par instance chargée)

```text
1. Drain des inputs réseau (files lock-free SPSC gateway → instance)
2. Validation des inputs (cadence, bornes, état)
3. Déplacements joueurs (collisions tuiles + cercles)
4. IA monstres (seulement cellules actives, voir 2.4)
5. Compétences : lancements, projectiles, zones, déclencheurs (budget par entité)
6. Résolution des dégâts, morts, XP, loot
7. Statuts (DoT, buffs), régénération, recharges
8. Mise à jour grille spatiale + dirty flags
9. Construction des snapshots/événements par client (cache d'encodage par cellule)
10. Envoi (buffers vers gateways) ; métriques du tick
```

### 2.3 ECS orienté données

- Stockage en **Structure of Arrays** (colonnes par composant) pour la localité cache.
- Composants principaux : `Transform`, `Velocity`, `Collider`, `Health`, `Resources`, `CombatStats` (compilé), `Cooldowns`, `Statuses`, `AiState`, `Owner`, `NetReplicated` (dirty mask), `PlayerLink`, `MoonState`.
- Entités recyclées (index + génération) ; **aucune allocation dans la boucle** : pools préalloués pour projectiles, zones, événements.

### 2.4 IA et monstres

- **Cellules actives** : seules les cellules à ≤ 2 cellules d'un joueur simulent l'IA ; les autres sont endormies (monstres figés, réapparitions différées). Une zone vide de joueurs ne consomme quasiment rien.
- Arbres de comportement compilés en tableaux (pas de pointeurs), évalués à fréquence réduite (10 Hz) ; mouvement à 30 Hz.
- Pathfinding : **champs de flux (flow fields)** par cible de joueur, recalculés à la demande sur la région active et partagés par tous les monstres qui poursuivent ce joueur ; A* sur grille pour les cas isolés, avec cache.
- Séparation (évitement entre monstres) via la grille, rayon court.

### 2.5 Collisions

- Monde : grille de tuiles (bitmask : bloquant, projectile-bloquant, sautable, eau).
- Entités : cercles ; requêtes via la grille spatiale.
- Même code de mouvement que le client (crate `sim-movement`, compilée aussi en WASM).

### 2.6 Instances et canaux

| Type | Capacité | Création |
|---|---|---|
| Zone ouverte (canal) | 120 joueurs max, ~1 500 monstres actifs max | Nouveau canal ouvert quand tous les canaux dépassent 80 % |
| Sanctuaire | 250 joueurs (pas de combat, AOI réduite, moins de monstres) | Idem |
| Donjon | 1–4 joueurs | À la demande, détruit 5 min après la sortie du dernier joueur |
| Arène de boss | 1–4 joueurs | À la demande |
| Événement mondial | Canal spécial | Planifié |

Placement (World Directory) : préférer le canal du groupe, puis des amis, puis le canal le plus
rempli sous 80 % (pour que le monde paraisse vivant), et répartir la charge entre machines.

## 3. Persistance

### 3.1 Principe

**La boucle de jeu ne touche jamais la base de données.**

| Donnée | Où elle vit pendant la session | Quand elle est écrite |
|---|---|---|
| Position, PV, combat, statuts, monstres, projectiles | Mémoire du game server | Jamais (position de reprise : au checkpoint) |
| XP, niveau, or, compteurs | Mémoire | Checkpoint toutes les 60 s, à la déconnexion, au changement de zone |
| Inventaire, équipement (ramassage, équipement) | Mémoire + file d'écriture | Écriture différée groupée (≤ 5 s) |
| Objets rareté ≥ 7, Soleils, Lunes | Mémoire + **écriture synchrone** | Immédiatement (transaction), avant annonce |
| Échanges, fusions, forge, dépenses importantes | — | **Transaction synchrone** hors boucle (tâche async), résultat renvoyé à l'instance |

### 3.2 Persistence Service

- Le game server publie des **commandes de persistance** versionnées (`CharacterCheckpoint`, `ItemsPicked`, …) dans une file (NATS JetStream, durable).
- Le Persistence Service les applique par lots (regroupement par personnage, `COPY`/`INSERT ... ON CONFLICT`), idempotentes (numéro de séquence par personnage).
- En cas de crash du game server : l'état perdu est au plus celui depuis le dernier checkpoint (≤ 60 s d'XP), jamais un objet rare. Les objets ramassés et non encore écrits sont dans la file durable.

### 3.3 Verrou de personnage

Un personnage ne peut être « possédé » que par une seule instance à la fois : bail (lease) dans Redis
`char_lock:{id}` renouvelé toutes les 10 s + numéro d'époque vérifié à chaque écriture SQL
(`WHERE epoch = $n`). Empêche la double connexion et la duplication par reconnexion concurrente.

## 4. Configuration

- `config/` versionné : équilibrage (taux, courbes, coûts), paramètres serveur (tick, AOI, limites).
- Rechargement à chaud : l'Admin API publie `config.updated {version}` ; chaque service charge, valide et bascule atomiquement au prochain tick. Journalisé dans l'audit.
- Feature flags pour activer progressivement les systèmes.

## Scaling

### 5.1 Axes

| Axe | Mécanisme |
|---|---|
| Joueurs par zone | Canaux (instances parallèles de la même zone) |
| Nombre total de joueurs | Plus de machines game server ; le World Directory répartit les instances |
| Connexions | Gateways horizontaux (1 gateway ≈ 20 000 connexions WS) |
| Services méta | Sans état → réplicas derrière le load balancer |
| Base de données | Primaire + réplicas en lecture ; pooling (PgBouncer) ; partitionnement des journaux ; plus tard sharding par `account_id` si nécessaire |
| Géographie | Régions serveur (EU, NA, ASIA) indépendantes pour le temps réel, comptes globaux |

### 5.2 Capacité estimée (à valider par les tests de charge)

| Élément | Hypothèse |
|---|---|
| Instance de zone chargée (120 joueurs, 1 500 monstres) | ≈ 5–8 ms CPU par tick → ~4 instances chargées par cœur |
| Machine 16 cœurs | ≈ 50 instances chargées ≈ 3 000–5 000 joueurs actifs |
| RAM | ≈ 2 Mo par instance + 50 Ko par joueur en jeu → < 2 Go pour 5 000 joueurs |
| Bande passante | 5 000 joueurs × 5 Ko/s ≈ 25 Mo/s ≈ 200 Mbit/s par machine |

### 5.3 Autoscaling

- Services sans état : HPA Kubernetes sur CPU et nombre de requêtes.
- Game servers : **Agones Fleet** avec buffer de serveurs prêts ; métrique = instances allouées / capacité ; montée proactive aux heures de pointe (planning) + réactive.
- Descente : une machine est drainée (plus de nouvelles instances, attente de la fin des donjons, transfert des canaux ouverts) avant arrêt — jamais d'éviction d'une partie en cours.

### 5.4 Chemin d'évolution

```text
Prototype : 1 VM, Docker Compose (game-server monolithique + Postgres + Redis)
Alpha     : 2–4 VM, services séparés, NATS, Prometheus/Grafana
Bêta      : Kubernetes managé, Agones, réplicas Postgres, CDN, WebTransport
Lancement : multi-régions, autoscaling planifié + réactif, bascule DB automatisée
```

### 5.5 Résilience

- Crash d'un game server : les joueurs sont reconnectés par le gateway sur une nouvelle instance de la même zone (état depuis le dernier checkpoint + file durable).
- Crash d'un gateway : le client se reconnecte (jeton de reprise), le personnage est toujours dans son instance (60 s de grâce).
- Redis perdu : présences et groupes reconstruits (heartbeats), classements restaurés depuis les instantanés PostgreSQL + rejeu du flux JetStream.
- PostgreSQL : réplication synchrone vers 1 réplica, sauvegardes continues (WAL archiving, PITR), tests de restauration mensuels.
