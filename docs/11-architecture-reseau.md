# 11 — Architecture réseau et stratégie d'optimisation réseau

Objectif : **minimiser drastiquement** la bande passante et la charge serveur, tout en donnant une
sensation de réactivité immédiate.

## 1. Modèle

- **Server authoritative** : le serveur simule, le client affiche.
- Le client envoie des **intentions** (inputs), jamais des résultats.
- Le serveur envoie des **snapshots** (états continus : positions, PV) et des **événements** (faits discrets : compétence lancée, coup, drop, mort).

| Paramètre | Valeur | Justification |
|---|---|---|
| Tick de simulation | **30 Hz** (33,3 ms) | Réactivité d'un hack'n slash, coût CPU maîtrisé |
| Envoi des inputs client | 30 Hz, alignés sur le tick, 3 derniers inputs répétés | Redondance contre la perte (WebTransport) |
| Snapshots | 15 Hz (proche), 7,5 Hz (moyen), 3,75 Hz (lointain) | Voir §4 |
| Événements | Chaque tick où il y en a, regroupés dans le même paquet | Latence minimale sur les faits importants |
| Délai d'interpolation | 100 ms (≈ 1,5 intervalle de snapshot proche) | Fluidité même avec gigue |

## 2. Transport

| Phase | Transport | Canaux |
|---|---|---|
| MVP | **WebSocket** (WSS) binaire | Un flux ordonné ; messages petits pour limiter le head-of-line blocking |
| Scaling | **WebTransport** (HTTP/3, QUIC) | Datagrammes non fiables : snapshots, inputs ; flux fiable : événements, inventaire, chat |
| Repli | WebSocket si WebTransport indisponible (Safari, réseaux d'entreprise) | Même protocole, même encodage |

Le protocole est conçu **tolérant à la perte dès le départ** (deltas relatifs au dernier snapshot
acquitté, inputs redondants), donc le passage aux datagrammes ne demande aucune refonte.

Compression : **pas de `permessage-deflate`** (coût CPU serveur élevé, gain faible sur des données
déjà compactes, vulnérabilités de type CRIME). La compression vient de l'encodage lui-même.

## 3. Protocole binaire

### 3.1 Principes

- Schéma unique (`shared/protocol/schema`) → code généré Rust et TypeScript.
- **Bit-packing** : chaque champ a une largeur en bits ; les booléens coûtent 1 bit.
- **Quantification** : pas de `f32` sur le réseau.
- **Varints** pour les identifiants et compteurs.
- **Identifiants réseau courts** : chaque client a une table locale `net_id (u16) ↔ entity`, attribuée à l'entrée dans son AOI (et non l'ID global 64 bits).
- Lecture/écriture dans des buffers préalloués (zéro allocation par message des deux côtés).

### 3.2 Quantification

| Donnée | Encodage | Taille |
|---|---|---|
| Position | Coordonnées locales à la zone, pas de 1/8 de pixel → 2 × 17 bits (zone ≤ 8 192 px) | 34 bits |
| Position (delta) | Différence avec la référence, 2 × 9 bits signés si petite, sinon absolue | 18 bits typique |
| Orientation | 64 directions | 6 bits |
| Vitesse | Déduite côté client (interpolation), non envoyée | 0 |
| PV des autres entités | Pourcentage sur 7 bits (0–100) | 7 bits |
| PV du joueur local | Valeur exacte (varint) | 2–4 octets |
| Animation/état | Index d'état sur 5 bits + phase sur 3 bits | 8 bits |
| Buffs visibles | Bitmask des 16 statuts visuels principaux | 16 bits (si changé) |

### 3.3 Messages principaux

Client → serveur :

| Message | Contenu | Taille |
|---|---|---|
| `Input` | tick, seq, direction de mouvement (6 bits + 1 bit actif), visée (2 × 12 bits relatifs), boutons (8 bits), redondance 2 précédents | ≈ 10–16 o |
| `Cast` | seq, slot (3 bits), cible (point ou net_id) | 4–6 o |
| `Ack` | dernier snapshot reçu (inclus dans `Input`) | 0 (intégré) |
| Requêtes fiables | ramasser, équiper, fusionner, chat, groupe… | variable |

Serveur → client :

