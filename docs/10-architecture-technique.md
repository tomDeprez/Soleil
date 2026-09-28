# 10 — Architecture technique et choix technologiques

## 1. Contraintes qui guident les choix

| Contrainte | Conséquence technique |
|---|---|
| Temps réel, server authoritative | Boucle de simulation à tick fixe, langage sans pauses GC imprévisibles côté serveur |
| 60 FPS dans le navigateur | Rendu GPU batché (WebGL2/WebGPU), zéro allocation dans la boucle, travail hors thread principal |
| Milliers → dizaines de milliers de joueurs | Partitionnement par zones/instances, services sans état scalables, bus de messages |
| Bande passante minimale | Protocole binaire compact, interest management, deltas |
| Sécurité | Aucune logique décisionnelle client, transactions pour l'économie, TLS partout |
| Maintenabilité | Une source de vérité pour le protocole et les données de jeu, peu de langages, monorepo |
| Démarrage réaliste | Commencer avec quelques processus, évoluer sans réécriture |

## 2. Évaluation des technologies

| Technologie | Verdict | Justification |
|---|---|---|
| **TypeScript** | ✅ Client, admin | Seul choix mûr pour un client navigateur riche ; typage fort ; outillage (Vite, Vitest). Pas pour le game server (GC V8, mono-thread, coût mémoire par entité). |
| **WebGL2** | ✅ Base | Support universel desktop. Suffisant pour du 2D batché (dizaines de milliers de sprites). |
| **WebGPU** | ✅ Opportuniste | Utilisé si disponible via le moteur (compute pour particules), repli WebGL2 automatique. Ne pas en dépendre. |
| **Moteur 2D : PixiJS v8** | ✅ Retenu | Renderer le plus performant et le plus éprouvé en 2D web, batching automatique, WebGL2 + WebGPU, faible surcouche. Phaser ajoute une couche de jeu (physique, scènes) inutile : la logique est serveur. Un moteur maison WebGL coûterait des mois pour un gain marginal. |
| **WebSocket** | ✅ MVP | Disponible partout, passe les proxys, TLS natif. Limite : TCP (head-of-line blocking) ; atténuée par des messages petits et fréquents et l'absence de dépendance forte à chaque paquet. |
| **WebTransport** | ✅ Phase scaling | Datagrammes non fiables (UDP-like) pour les snapshots + flux fiables pour les événements. Chrome/Edge/Firefox ; Safari en repli WebSocket. Le protocole est conçu dès le départ pour tolérer la perte (deltas contre dernier ack). |
| **Rust** | ✅ Game server + services | Performances natives, pas de GC (latence de tick stable), mémoire compacte, sécurité mémoire (surface d'attaque réduite face à des paquets hostiles), excellent écosystème réseau (tokio, quinn, axum). Coût : courbe d'apprentissage, compensé par l'absence de bugs mémoire en production. |
| **Go** | ❌ Écarté | Très bon pour des services réseau, mais GC (pauses faibles mais non nulles, surtout avec des millions d'objets vivants), et un second langage backend doublerait les formules partagées. Serait un choix acceptable pour les services méta si l'équipe le maîtrise mieux. |
| **Java** | ❌ Écarté | JVM performante mais empreinte mémoire élevée par instance, GC à régler finement, démarrage lent pour l'autoscaling de game servers. |
| **Node.js serveur** | ❌ Écarté pour la simulation | Pratique pour partager le code TS, mais mono-thread, GC, coût CPU par entité ×3–10 par rapport à Rust. |
| **Redis (Valkey)** | ✅ | Sessions, présence, rate limiting, classements (sorted sets), groupes, recherche de groupe. Données chaudes et temporaires uniquement. |
| **PostgreSQL** | ✅ | Transactions ACID indispensables pour les objets, échanges, fusions ; JSONB pour les données flexibles ; réplication mature ; partitionnement natif pour les journaux. |
| **Cache** | ✅ Multi-niveaux | Données de jeu statiques en mémoire des processus (chargées au démarrage), état joueur en mémoire du game server pendant la session, Redis pour le partagé, CDN pour les assets. |
| **Bus de messages : NATS** | ✅ | Pub/sub à très faible latence, request/reply, sujets hiérarchiques (parfaits pour chat/présence/groupes), léger à opérer. JetStream pour les flux durables (événements de classement, audit). Kafka : surdimensionné et plus lourd à ce stade. |
| **Docker** | ✅ | Images reproductibles, Compose pour le développement et le premier déploiement. |
| **Kubernetes** | ⏳ Plus tard | Nécessaire au-delà de quelques machines : autoscaling des services sans état. Pour les game servers, **Agones** (allocation, cycle de vie, pas d'éviction en cours de partie). Pas avant la phase de scaling. |
| **Protocol Buffers / JSON** | ❌ dans la boucle | JSON : trop gros et lent. Protobuf : pas de bit-packing ni de quantification. → protocole binaire maison, schéma unique, code généré (voir réseau). JSON seulement pour l'API REST méta. |

## 3. Vue d'ensemble

```text
                              ┌────────────────────── CDN ──────────────────────┐
                              │ client JS/wasm, atlas, audio, données de contenu │
                              └──────────────────────────────────────────────────┘
 Navigateur ──HTTPS──► API Gateway (axum) ──► Auth Service ──► PostgreSQL
     │                        │            ──► Social / Leaderboard / Market (REST)
     │                        │
     └──WSS / WebTransport──► Edge Gateway (terminaison TLS, auth jeton, routage, rate limit)
                                   │  QUIC/TCP interne, messages multiplexés
                                   ▼
                     ┌────────── Game Servers (Rust) ──────────┐
                     │ Zone A canal 1 │ Zone A canal 2 │ Donjon │   (instances de simulation)
                     └───────┬───────────────┬──────────────────┘
                             │ NATS (événements, chat, présence, groupes)
         ┌───────────────────┼─────────────────────────────┬──────────────────┐
     Chat Service     World Directory / Orchestrateur    Persistence Service   Leaderboard Service
         │                   │                              │                        │
       Redis ◄───────────────┴──────────────────────────────┤                      Redis
                                                        PostgreSQL (primaire + réplicas)
     Observabilité : OpenTelemetry Collector → Prometheus / Loki / Tempo → Grafana + Alertmanager
     Admin Panel (React/TS) → Admin API (RBAC, audit)
```

## 4. Modules du projet

| Module | Rôle | Technologie |
|---|---|---|
| `client` | Rendu, interface, audio, prédiction, interpolation | TypeScript, PixiJS, Vite |
| `backend/api` | API HTTP méta (comptes, inventaire hors jeu, amis, classements, paramètres) | Rust, axum |
| `backend/auth` | Authentification, sessions, jetons | Rust, argon2, JWT EdDSA |
| `backend/game-server` | Simulation autoritaire des zones et instances | Rust, tokio, ECS maison |
| `backend/gateway` | Terminaison des connexions temps réel, routage vers game servers | Rust, tokio-tungstenite, quinn |
| `backend/chat` | Chat, modération | Rust, NATS |
| `backend/social` | Amis, blocages, groupes, guildes, présence | Rust, NATS, Redis |
| `backend/matchmaking` | Placement en canaux, files de donjon | Rust (dans le World Directory au début) |
| `backend/persistence` | Écriture différée et transactionnelle des états joueurs | Rust, sqlx |
| `backend/leaderboard` | Consommation d'événements, sorted sets | Rust, Redis |
| `shared/protocol` | Schéma du protocole + code généré Rust/TS | DSL maison → codegen |
| `shared/game-data` | Types et formules partagés (stats, dégâts, courbes) | Rust (+ exposés en TS générés) |
| `content` | Données de jeu : compétences, objets, monstres, zones, loot | Fichiers RON/TOML validés en CI |
| `assets` | Sprites sources, atlas générés, audio, cartes (Tiled) | Pipeline Aseprite → atlas |
| `config` | Équilibrage, taux, paramètres serveur rechargeables | TOML versionné |
| `admin` | Panneau d'administration | TypeScript, React |
| `infra` | Docker, Compose, Kubernetes, Terraform, dashboards | YAML, HCL |
| `monitoring` | Dashboards Grafana, règles d'alertes | JSON/YAML |
| `tools` | Bots de charge, simulateur de DPS, outils d'équilibrage | Rust, Python |

### Arborescence cible

```text
soleil/
├── client/                 # jeu navigateur
│   ├── src/{core,net,render,ecs,ui,audio,input,assets,workers}
│   └── public/
├── admin/                  # panneau admin
├── backend/                # workspace Cargo
│   ├── game-server/  gateway/  api/  auth/  chat/  social/  persistence/  leaderboard/
│   └── crates/{protocol,game-data,sim,spatial,netcode,persistence-model,telemetry}
├── shared/protocol/schema/ # définition du protocole → codegen Rust + TS
├── content/                # données de jeu
├── assets/                 # sources d'art et audio
├── config/                 # configuration d'équilibrage et serveurs
├── infra/                  # docker, compose, k8s, terraform
├── monitoring/             # grafana, prometheus rules, loki
├── tools/                  # load-bots, balance, pipeline d'assets
└── docs/                   # ce dossier
```

## 5. Évolution progressive de l'architecture

Ne pas construire l'infrastructure finale d'emblée.

| Étape | Déploiement | Capacité visée |
|---|---|---|
| **Prototype (vertical slice)** | 1 binaire `game-server` (gateway + simulation + chat simple intégrés), 1 PostgreSQL, 1 Redis, Docker Compose | 100–200 joueurs |
| **Alpha** | Gateway séparé, game servers multiples, NATS, chat et social en services, Prometheus/Grafana | 1 000–2 000 |
| **Bêta** | Plusieurs machines, réplicas PostgreSQL en lecture, World Directory, WebTransport, CDN | 5 000–10 000 |
| **Lancement** | Kubernetes + Agones, plusieurs régions serveur (EU/NA/ASIA), autoscaling | 10 000–50 000+ |

Les frontières de modules existent **dès le prototype** (crates séparées, interfaces), ce qui permet
de sortir un module en service sans réécrire sa logique.

## 6. Source unique de vérité

- **Protocole** : un schéma (`shared/protocol/schema/*.proto.ron`) génère les encodeurs/décodeurs Rust et TypeScript. Le hash du schéma est échangé au handshake : versions incompatibles refusées proprement.
- **Contenu** : `content/` est compilé par un outil (`tools/content-compiler`) en un paquet binaire versionné, chargé par le serveur et, pour la partie visible, téléchargé par le client (par région, voir streaming).
- **Formules** : implémentées une fois en Rust (`crates/game-data`). Le client n'a besoin que des formules d'affichage (infobulles estimées) ; les valeurs exactes lui sont envoyées par le serveur.

## 7. Qualité et CI

- CI : `cargo clippy`, `cargo test`, `cargo fmt --check`, tests TypeScript, lint, validation du contenu, build des atlas, tests de protocole croisés (encodage Rust → décodage TS).
- Tests de simulation déterministes (même seed + mêmes inputs ⇒ même état) : la simulation n'utilise que des RNG seedés et un pas fixe.
- Bench automatisés (voir [17](17-performance-tests-charge.md)) : régression de performance > 10 % = échec de CI.
