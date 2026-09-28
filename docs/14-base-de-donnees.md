# 14 — Base de données, modèle personnage, modèle objet

## 1. Séparation des données

| Catégorie | Stockage | Exemples |
|---|---|---|
| **Persistantes** | PostgreSQL | Comptes, personnages, niveau, XP, inventaire, objets, runes, Soleils, Lunes, montures, amis, progression, statistiques, journaux |
| **Chaudes partagées** | Redis | Sessions, présence, groupes, recherche de groupe, rate limiting, classements, verrous de personnage |
| **Temporaires temps réel** | Mémoire du game server | Positions, combat, monstres, projectiles, statuts, événements, état de zone, phase des Lunes |
| **Statiques** | Fichiers de contenu compilés (mémoire) | Définitions de compétences, objets de base, monstres, tables de loot |

Aucune donnée temps réel n'est écrite en continu en SQL (voir [12 §3](12-architecture-serveur.md)).

## 2. Schéma PostgreSQL

Conventions : identifiants `uuid` (v7, triables par date) pour les entités créées à haut débit,
`bigint` pour les monnaies/XP, horodatages `timestamptz`, colonne `version` pour le verrouillage optimiste.

```sql
-- ============ Comptes et sécurité ============
CREATE TABLE account (
  id              uuid PRIMARY KEY,
  email           citext UNIQUE NOT NULL,
  password_hash   text NOT NULL,                 -- argon2id
  display_name    citext UNIQUE NOT NULL,
  region          text NOT NULL,                 -- EU / NA / ASIA
  role            text NOT NULL DEFAULT 'player',-- player | moderator | gm | admin
  mfa_secret      bytea,                         -- chiffré (obligatoire pour les rôles staff)
  status          text NOT NULL DEFAULT 'active',-- active | suspended | banned
  created_at      timestamptz NOT NULL DEFAULT now(),
  last_login_at   timestamptz
);

CREATE TABLE session (
  id              uuid PRIMARY KEY,
  account_id      uuid NOT NULL REFERENCES account(id),
  refresh_hash    bytea NOT NULL,                -- hash du refresh token (rotation)
  ip              inet, user_agent text,
  created_at      timestamptz NOT NULL DEFAULT now(),
  expires_at      timestamptz NOT NULL,
  revoked_at      timestamptz
);

CREATE TABLE account_settings (
  account_id      uuid PRIMARY KEY REFERENCES account(id),
  schema_version  int NOT NULL,
  settings        jsonb NOT NULL,                -- graphismes, audio, gameplay, contrôles
  updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE sanction (
  id              bigserial PRIMARY KEY,
  account_id      uuid NOT NULL REFERENCES account(id),
  kind            text NOT NULL,                 -- mute | ban | trade_lock | leaderboard_hide
  scope           text,                          -- canal de chat, etc.
  reason          text NOT NULL,
  issued_by       uuid REFERENCES account(id),
  starts_at       timestamptz NOT NULL DEFAULT now(),
  ends_at         timestamptz,                   -- NULL = permanent
  revoked_at      timestamptz
);

-- ============ Personnage ============
CREATE TABLE character (
  id              uuid PRIMARY KEY,
  account_id      uuid NOT NULL REFERENCES account(id),
  name            citext UNIQUE NOT NULL,
  realm           text NOT NULL DEFAULT 'permanent', -- permanent | season_N
  level           smallint NOT NULL DEFAULT 1 CHECK (level BETWEEN 1 AND 90),
  xp              bigint NOT NULL DEFAULT 0,
  apex_xp         bigint NOT NULL DEFAULT 0,     -- XP post-90
  gold            bigint NOT NULL DEFAULT 0 CHECK (gold >= 0),
  star_dust       bigint NOT NULL DEFAULT 0 CHECK (star_dust >= 0),
  rune_dust       bigint NOT NULL DEFAULT 0 CHECK (rune_dust >= 0),
  moon_shards     bigint NOT NULL DEFAULT 0 CHECK (moon_shards >= 0),
  primary_stats   jsonb NOT NULL,                -- {str, agi, int, vig, spi, unspent}
  active_evolution smallint,                     -- NULL avant le niveau 15
  zone_id         int NOT NULL, pos_x real NOT NULL, pos_y real NOT NULL, -- point de reprise
  appearance      jsonb NOT NULL,
  epoch           bigint NOT NULL DEFAULT 0,     -- incrémenté à chaque prise de possession (anti double session)
  version         bigint NOT NULL DEFAULT 0,
  created_at      timestamptz NOT NULL DEFAULT now(),
  last_saved_at   timestamptz NOT NULL DEFAULT now(),
  deleted_at      timestamptz
);
CREATE INDEX ON character(account_id);

CREATE TABLE character_evolution (
  character_id    uuid REFERENCES character(id),
  evolution_id    smallint,
  unlocked_at     timestamptz NOT NULL,
  mastery_xp      bigint NOT NULL DEFAULT 0,
  allocation      jsonb NOT NULL,                -- {skill_id: [upgrade_ids]}, validé serveur
  unique_facets   jsonb NOT NULL,                -- {unique_skill_id: facet}
  loadouts        jsonb NOT NULL,                -- jusqu'à 3 barres Q W E R T D F
  active_loadout  smallint NOT NULL DEFAULT 0,
  PRIMARY KEY (character_id, evolution_id)
);

CREATE TABLE character_progress (             -- quêtes, découvertes, succès
  character_id    uuid REFERENCES character(id),
  kind            text, key text,
  value           jsonb NOT NULL,
  updated_at      timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (character_id, kind, key)
);

CREATE TABLE character_stats (                -- statistiques cumulées (classements, profil)
  character_id    uuid PRIMARY KEY REFERENCES character(id),
  monsters_killed bigint NOT NULL DEFAULT 0,
  elites_killed   bigint NOT NULL DEFAULT 0,
  deaths          bigint NOT NULL DEFAULT 0,
  play_seconds    bigint NOT NULL DEFAULT 0,
  distance_m      bigint NOT NULL DEFAULT 0,
  extra           jsonb NOT NULL DEFAULT '{}'
);

-- ============ Objets ============
CREATE TABLE item (
  id              uuid PRIMARY KEY,
  owner_character uuid REFERENCES character(id),
  owner_account   uuid REFERENCES account(id),   -- pour le coffre de compte
  guild_id        uuid,                          -- pour le coffre de guilde
  location        text NOT NULL,                 -- inventory | equipped | stash | guild_bank | trade_escrow | mail
  slot            smallint,                      -- position dans le conteneur / emplacement d'équipement
  base_id         int NOT NULL,
  rarity          smallint NOT NULL CHECK (rarity BETWEEN 1 AND 9),
  ilvl            smallint NOT NULL,
  quality         smallint NOT NULL DEFAULT 0,
  seed            bigint NOT NULL,
  affixes         jsonb NOT NULL,                -- [{affix_id, tier, value}]
  powers          jsonb NOT NULL DEFAULT '[]',   -- pouvoirs légendaires / fusionnés
  sockets         jsonb NOT NULL DEFAULT '[]',   -- [{color, rune_family?, rune_level?}]
  binding         text NOT NULL DEFAULT 'none',  -- none | on_trade_once | account
  trades_left     smallint,
  durability      smallint NOT NULL DEFAULT 100,
  locked          boolean NOT NULL DEFAULT false,-- verrou joueur (anti-démontage accidentel)
  origin          jsonb NOT NULL,                -- {source: drop|fusion|forge|admin, monster/boss, zone, at}
  version         bigint NOT NULL DEFAULT 0,
  created_at      timestamptz NOT NULL DEFAULT now(),
  destroyed_at    timestamptz,                   -- soft delete
  destroyed_reason text,                         -- fused | salvaged | sold | admin
  CHECK (num_nonnulls(owner_character, owner_account, guild_id) = 1 OR destroyed_at IS NOT NULL)
);
CREATE INDEX ON item(owner_character) WHERE destroyed_at IS NULL;
CREATE UNIQUE INDEX item_slot_unique ON item(owner_character, location, slot) WHERE destroyed_at IS NULL AND owner_character IS NOT NULL;

CREATE TABLE rune_stack (
  character_id    uuid REFERENCES character(id),
  family_id       smallint, level smallint CHECK (level BETWEEN 1 AND 8),
  quantity        int NOT NULL CHECK (quantity >= 0),
  PRIMARY KEY (character_id, family_id, level)
);

CREATE TABLE sun_owned (
  account_id uuid REFERENCES account(id), sun_id smallint,
  stars smallint NOT NULL DEFAULT 0 CHECK (stars BETWEEN 0 AND 5),
  obtained_at timestamptz NOT NULL, source text NOT NULL,
  PRIMARY KEY (account_id, sun_id)
);
CREATE TABLE sun_slot (character_id uuid REFERENCES character(id), slot smallint CHECK (slot BETWEEN 1 AND 5), sun_id smallint, PRIMARY KEY (character_id, slot));

CREATE TABLE moon_owned (
  id uuid PRIMARY KEY, account_id uuid NOT NULL REFERENCES account(id),
  moon_def_id smallint NOT NULL, level smallint NOT NULL DEFAULT 1 CHECK (level BETWEEN 1 AND 10),
  obtained_at timestamptz NOT NULL, source text NOT NULL, destroyed_at timestamptz
);
CREATE TABLE moon_orbit (character_id uuid REFERENCES character(id), slot smallint CHECK (slot BETWEEN 0 AND 5), moon_id uuid UNIQUE REFERENCES moon_owned(id), PRIMARY KEY (character_id, slot)); -- slot 0 = orbite libre
CREATE TABLE conjunction_discovery (account_id uuid, conjunction_id int, discovered_at timestamptz NOT NULL, PRIMARY KEY (account_id, conjunction_id));

CREATE TABLE boss_progress (
  account_id uuid REFERENCES account(id), boss_id smallint,
  kills bigint NOT NULL DEFAULT 0, kills_since_sun bigint NOT NULL DEFAULT 0,
  shards int NOT NULL DEFAULT 0 CHECK (shards >= 0),
  best_time_ms int, weekly_bonus_at timestamptz,
  PRIMARY KEY (account_id, boss_id)
);

CREATE TABLE mount_owned (
  account_id uuid REFERENCES account(id), mount_def_id smallint,
  level smallint NOT NULL DEFAULT 1, distance_m bigint NOT NULL DEFAULT 0,
  customization jsonb NOT NULL DEFAULT '{}', obtained_at timestamptz NOT NULL,
  PRIMARY KEY (account_id, mount_def_id)
);

-- ============ Social ============
CREATE TABLE friendship (account_a uuid, account_b uuid, state text NOT NULL, requested_by uuid NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY (account_a, account_b), CHECK (account_a < account_b));
CREATE TABLE block (blocker_id uuid, blocked_id uuid, created_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY (blocker_id, blocked_id));
CREATE TABLE guild (id uuid PRIMARY KEY, name citext UNIQUE NOT NULL, tag citext UNIQUE NOT NULL, emblem jsonb, level smallint NOT NULL DEFAULT 1, xp bigint NOT NULL DEFAULT 0, created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE guild_rank (guild_id uuid REFERENCES guild(id), rank_id smallint, name text NOT NULL, permissions int NOT NULL, PRIMARY KEY (guild_id, rank_id));
CREATE TABLE guild_member (guild_id uuid REFERENCES guild(id), character_id uuid UNIQUE REFERENCES character(id), rank_id smallint NOT NULL, joined_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY (guild_id, character_id));

-- ============ Journaux (partitionnés par mois) ============
CREATE TABLE currency_ledger (
  id bigserial, character_id uuid NOT NULL, currency text NOT NULL,
  delta bigint NOT NULL, balance_after bigint NOT NULL,
  reason text NOT NULL, ref_id uuid, at timestamptz NOT NULL DEFAULT now()
) PARTITION BY RANGE (at);

CREATE TABLE item_event (
  id bigserial, item_id uuid NOT NULL, kind text NOT NULL,   -- created|picked|equipped|traded|fused|salvaged|admin_edit
  from_owner uuid, to_owner uuid, data jsonb, at timestamptz NOT NULL DEFAULT now()
) PARTITION BY RANGE (at);

CREATE TABLE trade_log (id uuid PRIMARY KEY, a uuid NOT NULL, b uuid NOT NULL, items_a uuid[], items_b uuid[], gold_a bigint, gold_b bigint, fee bigint, at timestamptz NOT NULL DEFAULT now());
CREATE TABLE fusion_log (id uuid PRIMARY KEY, character_id uuid NOT NULL, inputs uuid[] NOT NULL, output uuid NOT NULL, recipe text NOT NULL, seed bigint NOT NULL, pity_before int, pity_after int, client_nonce uuid UNIQUE NOT NULL, at timestamptz NOT NULL DEFAULT now());
CREATE TABLE chat_log (id bigserial, channel text, sender uuid, body text, flagged boolean, at timestamptz NOT NULL DEFAULT now()) PARTITION BY RANGE (at);
CREATE TABLE report (id bigserial PRIMARY KEY, reporter uuid NOT NULL, target uuid NOT NULL, kind text NOT NULL, context jsonb NOT NULL, status text NOT NULL DEFAULT 'open', handled_by uuid, at timestamptz NOT NULL DEFAULT now());
CREATE TABLE admin_audit (id bigserial PRIMARY KEY, actor uuid NOT NULL, action text NOT NULL, target text, payload jsonb NOT NULL, ip inet, at timestamptz NOT NULL DEFAULT now()); -- append-only (REVOKE UPDATE, DELETE)
CREATE TABLE leaderboard_snapshot (board text, period text, taken_at timestamptz, entries jsonb NOT NULL, PRIMARY KEY (board, period, taken_at));
```

