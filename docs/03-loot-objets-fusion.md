# 03 — Loot, objets et fusion

## 1. Raretés

| Rang | Rareté | Couleur | Affixes | Sockets de runes | Effet au sol |
|---|---|---|---|---|---|
| 1 | Commun | Gris | 0 | 0 | Nom gris, aucun effet |
| 2 | Peu commun | Vert | 1 | 0–1 | Légère lueur |
| 3 | Magique | Bleu | 2 | 0–1 | Lueur + colonne courte |
| 4 | Rare | Jaune | 3–4 | 1–2 | Colonne lumineuse, son distinct |
| 5 | Épique | Violet | 4–5 | 1–2 | Colonne + particules lentes |
| 6 | Légendaire | Orange | 4 + 1 pouvoir légendaire | 2–3 | Faisceau haut, onde au sol, son grave |
| 7 | **Mythique** | Rouge-rubis | 5 + 1 pouvoir | 2–3 | Voir §2 |
| 8 | **Céleste** | Cyan-blanc | 5 + 2 pouvoirs | 3 | Voir §2 |
| 9 | **Primordial** | Or solaire animé (dégradé cyclique) | 6 + 2 pouvoirs + 1 affixe « Primordial » | 4 | Voir §2 |

Taux de base (monstre normal, par objet tiré ; modulés par catégorie de monstre, région, bonus de découverte) :

| Rareté | Taux |
|---|---|
| Commun | 62 % |
| Peu commun | 24 % |
| Magique | 9 % |
| Rare | 3,5 % |
| Épique | 1,1 % |
| Légendaire | 0,35 % |
| Mythique | 0,04 % (niveau ≥ 40) |
| Céleste | 0,004 % (niveau ≥ 60) |
| Primordial | **Jamais en drop direct** : uniquement fusion (§4) et quelques boss 85+ à 0,0005 % |

Bonus de découverte (« Fortune ») : plafonné à +150 % et n'affecte que les raretés 4 à 7, pour ne pas écraser la rareté des 8–9.

## 2. Effets visuels des drops (raretés 7, 8, 9)

Le joueur doit comprendre **immédiatement, même hors écran**, qu'un objet majeur est tombé.

| Élément | Mythique (7) | Céleste (8) | Primordial (9) |
|---|---|---|---|
| Animation de chute | Objet projeté en arc, rebond, rotation | Descend du ciel sur un rayon | Le temps ralentit 0,4 s (local), implosion puis éclosion |
| Lumière | Lumière rouge pulsée rayon 5 tuiles | Lumière cyan rayon 8 tuiles, change l'ambiance locale | Lumière dorée rayon 12 tuiles, recolore l'écran brièvement |
| Particules | Braises montantes | Étoiles en orbite + poussière céleste | Anneaux solaires, éruptions, rayons rotatifs |
| Aura | Anneau au sol | Rune géante animée au sol | Soleil miniature au-dessus de l'objet |
| Son | Carillon grave | Chœur court | Thème unique + écho audible dans toute la zone du joueur |
| Écran | — | Léger flash (réglable) | Flash + secousse (réglables), bordure dorée |
| Indication | Faisceau vertical visible à 30 tuiles | Faisceau + marqueur sur la mini-carte | Faisceau + marqueur sur la carte + icône d'indicateur hors écran |
| Social | — | Message dans le canal Région | Message **Système global** (« X a obtenu un objet Primordial ») |

Contraintes : ces FX restent actifs même en mode Performance (version simplifiée, jamais supprimés),
ils ne peuvent pas être masqués par les FX d'autres joueurs (couche dédiée au-dessus des effets).

## 3. Objets

### 3.1 Emplacements

Tête, torse, mains, pieds, ceinture, amulette, anneau ×2, arme (une ou deux mains), main gauche, cape, relique (12).

### 3.2 Structure d'un objet

