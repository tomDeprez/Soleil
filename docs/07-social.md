# 07 — Systèmes sociaux : groupes, amis, guildes, chat, classements

Services concernés (voir [12](12-architecture-serveur.md)) : **Social Service** (amis, blocages,
guildes, présence), **Chat Service**, **Leaderboard Service**, et le **Game Server** pour la
logique de groupe en jeu.

## Groupes

### 1. Fonctionnement

- 1 à **4** joueurs. Chef de groupe : invite, expulse, transfère, choisit les règles.
- Invitation par nom, depuis la liste d'amis, le chat, ou via la **Recherche de groupe**.
- Les membres peuvent être dans des canaux différents : le groupe force leur regroupement dans le même canal lorsqu'ils se rejoignent dans une zone (voir serveur, placement).
- Donjons et arènes instanciés au nom du groupe.

### 2. XP de groupe

Bonus d'XP par membre **à portée** (≤ 40 tuiles et même zone) :

| Membres à portée | XP totale générée | Part de chacun (niveaux égaux) |
|---|---|---|
| 1 | 100 % | 100 % |
| 2 | 125 % | 62,5 % |
| 3 | 150 % | 50 % |
| 4 | 180 % | 45 % |

En groupe, la densité et la vitesse de kill augmentent (× 2 à × 3), donc chaque joueur gagne plus
qu'en solo (≈ +20 à +40 %) sans rendre le solo inutile (le solo garde 100 % de chaque kill et la liberté).