| Message | Contenu |
|---|---|
| `Snapshot` | tick, baseline acquittée, état complet du joueur local, liste d'entités modifiées (delta), entités entrées/sorties de l'AOI |
| `Events` | `CastStarted`, `Telegraph`, `HitBatch` (coups agrégés par tick et par cible), `Death`, `ItemDropped`, `Loot`, `LevelUp`, `ProjectileSpawn`, `ProjectileEnd` |
| `Reliable` | Inventaire, stats, chat, groupe, erreurs |

### 3.4 Exemple de budget d'un snapshot proche

Scène de combat typique : 8 joueurs et 40 monstres dans l'AOI, 25 entités modifiées à ce snapshot.

```text
En-tête (tick, baseline, compteurs)                   6 o
Joueur local (position, PV, ressource, recharges Δ)  12 o
25 entités × (net_id 10 b + masque 4 b + pos Δ 18 b + état 8 b ≈ 40 b)  ≈ 125 o
Entrées/sorties d'AOI (2 × ~12 o)                     24 o
Total                                               ≈ 167 o  × 15 Hz ≈ 2,5 Ko/s
+ événements (casts, coups, drops)                  ≈ 1–4 Ko/s en combat intense
```

**Budget cible par client : 3–6 Ko/s en moyenne, 15 Ko/s en pic, plafond dur 32 Ko/s.**
En sortie serveur : 10 000 joueurs × 5 Ko/s ≈ 50 Mo/s ≈ 400 Mbit/s répartis sur toutes les machines.

## 4. Interest management (Area of Interest)

### 4.1 Grille spatiale

Chaque zone est découpée en **cellules de 16 × 16 tuiles (512 × 512 px)**.
Une zone de 256 × 256 tuiles = 16 × 16 = 256 cellules.

```text
Structure (par instance de zone) :
  cells: [Cell; W×H]                 // tableau plat, pas de HashMap
  Cell { entities: SmallVec<[EntityId; 16]>, players: SmallVec<[EntityId; 4]> }
  Mise à jour : quand une entité change de cellule (rare), retrait/ajout O(1) amorti.
```

La grille est préférée au quadtree : entités de taille similaire, densité variable mais bornée,
mise à jour O(1), requêtes de voisinage triviales, excellente localité mémoire. Un quadtree
n'apporte rien ici et coûte en rééquilibrage.

### 4.2 Anneaux d'intérêt

L'écran du joueur couvre ≈ 1 920 × 1 080 px à l'échelle ×2 → ≈ 960 × 540 px monde ≈ 2 × 1 cellules.

| Anneau | Distance (cellules de Chebyshev) | Fréquence | Contenu envoyé |
|---|---|---|---|
| Proche | 0–1 (3 × 3 cellules, ≈ écran + marge) | 15 Hz | Tout : position, état, PV, buffs, projectiles, événements de combat |
| Moyen | 2 (anneau 5 × 5) | 7,5 Hz | Position, état ; pas de projectiles ni de nombres de dégâts |
| Lointain | 3 (anneau 7 × 7) | 3,75 Hz | Joueurs et boss seulement, position grossière |
| Hors AOI | > 3 | — | Rien (sauf groupe et événements globaux) |

Hystérésis : une entité entre dans un anneau à `d ≤ n` et en sort à `d > n + 0,5 cellule` pour éviter le clignotement en bordure.
Montures : l'AOI est étendue de 1 cellule dans la direction du mouvement.

### 4.3 Toujours envoyés, quelle que soit la distance

- Membres du groupe : position grossière à 1 Hz (mini-carte), PV à 2 Hz.
- Boss de la zone : état de phase et PV (barre de boss) à 2 Hz si le joueur est engagé.
- Événements de zone, annonces système, chat.

### 4.4 Filtrage supplémentaire

- **Loot personnel** : les objets au sol ne sont envoyés qu'à leur propriétaire.
- **Projectiles** : jamais en flux continu. Un `ProjectileSpawn { origine, direction, vitesse, type, seed }` suffit ; le client simule la trajectoire déterministe ; le serveur envoie `ProjectileEnd` à l'impact. Projectiles des autres joueurs hors anneau proche : non envoyés.
- **Nombres de dégâts** : agrégés par (cible, tick) dans `HitBatch`, et seulement pour le joueur concerné (source ou cible) + son groupe dans l'anneau proche. Les autres joueurs voient seulement l'effet visuel d'impact.
- **Surcharge** : si plus de 60 entités dans l'anneau proche, un **accumulateur de priorité** (priorité = importance × temps depuis dernier envoi / distance) sélectionne les entités envoyées sous le budget d'octets du client ; les autres attendent le snapshot suivant.