Rétention : journaux partitionnés par mois, chat 30 jours, `item_event` 18 mois puis archivage à froid, `admin_audit` conservé sans limite.

## Modèle personnage

### Vue persistante (base)

`character` + `character_evolution` + `character_progress` + `character_stats` + objets équipés/inventaire + runes + emplacements de Soleils et orbites.

### Vue en jeu (mémoire du game server)

```rust
struct PlayerRuntime {
    character_id: Uuid, epoch: u64,
    // persistant, modifié en mémoire, sauvegardé par checkpoint
    level: u8, xp: i64, gold: i64, currencies: Currencies,
    primary: PrimaryStats, active_evolution: EvolutionId,
    inventory: Inventory,            // conteneurs → ItemInstance
    equipment: [Option<ItemId>; 12],
    suns: [Option<SunId>; 5], moons: [Option<MoonId>; 6],
    // dérivé, recalculé au changement de build
    compiled: CompiledLoadout,       // stats finales, compétences compilées, déclencheurs
    // temporaire, jamais persisté
    entity: Entity,                  // Transform, Health, Resources, Cooldowns, Statuses, MoonState…
    net: ClientNetState,             // AOI, historique de snapshots, file d'inputs
    dirty: DirtyFlags,               // quelles parties sauvegarder au prochain checkpoint
}
```