Répartition entre niveaux différents : pondérée par `niveau^2` des membres à portée
(le haut niveau prend une part plus grande de l'XP du groupe).

### 3. Aider un joueur bas niveau sans power leveling abusif

| Mécanique | Effet |
|---|---|
| **Synchronisation (Mentor)** | Un joueur de niveau ≥ zone + 10 peut se synchroniser au niveau de la zone : stats ramenées au niveau de zone + 2, compétences et Soleils plafonnés. En échange : récompenses de mentor (monnaie cosmétique, loot adapté à son niveau réel). C'est la voie **encouragée**. |
| **Écart de niveau** | Si un membre non synchronisé dépasse le niveau du monstre de 10+, l'XP du kill est divisée par 4 pour **tout le groupe** (le kill est « trivial »). |
| **Contribution minimale** | Pour recevoir de l'XP, un membre doit avoir contribué (dégâts, soins, bouclier, contrôle) dans les 15 dernières secondes sur un monstre du même combat, ou être à ≤ 15 tuiles. Un joueur AFK suivi ne reçoit rien. |
| **Plafond de gain** | L'XP par kill reçue par un joueur ne peut dépasser l'XP d'un monstre de son propre niveau + 4 (pas de « monstres niveau 80 » tués pour un niveau 20). |
| **Donjons** | Le niveau du donjon est fixé à l'entrée par le niveau du membre le plus bas (+2) ; un haut niveau non synchronisé désactive le bonus de complétion. |
| **Détection** | Métrique « XP/h par tranche de niveau » ; au-delà de 3 × la médiane pendant 1 h, signalement automatique pour revue (pas de sanction automatique). |

### 4. Loot en groupe

Loot personnel (chacun le sien, voir [03](03-loot-objets-fusion.md)) : pas de conflit, pas de ninja-loot.
Les objets échangeables peuvent être donnés aux membres du groupe présents lors du drop pendant 2 h (même s'ils sont liés).

### 5. Recherche de groupe

- Annonces : activité (zone, donjon, boss), niveau min, rôle recherché (tags d'évolution), langue, micro.
- Stockage : Redis (TTL 30 min, index par activité et région serveur).
- Matchmaking automatique optionnel pour les donjons : file par (donjon, région serveur, tranche de niveau), formation lorsque 4 joueurs ou 2 minutes (groupe partiel proposé).

### 6. Données et architecture

```text
Party (état temporaire, en mémoire du Social Service + Redis) {
  party_id, leader_id, members[{character_id, zone_id, instance_id, level, synced}], settings, created_at
}
```

Les groupes ne sont pas persistés en SQL (état temporaire). Redis contient l'état du groupe
(clé `party:{id}`, hash) et chaque game server concerné s'abonne au sujet NATS `party.{id}` pour
les mises à jour. Le game server reçoit la composition pour appliquer XP, portée et partage.

## Amis

### 1. Fonctionnement

- Demande → acceptation (bidirectionnel). Limite : 200 amis.
- Statut : en ligne / absent / occupé / hors ligne / invisible ; zone et activité visibles par les amis (paramètre de confidentialité).
- Notes personnelles sur un ami, favoris.
- **Blocage** : unilatéral, prioritaire sur tout (chat, invitations, échanges, demandes, visibilité de statut). Limite 500.
- Invitations de groupe et de guilde depuis la liste.

### 2. Données

```text
friendship    (account_a, account_b, state: pending|accepted, requested_by, created_at)  -- a < b
block         (blocker_id, blocked_id, created_at)
presence      Redis hash presence:{account_id} → { status, character_id, zone, updated_at } TTL 90 s
```

La présence est rafraîchie par le gateway (heartbeat 30 s). Les changements sont diffusés en push
aux amis connectés via NATS (`presence.{account_id}`), jamais par polling.

## Guildes

- 5 à 200 membres, rangs personnalisables (permissions : inviter, expulser, annoncer, gérer le coffre).
- Coffre de guilde : transactions journalisées, permissions par rang.
- Niveau de guilde (activités cumulées) : bonus cosmétiques et d'emblème, **pas** de puissance de combat.
- Classement de guilde (boss tués, collection cumulée, saison).

```text
guild         (id, name unique, tag, emblem jsonb, level, xp, created_at)
guild_member  (guild_id, character_id, rank_id, joined_at)
guild_rank    (guild_id, rank_id, name, permissions bitmask)
guild_bank_log(id, guild_id, character_id, action, item_id?, amount?, at)
```

## Chat

### 1. Canaux

| Canal | Portée | Transport | Persistance |
|---|---|---|---|
| Global | Tous les joueurs d'une **région serveur** (EU, NA, ASIA) et d'une langue | NATS `chat.global.{region}.{lang}` | 24 h (modération) |
| Région | Joueurs d'une même région de jeu (ex. Forêt des Murmures), tous canaux | NATS `chat.zone.{region_id}` | 24 h |
| Groupe | Membres du groupe | `chat.party.{id}` | Durée du groupe |
| Guilde | Membres de la guilde | `chat.guild.{id}` | 30 jours |
| Privé | 1 à 1 | `chat.dm.{account_id}` | 30 jours |
| Système | Serveur → joueur(s) | Émis par les services | Non |

Le global « mondial » est découpé par région serveur et par langue pour rester lisible et scalable ;
un canal « Monde » unique est réservé aux annonces système (drops Primordiaux, événements).

### 2. Architecture

```text
Client ──WS──► Gateway ──NATS request──► Chat Service ──► filtres ──► NATS publish chat.<canal>
                                                                     │
Gateways abonnés aux sujets de leurs clients ◄───────────────────────┘ ──► push aux clients concernés
                                           Chat Service ──► Postgres (batch, historique modération)
```

- Le Chat Service est **sans état** (hors caches), scalable horizontalement.
- Chaque gateway ne s'abonne qu'aux sujets pertinents pour ses clients connectés (abonnement dynamique).
- Messages : max 256 caractères, UTF-8 normalisé NFC, caractères de contrôle et zéro-largeur retirés.

### 3. Modération et protection

| Mécanisme | Détail |
|---|---|
| Rate limiting | Token bucket par compte et par canal (Redis) : Global 1 msg / 10 s, Région 1 msg / 3 s, autres 5 msg / 5 s en rafale |
| Anti-spam | Détection de répétition (hash des 10 derniers messages), similarité, liens bloqués sauf liste blanche, majuscules excessives |
| Filtrage | Liste de mots par langue, configurable ; mode « masquer » ou « bloquer » ; filtre de grossièretés côté client optionnel (préférence) |
| Comptes récents | Pas de Global avant le niveau 5 et 2 h de jeu (anti-bots) |
| Mute | Temporaire ou permanent, par canal ou total, posé par modérateur ou automatiquement (score de spam) |
| Block | Les messages d'un joueur bloqué sont filtrés **côté serveur** (le gateway ne les transmet pas) |
| Signalement | Clic droit → signaler : capture serveur des 20 derniers messages du contexte, file de modération |
| Journalisation | Tous les messages Global/Région/signalés conservés 24 h–30 j pour modération (RGPD : durée limitée, documentée) |

## Classements

### 1. Catégories

| Classement | Métrique | Période |
|---|---|---|
| Niveau / XP | XP totale (départage : horodatage d'atteinte) | Permanent + saison |
| Rangs d'Apogée | XP post-90 | Saison |
| Boss tués | Nombre par boss et total | Permanent + hebdo |
| Temps de boss | Meilleur temps par boss, solo et groupe (par taille) | Saison |
| Progression | Premier à atteindre un palier (niveau 60/90, premier kill de boss) | Permanent (« Premiers mondiaux ») |
| Collection | Points de Codex (objets uniques, montures, conjonctions) | Permanent |
| Objets rares | Points pondérés des raretés 7–9 obtenues | Permanent + saison |
| Soleils | Soleils distincts + étoiles d'Ascension | Permanent |
| Lunes | Lunes distinctes + conjonctions découvertes | Permanent |
| PvE (score composite) | Formule saisonnière publique | Saison |
| Guildes | Somme de contributions | Saison |

Filtres : région serveur, évolution (pour les temps de boss), amis, guilde.

### 2. Architecture

- **Redis sorted sets** : `lb:{catégorie}:{période}:{filtre}` → score, membre = character_id. Lecture top N et rang d'un joueur en O(log n).
- Scores **écrits uniquement par les services serveur** suite à des événements validés (`BossKilled`, `LevelUp`, `ItemObtained`) publiés sur NATS et consommés par le Leaderboard Service. Aucune API client n'écrit un score.
- Scores composites encodés pour départager : `score = valeur × 2^21 + (2^21 − secondes_depuis_début_saison / 4)` (exact en double tant que `valeur < 2^32` ; les métriques plus grandes, comme les Rangs d'Apogée, sont divisées par une unité de palier avant encodage).
- Instantané quotidien et fin de saison en PostgreSQL (`leaderboard_snapshot`) pour l'historique et la reconstruction si Redis est perdu.
- Temps de boss : mesurés par le game server (ticks entre l'engagement et la mort), enregistrés avec l'ID de replay d'événements (journal des inputs de combat conservé 7 jours pour les tops 100) pour audit.

### 3. Sécurité

- Détection d'anomalies : progression impossible (XP/h, temps de boss sous un seuil théorique calculé par le simulateur de DPS) → mise en quarantaine du score (masqué) en attente de revue.
- Les modérateurs peuvent retirer une entrée (action journalisée).

### 4. Performance

- Top 100 mis en cache 10 s ; rang individuel à la demande.
- Mise à jour par lot (pipeline Redis) toutes les secondes depuis le flux d'événements.