- **Base** : type (ex. « Épée longue »), niveau requis, implicite fixe (ex. +8 % vitesse d'attaque).
- **Niveau d'objet (ilvl)** : détermine les paliers d'affixes accessibles.
- **Affixes** : préfixes (offensifs) et suffixes (défensifs/utilitaires), tirés dans des pools pondérés par emplacement, paliers T1–T10 selon l'ilvl.
- **Pouvoir légendaire** : effet mécanique (modificateur ou déclencheur, voir [02 §6](02-classe-evolutions-competences.md)).
- **Sockets** : 0–4 emplacements de runes.
- **Qualité** : 0–20 %, multiplie les valeurs des affixes.
- **Graine (seed)** : toutes les valeurs sont dérivées d'une graine serveur, stockée avec l'objet (reproductible, audit).

Le modèle de données complet est dans [14-base-de-donnees.md](14-base-de-donnees.md#modèle-objet).

### 3.3 Génération (serveur uniquement)

```text
OnKill(monster, killers[]):
  pour chaque joueur éligible (contribution ≥ 10 % ou membre de groupe à portée) :
    nb_tirages = table(monster.category) × modificateurs de zone/événement
    pour chaque tirage :
      rareté   = roll(rng_joueur, table_rareté ajustée)
      base     = roll(table_loot(monster, région), filtre niveau)
      ilvl     = monster.level (+ bonus élite/boss)
      affixes  = roll_affixes(base, rareté, ilvl, seed)
      → ItemInstance en mémoire (état « au sol », propriétaire = joueur)
```

- **Loot personnel** : chaque joueur voit et ramasse **son** loot (pas de vol, pas de course). Les objets au sol n'existent que pour leur propriétaire → le serveur n'envoie les drops qu'à lui.
- Les objets au sol vivent 5 min en mémoire (jamais en base) ; ils sont persistés **au ramassage**.
- Objets de rareté ≥ 7 : persistance **immédiate** dans une file prioritaire de sauvegarde (voir serveur) pour qu'aucun crash ne les fasse disparaître.
- Filtrage : les objets en dessous du filtre de rareté du joueur sont démontés automatiquement en poussière (option) et ne sont même pas envoyés au client.

### 3.4 Démontage et échanges

- Démontage → Poussière d'étoile (quantité selon rareté).
- Échange entre joueurs : fenêtre d'échange à double validation, transaction atomique en base (voir sécurité). Les objets de rareté 9 et les Soleils sont **liés au compte** ; les raretés 7–8 sont échangeables une seule fois.

## 4. Fusion

### 4.1 Fonctionnement

À la Forge de Fusion (sanctuaire), le joueur place **5 objets** et paie de l'or + de la poussière.

| Entrée | Résultat possible |
|---|---|
| 5 objets de même rareté R | Objet de rareté R (70 %), R+1 (25–28 %), variante spéciale (2–5 %) |
| 5 objets de même emplacement | Le résultat garde cet emplacement (sinon aléatoire) |
| 5 objets d'une même famille (set, région) | Chance de variante spéciale × 2 |
| Catalyseur optionnel (drop rare) | Oriente le résultat : emplacement, élément, famille d'affixes |

Probabilités de montée de rareté (par défaut, configurables) :

| Entrée (5 ×) | Même rareté | Rareté +1 | Variante spéciale | Rareté 9 |
|---|---|---|---|---|
| Rare (4) | 70 % | 28 % | 2 % | — |
| Épique (5) | 72 % | 25 % | 3 % | — |
| Légendaire (6) | 75 % | 21 % | 4 % | — |
| Mythique (7) | 80 % | 15 % | 5 % | — |
| Céleste (8) | 94,5 % | — | 5 % | **0,5 %** |

- **Variante spéciale** : objet de la même rareté avec un pouvoir « Fusionné » introuvable en drop (collection dédiée).
- Rareté 9 : 5 Célestes = en moyenne 1 000 Célestes consommés par Primordial sans protection → ajout d'une **Ferveur de Forge** : chaque fusion Céleste ratée ajoute +0,05 % (plafonné à +5 %), réinitialisée au succès. Le compteur est visible.
- Entrées de rareté < 4 : fusion en poussière uniquement (évite la fusion de déchets en masse).

### 4.2 Transaction serveur

```text
FuseRequest(item_ids[5], catalyst_id?, client_nonce)
  1. Vérifier propriété, non-verrouillage, non-équipé, non en échange, compatibilité, coûts.
  2. BEGIN ; SELECT ... FOR UPDATE sur les 5 objets ; vérifier leur version.
  3. Tirage serveur (RNG cryptographique, seed enregistrée).
  4. Supprimer (soft delete + raison « fused ») les 5 objets, débiter or/poussière (ledger),
     insérer le résultat, écrire fusion_log(inputs, outputs, seed, pity_before, pity_after).
  5. COMMIT → réponse FuseResult(item complet, animation_script).
  Idempotence : client_nonce unique → un double envoi renvoie le même résultat.
```

Le résultat est **déterminé et persisté avant** que l'animation ne commence. Une déconnexion pendant
l'animation ne change rien ; à la reconnexion, l'objet est dans l'inventaire.

### 4.3 Animation de fusion

Durée totale 4–9 s, passable après la première seconde (option « Fusion rapide »).

```text
1. Les 5 objets s'élèvent en pentagone autour de l'enclume (0,8 s)
2. Ils tournent en accélérant, traînées de leur couleur de rareté (1,2 s)
3. Convergence au centre, implosion lumineuse (0,6 s)
4. Roulement : une roue de raretés défile et ralentit (1–4 s selon le résultat)
      → la roue s'arrête sur la rareté obtenue ; chaque cran « tick » sonore
5. Révélation : l'objet apparaît avec l'effet de sol de sa rareté (§2), infobulle ouverte
```

Le roulement est une **présentation** d'un résultat déjà acquis : il n'y a aucun choix, pari ni
achat associé ; l'interface affiche clairement les probabilités de la recette avant validation et
un historique des fusions. Aucune fusion n'est vendable contre de l'argent réel.

## 5. Interactions

| Système | Interaction |
|---|---|
| Runes | Les sockets survivent à la fusion si le résultat est de même emplacement (runes rendues sinon) |
| Soleils | Certains Soleils modifient la Fortune ou la fusion (ex. +1 % variante spéciale) |
| Collection | Chaque pouvoir légendaire/fusionné découvert est enregistré dans le Codex |
| Classements | « Objets rares » : points par rareté 7–9 obtenus (horodatés par le serveur) |
| Chat système | Annonces des raretés 8 (région) et 9 (global), rate-limitées |

## 6. Performances

- Tables de loot compilées en tables d'alias (tirage O(1)).
- Aucun accès base pour générer un drop ; écriture différée groupée au ramassage.
- Un drop = 1 message réseau (`ItemDropped { id, base_icon, rarity, pos }` ≈ 12 octets), détails envoyés au survol/ramassage seulement.

## 7. Sécurité

- Génération, ramassage, fusion, démontage, échange : **exclusivement serveur**.
- Chaque objet a un UUID unique + un compteur de version ; toute mutation vérifie la version (anti-duplication, voir [15](15-securite-anticheat.md)).
- Ramassage validé par distance serveur (≤ 2 tuiles + tolérance de latence).
- Journal immuable : création (source, seed), transferts, destruction.