Chargement à l'entrée en jeu (1 requête par table, en parallèle), puis aucune lecture jusqu'à la déconnexion.

## Modèle objet

```rust
struct ItemInstance {
    id: Uuid, version: u64,
    base: ItemBaseId,          // → ItemBaseDef (statique : type, emplacement, implicite, icône, sprite)
    rarity: Rarity,            // 1..=9
    ilvl: u8, quality: u8,
    seed: u64,                 // toutes les valeurs dérivées de la seed + tables versionnées
    affixes: SmallVec<[RolledAffix; 6]>,   // {affix_id, tier, value}
    powers: SmallVec<[PowerId; 2]>,
    sockets: SmallVec<[Socket; 4]>,        // {color, rune: Option<(family, level)>}
    binding: Binding, trades_left: Option<u8>,
    durability: u8, locked: bool,
    origin: ItemOrigin,
}
```

- Représentation réseau : l'infobulle complète est envoyée uniquement au propriétaire (et aux joueurs qui inspectent) ; au sol, seuls `id` réseau, icône, rareté et position.
- Valeurs stockées **et** reproductibles depuis la seed (audit : une valeur non reproductible trahit une manipulation).
- `ItemBaseDef`, `AffixDef`, `PowerDef` : contenu statique versionné ; les objets gardent la valeur tirée pour que l'équilibrage futur n'altère pas silencieusement l'existant (sauf migration explicite).

## 3. Accès et performances

- Pool de connexions par service (sqlx) + PgBouncer en mode transaction.
- **Aucune requête SQL dans la boucle de tick** ; tous les accès passent par des tâches asynchrones hors simulation.
- Écritures regroupées (checkpoints par lots de 100 personnages, `UNNEST`).
- Lecture des classements et profils publics sur réplicas.
- Index partiels sur les objets non détruits ; `VACUUM` agressif sur `item` (fort taux de mise à jour).

## 4. Redis (clés)

| Clé | Type | TTL | Contenu |
|---|---|---|---|
| `sess:{token_id}` | hash | 5 min | Jeton de connexion temps réel |
| `presence:{account}` | hash | 90 s | Statut, zone |
| `char_lock:{character}` | string | 30 s | Instance propriétaire + époque |
| `party:{id}` | hash | durée du groupe | Membres, chef, règles |
| `lfg:{activity}:{region}` | sorted set | 30 min | Annonces |
| `rl:{scope}:{account}` | string | fenêtre | Rate limiting |
| `lb:{board}:{period}` | sorted set | période | Classements |
| `dir:char:{id}` / `dir:inst:{id}` | hash | — | World Directory |
