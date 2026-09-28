# 16 — Monitoring et administration

## 1. Pile d'observabilité

```text
Services Rust ──(OpenTelemetry SDK)──► OTel Collector ──► Prometheus (métriques)
Client (télémétrie échantillonnée) ──► API /telemetry ─┘  ├──► Loki (logs)
PostgreSQL ── postgres_exporter ─────► Prometheus         ├──► Tempo (traces)
Redis ── redis_exporter ─────────────► Prometheus         └──► Grafana (dashboards) + Alertmanager
NATS ── exporter intégré ────────────► Prometheus                     └──► Discord/Slack/PagerDuty
Nœuds ── node_exporter / cAdvisor ───► Prometheus
```

- **Tempo** plutôt que Jaeger : même rôle (traces distribuées), stockage objet peu coûteux, intégration native Grafana (liens logs ↔ traces ↔ métriques). Jaeger reste compatible via OTLP si préféré.
- Traces uniquement sur les chemins méta (connexion, fusion, échange, persistance) et échantillonnées ; **pas de span par tick** (coût). Le tick est mesuré par histogrammes.
- Cardinalité maîtrisée : labels par service, instance, zone — jamais par joueur.

## 2. Métriques

### Serveurs

| Métrique | Nom Prometheus |
|---|---|
| CPU / RAM / réseau | `process_cpu_seconds_total`, `process_resident_memory_bytes`, `node_network_*` |
| Connexions | `gateway_connections{transport}` |
| Tick rate effectif | `sim_ticks_total{instance}` (rate) |
| Durée du tick | `sim_tick_duration_seconds{zone}` (histogramme, p50/p99) et par phase `sim_phase_duration_seconds{phase}` |
| Ticks en retard | `sim_tick_overrun_total` |
| Latence (RTT) | `net_rtt_seconds` (histogramme) |
| Erreurs | `errors_total{service,kind}` |
| Charge par instance | `instance_players`, `instance_entities`, `instance_load_ratio` |

### Jeu

| Métrique | Nom |
|---|---|
| FPS client (p50/p99) | `client_fps_bucket` (télémétrie agrégée) |
| Ping | `net_rtt_seconds` |
| Temps de réponse des requêtes | `request_duration_seconds{op}` (fusion, échange, équipement…) |
| Joueurs | `players_online{region}` |
| Monstres | `monsters_active{zone}` |
| Projectiles | `projectiles_active{zone}` |
| Événements | `game_events_total{kind}` |
| Durée moyenne des combats | `combat_duration_seconds{kind=elite|boss}` |
| Économie | `currency_flow_total{currency,reason,direction}`, `items_created_total{rarity}` |
| Déclencheurs coupés (budget) | `triggers_dropped_total` |

### Base de données

CPU, RAM, requêtes/s, durée moyenne et p99 par requête (`pg_stat_statements`), connexions actives/en attente (PgBouncer), erreurs, deadlocks, retard de réplication, taille des tables, bloat.

### Réseau

`net_bytes_sent_total{msg_type}`, `net_bytes_received_total`, `net_packets_*`, `net_message_size_bytes` (histogramme), `net_full_snapshots_total`, `net_priority_skipped_total`, `net_datagram_loss_ratio` (WebTransport).

## 3. Dashboards Grafana (versionnés dans `monitoring/`)

1. **Vue globale** : joueurs en ligne par région, instances, erreurs, alertes actives.
2. **Game servers** : durée de tick par zone (heatmap), dépassements, CPU/RAM par instance, entités.
3. **Réseau** : Ko/s par client (distribution), taille des messages par type, RTT, pertes.
4. **Base de données** : latence, connexions, requêtes lentes, réplication.
5. **Économie** : création/destruction de monnaie et d'objets par rareté, anomalies.
6. **Client** : FPS par qualité/GPU/navigateur, temps de chargement.
7. **Sécurité** : échecs de connexion, rejets de validation, scores d'anomalie.

## 4. Alertes

| Alerte | Condition | Sévérité |
|---|---|---|
| Tick lent | p99 `sim_tick_duration_seconds` > 25 ms pendant 2 min | Critique |
| Dépassements | `sim_tick_overrun_total` > 1 % des ticks sur 5 min | Haute |
| Latence DB | p99 > 100 ms pendant 5 min | Haute |
| File de persistance | Retard > 30 s | Critique |
| Réplication | Retard > 10 s | Haute |
| Erreurs | Taux d'erreurs > 1 % des requêtes | Haute |
| Économie | Création de monnaie > 3 σ de la normale horaire | Haute (possible exploit) |
| Objets rareté 9 | > N par heure (configurable) | Haute |
| Connexions | Chute > 20 % en 1 min | Critique (panne) |
| Capacité | Instances > 85 % de capacité régionale | Moyenne (scaling) |

Chaque alerte renvoie vers un runbook (`docs/runbooks/…`, à écrire pendant l'alpha).

## Administration

### 5. Panneau d'administration

Application séparée (`admin/`, TypeScript + React), servie sur un domaine distinct, accessible
uniquement via SSO + MFA obligatoire, liste d'IP autorisées ou VPN, sessions courtes.

| Fonctionnalité | Rôle minimal | Détails |
|---|---|---|
| Joueurs connectés | moderator | Liste filtrable (région, zone, niveau), temps réel via NATS |
| Serveurs et instances | admin | Liste, charge, joueurs, tick, drain/fermeture d'instance |
| Performances | admin | Dashboards Grafana intégrés (iframe authentifiée) |
| Recherche de joueur | moderator | Par nom, compte, email (email masqué sauf gm+) |
| Inventaire et objets | gm | Lecture ; historique `item_event` ; restauration d'un objet détruit avec justification obligatoire |
| Statistiques d'un joueur | moderator | Progression, stats cumulées, score d'anomalie |
| Logs | admin | Recherche Loki filtrée, lien vers traces |
| Sanctions | moderator (mute), admin (ban) | Mute, ban temporaire/permanent, blocage d'échanges, masquage de classement ; motifs prédéfinis ; historique |
| Signalements | moderator | File, contexte capturé, décision |
| Événements | admin | Lancer/planifier un événement mondial, annonce système |
| Configuration | admin | Édition des paramètres rechargeables (taux, bonus) avec diff, validation et **double validation** pour les valeurs sensibles (taux de Soleil, XP) |
| Statistiques globales | admin | Joueurs, rétention, répartition des évolutions/builds, économie |

### 6. Journalisation des actions

- Chaque action passe par l'Admin API, qui écrit dans `admin_audit` **dans la même transaction** que l'effet (pas d'action sans trace).
- Contenu : acteur, action, cible, charge utile avant/après, justification, IP, horodatage.
- Table append-only (droits `UPDATE/DELETE` révoqués), export quotidien vers stockage immuable.
- Les joueurs sanctionnés voient le motif et la durée ; procédure d'appel.

### 7. Sécurité du panneau

- Aucune action d'administration depuis le client de jeu.
- Actions destructrices (ban permanent, suppression, modification de configuration économique) : confirmation + justification, et pour les plus sensibles, validation par un second admin.
- Tokens staff à durée courte, révocation immédiate au départ d'un membre.