### 4.5 Coût serveur

Pour chaque client, la liste d'intérêt est recalculée **seulement quand le joueur change de cellule**
ou toutes les 500 ms. Les snapshots sont construits à partir d'un **journal de changements par
cellule** (dirty flags par composant) : on ne sérialise que ce qui a changé, et une même donnée de
cellule est encodée une fois puis réutilisée pour tous les clients qui la voient au même tick
(cache d'encodage par cellule et par tick).

## 5. Deltas et snapshots

- Chaque client acquitte le dernier snapshot reçu (dans ses inputs).
- Le serveur garde un historique circulaire de 32 snapshots par client (état « vu » par client, compact : uniquement les champs réseau quantifiés).
- Un snapshot est encodé en **delta par rapport au dernier snapshot acquitté** ; si aucun ack depuis 32 snapshots (≈ 2 s), envoi d'un snapshot complet de l'AOI.
- Champs par entité : masque de bits des champs modifiés, puis uniquement ces champs.

## 6. Client : prédiction, réconciliation, interpolation

### 6.1 Joueur local

- **Prédiction du déplacement** : le client applique immédiatement ses inputs avec **le même code de mouvement et de collision que le serveur**, compilé en WebAssembly depuis la crate Rust `sim-movement` (aucune divergence d'implémentation).
- **Réconciliation** : à chaque snapshot, le client compare la position serveur au tick acquitté avec sa prédiction de ce tick ; en cas d'écart, il repart de l'état serveur et rejoue les inputs non acquittés. Correction visuelle lissée sur 100 ms (sauf écart > 2 tuiles : téléportation).
- **Esquive** : prédite (mouvement), mais l'invulnérabilité est décidée par le serveur au tick où elle a réellement commencé.
- **Compétences** : animation et FX de lancement prédits ; dégâts, projectiles « réels » et effets confirmés par le serveur. En cas de rejet, annulation visuelle.

### 6.2 Autres entités

- **Interpolation** entre les deux snapshots encadrant `temps_serveur_estimé − 100 ms`.
- Extrapolation limitée à 150 ms en cas de trou, puis gel.
- Horloge : synchronisation par échanges ping (moyenne glissante filtrée), estimation du tick serveur courant.

### 6.3 Compensation de latence

- **Attaques du joueur** : le serveur évalue les coups de mêlée et les compétences ciblées contre les positions de monstres « vues » par le client, reconstituées par rembobinage de l'historique de positions, **limité à 150 ms** (au-delà, la latence est à la charge du joueur).
- **Attaques des monstres et boss** : pas de rembobinage ; les télégraphes sont envoyés au début de l'annonce avec l'instant de résolution en tick serveur, et le client affiche un compte à rebours corrigé de sa latence → le joueur a l'information pour esquiver à temps. La résolution utilise la position serveur, ce qui est juste pour tous.

## 7. Connexion, handoff et reconnexion

1. Le client obtient un **jeton de session court** (5 min, signé EdDSA) via l'API HTTPS.
2. Connexion au gateway avec le jeton ; handshake : version du protocole (hash du schéma), version du contenu.
3. Le gateway demande au World Directory l'instance du personnage et ouvre un lien interne vers le game server.
4. **Changement de zone** : le game server source transfère l'état du personnage au game server cible (message interne), le gateway re-route ; le client ne se reconnecte pas.
5. **Reconnexion** : dans les 60 s, le personnage reste en jeu (invulnérable et immobile après 5 s sans input en zone sûre ; en combat, il reste vulnérable pour empêcher la déconnexion d'évasion) ; le client reprend avec un snapshot complet.

## 8. Protection réseau

- TLS obligatoire (WSS / HTTP/3).
- Taille maximale de message (entrant : 512 o pour les inputs, 4 Ko pour les requêtes), validation stricte du décodage (tout champ hors bornes = message rejeté + score d'anomalie).
- Rate limiting par connexion au gateway (token bucket : 40 inputs/s, 10 requêtes fiables/s, rafales bornées).
- Vérification de l'origine (`Origin`) et d'un jeton à usage unique au handshake.
- Voir [15](15-securite-anticheat.md).

## 9. Métriques réseau suivies

Octets et paquets envoyés/reçus par seconde (par client, par instance, par type de message),
taille moyenne des messages, part des snapshots complets vs deltas, entités sautées par l'accumulateur
de priorité, RTT, gigue, pertes (WebTransport), temps d'encodage par tick.
