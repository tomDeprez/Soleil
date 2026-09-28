# 06 — Montures

## 1. Fonctionnement

- Déblocage au **niveau 20** (quête « Le Premier Galop », monture commune offerte).
- Usage : **déplacement**. Monter : 1 s d'incantation (interrompue par les dégâts), touche Z par défaut.
- Démonte automatiquement en subissant des dégâts, en attaquant ou en lançant une compétence. Aucune compétence de combat utilisable monté.
- Recharge de 3 s après un démontage forcé par dégâts (empêche l'aller-retour en combat).
- Interdites en donjon et en arène de boss (sauf montures « d'arène » cosmétiques inexistantes : règle stricte).

Ainsi, les montures accélèrent l'exploration et le farm entre les packs sans jamais toucher l'équilibre des combats.

## 2. Raretés et vitesse

| Rareté | Vitesse | Capacités | Source typique |
|---|---|---|---|
| Commune | +40 % | — | Quête, marchand |
| Peu commune | +45 % | — | Marchand, drop |
| Rare | +50 % | 1 capacité mineure | Drop d'élites, succès |
| Épique | +55 % | 1 capacité | Boss de région, événements |
| Légendaire | +60 % | 2 capacités | Boss 60+, classements saisonniers |
| Mythique | +60 % | 2 capacités + apparence animée | Succès extrêmes, collection complète d'une région |

Vitesse plafonnée à +60 % (au-delà, la bande passante et le streaming d'assets deviennent problématiques et le monde « rétrécit »).

## 3. Capacités (hors combat)

| Capacité | Effet |
|---|---|
| Sprint | +20 % vitesse 5 s, recharge 30 s |
| Saut | Franchit des obstacles bas (collisions spéciales « sautables ») |
| Nage | Traverse l'eau profonde |
| Planeur | Descend des falaises des Terres Brisées |
| Aimant | Ramasse l'or et les consommables dans un rayon de 6 tuiles |
| Pistage | Indique l'élite rare la plus proche (recharge 5 min) |
| Sabots légers | Pas d'aggro des monstres normaux de niveau inférieur de 5+ |

Certaines zones exigent une capacité (raccourcis, secrets) : les montures participent à l'exploration, pas au DPS.

## 4. Progression et personnalisation

- **Niveau de monture (1–20)** : gagné par distance parcourue ; débloque des emplacements de personnalisation, pas de vitesse supplémentaire au-delà de la rareté.
- **Personnalisation** : selle, harnais, teinture (3 canaux de palette), traînée de pas, effet d'invocation. Assemblage paper-doll de sprites superposés.
- **Collection** : Codex des montures (≈ 60 au lancement), classement collection, bonus de compte à 10/25/50 montures (+1 % vitesse de montée, titres).
- Animations : invocation, idle, marche, galop, saut, démontage.

## 5. Données

```text
MountDef     { id, rarity, base_speed_pct, abilities[], sprite_set, customization_slots[] }
MountOwned   { account_id, mount_def_id, level, distance_m, customization jsonb, obtained_at }
CharacterMount { character_id, equipped_mount_def_id? }
```

Montures liées au compte : toutes les évolutions et personnages saisonniers y ont accès.

## 6. Réseau et performance

- Le game server simule la monture comme un simple état du personnage (`Mounted { def_id }`) : vitesse modifiée, ensemble de collisions « sautables ».
- Diffusion : 1 champ dans l'état du joueur (def_id sur 2 octets, envoyé une fois à l'entrée dans l'AOI puis sur changement).
- Validation de vitesse serveur identique (anti speed-hack), avec la vitesse de la monture comme borne.
- Streaming : le spritesheet d'une monture est chargé à l'apparition dans l'AOI, avec un sprite générique de repli pendant le chargement.
- Vitesse élevée → l'AOI est étendue de 20 % dans la direction du mouvement pour éviter l'apparition tardive des entités, et le client précharge les zones voisines plus tôt.
