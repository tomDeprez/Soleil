# 15 — Sécurité et anti-cheat

## 1. Principe fondateur

Le client est considéré comme **hostile**. Il ne décide jamais : dégâts, XP, niveau, loot, objets,
monnaie, recharges, position finale, résultat d'une fusion ou d'un échange. Il n'envoie que des
intentions, que le serveur valide.

## 2. Authentification et sessions

| Élément | Mesure |
|---|---|
| Mots de passe | argon2id (paramètres calibrés ≈ 50 ms), politique de longueur, vérification contre fuites connues (k-anonymity) |
| Connexion | Rate limit par IP et par compte, verrouillage progressif, CAPTCHA après échecs |
| MFA | TOTP optionnel pour les joueurs, **obligatoire** pour tout compte staff |
| Jetons | Access token court (15 min, JWT EdDSA), refresh token opaque en cookie `HttpOnly; Secure; SameSite=Strict`, rotation à chaque usage, détection de réutilisation → révocation de la famille |
| Jeton temps réel | Jeton dédié à usage unique (5 min), lié au compte, consommé au handshake gateway |
| Sessions | Liste des sessions actives visible par le joueur, révocation possible |
| OAuth (option) | Connexion via fournisseurs tiers, liaison de comptes |

## 3. Permissions

RBAC : `player`, `moderator` (chat, signalements, mutes), `gm` (support : inventaire en lecture, restauration d'objet avec justification), `admin` (configuration, bans, événements), `superadmin` (rôles). Principe du moindre privilège ; toute action staff est journalisée (voir [16](16-monitoring-administration.md#administration)).

## 4. Protection du transport et des API

- TLS partout (HTTPS, WSS, HTTP/3) ; HSTS ; CSP stricte sur le client ; COOP/COEP.
- WebSocket : vérification `Origin`, jeton unique, taille maximale des messages, timeouts d'inactivité, limite de connexions par IP et par compte (1 connexion de jeu par compte).
- Décodage binaire strict : bornes de chaque champ, longueur des listes, rejet de tout message mal formé (et score d'anomalie).
- Rate limiting à plusieurs niveaux : edge (L4/L7, protection DDoS du fournisseur), gateway (par connexion et par type de message), services (par compte).
- API HTTP : validation des schémas, protection CSRF (cookie SameSite + jeton), pas de données sensibles dans les URL.
- Secrets : gestionnaire de secrets (Vault / secrets Kubernetes chiffrés), jamais dans le dépôt ; rotation.
- Dépendances : audit automatisé (`cargo audit`, `npm audit`), images minimales signées.

## 5. Économie et objets : anti-duplication

| Risque | Protection |
|---|---|
| Double session exploitée | Verrou de personnage (bail Redis) + `epoch` vérifié à chaque écriture |
| Requêtes concurrentes (race) | Toutes les mutations d'objets passent par l'instance propriétaire (sérialisation naturelle) ; en base, verrouillage `SELECT … FOR UPDATE` + `version` |
| Rejeu de requête | `client_nonce` unique (fusion, échange, achat) : idempotence |
| Échange | Machine d'états : proposition → verrouillage des deux côtés → confirmation double → transaction unique (objets passent en `trade_escrow` puis au destinataire), annulation automatique si l'un des objets change |
| Crash en milieu d'opération | Transactions atomiques ; les opérations de valeur ne sont confirmées au client qu'après commit |
| Objet fabriqué de toutes pièces | Chaque objet a une origine + seed ; audit périodique de reproductibilité ; `item_event` complet |
| Monnaie | Grand livre (`currency_ledger`) avec solde après opération ; réconciliation quotidienne solde ↔ somme des deltas |

## Anti-cheat

### 6.1 Validation serveur systématique

| Domaine | Validation |
|---|---|
| Déplacement | Vitesse max selon stats/monture/buffs + tolérance ; collisions serveur ; téléportation impossible hors compétence |
| Compétences | Équipée, recharge (horloge serveur), ressource, état, portée, ligne de vue, cadence d'inputs |
| Attaques | Portée recalculée avec les positions serveur (rembobinage ≤ 150 ms uniquement) |
| Ramassage | Propriétaire + distance ≤ 2 tuiles + tolérance |
| Interactions | Distance au PNJ / à la forge / au coffre |
| Inputs | Numéros de séquence croissants, horodatage cohérent, nombre par tick borné |

Un input invalide est **ignoré** (et corrigé par le snapshot suivant), jamais « appliqué partiellement ».

### 6.2 Ce qui ne peut pas être triché, par conception

- Informations cachées non envoyées : loot des autres, monstres hors AOI, tables de loot, positions des élites rares avant leur apparition, conjonctions non découvertes → pas de wallhack/ESP utile.
- Les dégâts et le RNG sont serveur : un client modifié n'obtient rien de plus.

### 6.3 Menaces résiduelles et détection

Les **bots** (farm automatisé) et l'**assistance à l'esquive** restent possibles avec un client légitime.

| Signal | Méthode |
|---|---|
| Temps de jeu continu anormal | > 12 h sans pause significative |
| Régularité inhumaine | Variance des intervalles d'inputs, trajets répétés à l'identique (hash de trajectoire) |
| Réactions surhumaines | Esquives systématiquement < 120 ms après l'apparition d'un télégraphe, sur un grand échantillon |
| Économie | Flux de monnaie/objets vers un même compte depuis de nombreux comptes (réseaux de bots / RMT) |
| Progression | XP/h, drops/h, temps de boss hors distribution (z-score par tranche de niveau) |
| Réseau | Nombreux comptes par IP / empreinte d'appareil |

Chaque signal alimente un **score d'anomalie** par compte (fenêtre glissante). Actions graduées :
observation → défi (CAPTCHA en jeu lors d'une pause, question contextuelle) → restriction (échanges bloqués,
classements masqués) → revue humaine → sanction. Pas de ban automatique sur un seul signal statistique.

Le client est minifié et obfusqué légèrement (coût d'analyse), sans prétendre que cela protège : la sécurité vient du serveur.

## 7. Journalisation et audit

- Logs structurés (JSON) avec `trace_id`, `account_id`, `character_id` ; jamais de mots de passe, jetons ou données personnelles inutiles.
- Événements de sécurité : connexions, échecs, changements de mot de passe/MFA, sessions révoquées, rejets de validation, anomalies, actions staff.
- Audit admin en table append-only + export vers stockage immuable (object storage à rétention verrouillée).

## 8. Données personnelles

RGPD : minimisation (email + pseudo), export et suppression de compte (anonymisation des journaux),
durées de rétention documentées, chiffrement au repos (disques et sauvegardes), accès staff aux
données personnelles limité et journalisé.

## 9. Tests de sécurité

- Fuzzing du décodeur de protocole (`cargo fuzz`) en CI.
- Tests d'intégration « client malveillant » : bots de test envoyant des inputs hors bornes, rejouant des nonces, spammant, tentant des races sur la fusion/l'échange.
- Pentest externe avant bêta ouverte ; programme de bug bounty au lancement.
