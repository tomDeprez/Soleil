# 17 — Objectifs de performance, benchmarks et plan de tests de charge

## 1. Objectifs mesurables

| Domaine | Objectif | Mesure |
|---|---|---|
| Client | 60 FPS, p99 frame < 20 ms, qualité Medium, GPU intégré récent, scène de référence « combat de groupe » | Scène de bench automatisée (Playwright + overlay) |
| Client (mémoire) | Allocations en combat ≈ 0 ; aucune pause GC > 2 ms | Profil Chrome automatisé (`performance.measureUserAgentSpecificMemory`, traces) |
| Gameplay | Latence input → retour visuel local < 1 frame (prédiction) ; input → confirmation serveur < RTT + 34 ms | Horodatages instrumentés |
| Serveur | Tick 30 Hz stable ; p99 tick d'instance chargée < 15 ms ; 0 dépassement en charge nominale | `sim_tick_duration_seconds` |
| Réseau | 3–6 Ko/s moyen par client, pic ≤ 15 Ko/s, plafond 32 Ko/s | `net_bytes_sent_total` par client |
| Base de données | 0 requête dans la boucle de tick ; p99 < 20 ms en charge nominale | `pg_stat_statements`, traces |
| Mémoire serveur | ≤ 50 Ko par joueur en jeu, ≤ 2 Mo par instance vide | `process_resident_memory_bytes` |
| Connexion | Entrée en jeu < 3 s après authentification (assets en cache) | Traces |

## 2. Benchmarks (CI)

| Bench | Outil | Contenu |
|---|---|---|
| Simulation | `criterion` | Tick d'une instance avec 120 joueurs bots + 1 500 monstres, déterministe |
| Grille spatiale | `criterion` | Insertion/déplacement/requête de voisinage, 10 000 entités |
| Encodage réseau | `criterion` | Construction de snapshots pour 120 clients, octets produits |
| Compétences | `criterion` | Compilation de loadout, exécution d'un graphe d'effets, déclencheurs en chaîne |
| Loot | `criterion` | 1 million de tirages |
| Décodage client | Vitest bench | Décodage de snapshots, zéro allocation (vérifié par compteur) |
| Rendu client | Playwright + Chromium | Scène de référence 60 s, FPS, frame times, draw calls |

Régression > 10 % par rapport à la référence de `main` ⇒ échec de CI.

## 3. Outil de charge : bots protocolaires

`tools/load-bots` (Rust) : client headless qui implémente le vrai protocole (même crate `protocol`),
sans rendu. Un processus simule des milliers de bots.

Comportements scriptés :

- **Farmer** : se déplace vers les packs, lance des compétences selon une rotation, ramasse.
- **Explorateur** : traverse les zones (tests de handoff, streaming AOI).
- **Social** : chat à cadence réaliste, invitations de groupe, échanges.
- **Boss** : groupe de 4 en arène.
- **Pathologique** : tous les bots au même point (pire cas AOI), spam de compétences à projectiles, spam de chat (rate limit), reconnexions en boucle.

Les bots mesurent : RTT, octets reçus, fréquence de snapshots, corrections de prédiction.

## 4. Scénarios

| # | Scénario | Question | Méthode |
|---|---|---|---|
| S1 | Montée progressive dans 1 instance de zone | **Joueurs max par instance** | +10 bots/30 s jusqu'à p99 tick > 25 ms |
| S2 | Densité de monstres croissante, joueurs fixes (60) | **Monstres max** | +200 monstres/30 s |
| S3 | Projectiles : 60 bots en spam de projectiles multiples | **Projectiles max** | Augmentation de la cadence |
| S4 | Pire cas AOI : 120 joueurs sur 1 cellule | Bande passante et encodage | Mesure Ko/s par client, accumulateur de priorité |
| S5 | Machine complète : N instances × charge nominale | **Joueurs par machine**, RAM, CPU | Ajout d'instances jusqu'à saturation |
| S6 | Plateforme : 10 000 → 50 000 bots, toutes zones, chat, groupes | Scalabilité globale, gateways, NATS, Redis, DB | Montée sur 1 h, plateau 2 h |
| S7 | Vague de connexion (« ouverture de serveur ») | Auth, World Directory, DB | 5 000 connexions en 60 s |
| S8 | Endurance | Fuites mémoire, dérive | 24 h à 70 % de charge |
| S9 | Chaos | Résilience | Arrêt brutal d'un game server / gateway / Redis / primaire DB pendant S6 |
| S10 | Économie concurrente | Anti-duplication | 1 000 bots en fusion/échange simultanés sur les mêmes objets |
| S11 | Client | **FPS** | Navigateur réel dans la scène S4 (120 joueurs, FX au maximum) par préréglage |

Critères de réussite S1–S5 : on retient comme **capacité officielle 70 %** de la valeur de saturation
mesurée (marge pour les pics). Ces capacités alimentent les seuils de création de canaux et l'autoscaling.

## 5. Mesures relevées pour chaque scénario

CPU (par cœur), RAM, bande passante entrante/sortante, latence (RTT, input → confirmation),
durée du tick (p50/p99/max), dépassements, octets par client, taille des messages, FPS (S11),
erreurs, retard de la file de persistance, latence DB.

## 6. Environnement

- Environnement de charge dédié (même type de machines qu'en production), recréé par Terraform.
- Bots répartis sur plusieurs machines et régions (latence réaliste, perte simulée via `tc netem` : 50–150 ms, 1 % de perte, gigue 20 ms).
- Résultats archivés (Grafana snapshots + rapport Markdown) pour suivre l'évolution à chaque jalon.

## 7. Cadence

| Moment | Tests |
|---|---|
| Chaque PR | Benchmarks CI |
| Chaque semaine (dès l'alpha) | S1–S5, S10, S11 |
| Avant chaque jalon | S6–S9 complets |
| Avant le lancement | S6 à 2× la charge prévue |
