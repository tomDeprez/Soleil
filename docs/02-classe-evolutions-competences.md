# 02 — Classe, évolutions, compétences et système de build

## 1. L'Éveillé (classe de base)

Un seul personnage, une seule classe. De 1 à 15, l'Éveillé dispose d'un kit de base :

| Touche | Compétence de base | Rôle |
|---|---|---|
| Clic gauche | Attaque de base (arme équipée) | Génère du Lumen |
| Q | Entaille | Mêlée en arc |
| W | Trait de lumière | Projectile |
| E | Bond | Déplacement offensif |
| R | Garde | Réduction de dégâts courte |
| T | Nova | Zone autour de soi |
| Espace | Esquive | Roulade à i-frames (2 charges) |

Ressource commune : **Lumen** (100 de base, régénération 5/s, gagné par attaques de base).
Chaque évolution ajoute une **ressource secondaire** qui porte sa mécanique propre.

## 2. Évolutions

### 2.1 Déblocage

| Évolution débloquée | Condition |
|---|---|
| 1ʳᵉ | Niveau 15, quête « L'Éveil » : choix libre parmi les 10 |
| 2ᵉ | Niveau 25, quête « Double Aube » |
| 3ᵉ à 10ᵉ | Dès le niveau 30, chaque évolution se débloque en réussissant son **Épreuve** (donjon solo court à mécanique propre, rejouable) |

Ainsi un joueur peut tout essayer **sans créer de second personnage**, et l'Épreuve sert de tutoriel à l'évolution.

### 2.2 Changement d'évolution

- Instantané, gratuit, en sanctuaire (ou à un Autel d'Aube en zone), hors combat.
- Chaque évolution conserve **sa propre allocation** de compétences, sa barre et jusqu'à 3 **loadouts** sauvegardés.
- Partagé entre évolutions : niveau, statistiques primaires, équipement, runes, Soleils, Lunes, montures, collection.
- Points de compétence d'une évolution = points de niveau (partagés, pas de re-farm) + points de **Maîtrise** (propres à l'évolution, gagnés en jouant avec elle).

### 2.3 Points de compétence

| Source | Points |
|---|---|
| Niveau (1 par niveau à partir de 2) | 89 au niveau 90 |
| Maîtrise de l'évolution (paliers d'XP gagnée avec elle, continue après 90) | 15 |
| Quêtes d'évolution et Épreuve | 6 |
| **Total maximal par évolution** | **110** |

Coût pour maximiser une compétence : **19 points** (voir §4). Maximiser les 10 compétences
coûterait 190 points : le joueur peut en maximiser ~5, ou en répartir davantage partiellement.
Le choix est donc réel. Réinitialisation : gratuite jusqu'au niveau 20, puis coût en or modéré
(nœud par nœud, ou total en sanctuaire).

### 2.4 Les 10 évolutions

Chaque évolution change une **mécanique**, pas seulement des chiffres.

| # | Évolution | Orientation | Ressource secondaire | Mécanique signature |
|---|---|---|---|---|
| 1 | **Lame-Solaire** | Dégâts bruts mêlée | Ferveur (0–100, monte en touchant, décroît hors combat) | Combos : enchaîner des compétences différentes en < 1,5 s augmente les dégâts ; à 100 Ferveur, prochain coup = « Zénith » |
| 2 | **Voltigeur** | Mobilité | Élan (monte en se déplaçant) | Les dégâts dépendent de la vitesse ; esquive 4 charges ; attaques en mouvement sans ralentir |
| 3 | **Assassin d'Éclipse** | Critique | Marques (jusqu'à 5 par cible) | Les critiques posent des Marques ; « Exécuter » consomme les Marques pour des dégâts garantis ; invisibilité courte |
| 4 | **Arcaniste Prismatique** | Élémentaire | Prisme (cycle Feu → Givre → Foudre) | Chaque sort change l'élément courant ; enchaîner les trois déclenche une Résonance ; réactions élémentaires (Fusion, Surcharge, Cristallisation) |
| 5 | **Invocateur Stellaire** | Invocations | Constellation (capacité d'invocations) | Les invocations forment des figures géométriques ; la figure (triangle, ligne, cercle) donne un bonus global |
| 6 | **Rempart** | Défense | Garde (absorbe, se charge en bloquant) | Blocage directionnel actif ; blocage parfait (≤ 150 ms) = contre-attaque et Exposé ; provocation pour le groupe |
| 7 | **Tisse-Gravité** | Contrôle | Masse | Crée des puits et des lignes de force qui déplacent monstres et projectiles ; les collisions entre monstres infligent des dégâts |
| 8 | **Pestifère** | Dégâts sur durée | Contagion | Les DoT se propagent à la mort de la cible ; dégâts augmentés par nombre d'afflictions distinctes |
| 9 | **Chantre de l'Aube** | Soutien | Hymnes (jusqu'à 3 actifs) | Auras chantées qui évoluent selon la durée de maintien ; soins qui débordent en boucliers ; solo viable via auras offensives |
| 10 | **Chronomancien** | Mécanique temporelle | Échos | Enregistre les 3 dernières secondes ; « Rembobinage » renvoie à une position passée ; les Échos rejouent des compétences lancées |

### 2.5 Kits (10 compétences principales + 5 uniques par évolution)

| Évolution | Compétences principales (Q W E R T) | Compétences uniques (D F) |
|---|---|---|
| Lame-Solaire | Frappe Solaire, Tourbillon d'Aube, Lame Jaillissante, Brise-Garde, Onde de Choc, Charge Ardente, Fente Céleste, Couperet, Riposte, Cri de Guerre | Zénith Absolu, Avatar du Midi, Mille Lames, Jugement, Soleil de Plomb |
| Voltigeur | Rafale, Ricochet, Pas Fantôme, Vrille, Lame du Vent, Salto Piégé, Tir en Course, Sillage, Coup de Talon, Grappin | Vitesse Absolue, Cyclone, Mur du Son, Pluie de Lames, Sans Entrave |
| Assassin d'Éclipse | Coup Sournois, Dague d'Ombre, Voile, Exécuter, Éventail, Marque de Mort, Piège Noir, Pas d'Ombre, Saignée, Poison Éclipse | Éclipse Totale, Clone Noir, Mort Certaine, Nuit Tombante, Mille Marques |
| Arcaniste Prismatique | Trait Prismatique, Boule de Feu, Lance de Givre, Chaîne d'Éclairs, Météore, Nova Glaciale, Orbe Foudre, Mur Élémentaire, Prisme Réfracté, Transmutation | Tempête Prismatique, Singularité, Convergence, Âge de Glace, Supernova |
| Invocateur Stellaire | Étoile Servante, Sentinelle, Essaim, Golem d'Astéroïde, Lien Stellaire, Sacrifice, Comète Guidée, Portail, Rappel, Constellation d'Ordre | Géant Céleste, Pluie d'Étoiles, Carte du Ciel, Armée Éternelle, Big Bang |
| Rempart | Coup de Bouclier, Parade, Rempart Mobile, Charge Blindée, Provocation, Onde de Garde, Pieux, Bastion, Représailles, Égide | Forteresse, Mur Infranchissable, Dernier Rempart, Écho de Fer, Colosse |
| Tisse-Gravité | Puits, Répulsion, Ligne de Force, Écrasement, Orbite, Chute, Attraction, Lévitation, Masse Critique, Distorsion | Trou Noir, Inversion, Champ Nul, Collision Stellaire, Horizon |
| Pestifère | Crachat Putride, Nuée, Flétrissure, Spores, Miasme, Plaie, Contagion, Marée Noire, Parasite, Pourriture | Pandémie, Corps Hôte, Floraison Mortelle, Fléau Absolu, Mue |
| Chantre de l'Aube | Hymne de Vigueur, Hymne de Fureur, Hymne de Garde, Note Solaire, Chœur, Refrain, Silence, Crescendo, Canon, Harmonie | Opéra de l'Aube, Requiem, Sanctuaire Chanté, Unisson, Dernière Note |
| Chronomancien | Trait Temporel, Rembobinage, Ralenti, Écho, Boucle, Accélération, Paradoxe, Sablier, Fracture, Horloge Parfaite | Arrêt du Temps, Futur Antérieur, Mille Échos, Retour Absolu, Fin des Temps |

Répartition : chaque évolution a au moins 2 déplacements/défensives, 1 générateur, 1 consommateur, 2 zones, 1 cible unique lourde, pour que tout build reste jouable.

## 3. Compétences uniques (D / F)

- 5 par évolution, **2 équipables** simultanément.
- Déblocage : niveaux 20, 35, 50, 65, 80 (avec l'évolution active).
- Temps de recharge longs (45–120 s) ou déclencheurs conditionnels (ex. « Mort Certaine » est utilisable seulement sur une cible à 5 Marques).
- Elles transforment le gameplay pendant leur durée (ex. **Avatar du Midi** : 15 s, toutes les compétences deviennent des versions Zénith ; **Arrêt du Temps** : 4 s, monstres figés, les dégâts s'accumulent puis se libèrent).
- Chacune possède 3 **Facettes** mutuellement exclusives (débloquées par la Maîtrise) qui orientent son usage (dégâts, survie, groupe).

## 4. Arbre d'une compétence (15 améliorations)

Structure fixe pour toutes les compétences : 5 rangs × 3 nœuds.

| Rang | Nœuds | Coût | Règle | Nature |
|---|---|---|---|---|
| I | 3 | 1 pt | Tous prenables | Chiffres : dégâts, coût, portée |
| II | 3 | 1 pt | Tous prenables | Zone, recharge, durée |
| III | 3 | 2 pts | 1 fondamental + **1 variante parmi 2** | Changement de comportement (élément, forme) |
| IV | 3 | 2 pts | Tous prenables | Effets secondaires, synergies avec d'autres compétences |
| V | 3 | 3 pts | **1 Transformation parmi 3** | Change la nature de la compétence |

Déblocage d'un rang : ≥ 2 nœuds pris au rang précédent. Coût complet d'une compétence : 3 + 3 + 4 + 6 + 3 = **19 points**, 12 nœuds actifs sur 15.
Nombre de configurations distinctes par compétence (prise partielle incluse) : plusieurs centaines ;
par évolution, avec le choix des 5 compétences + 2 uniques + 3 Facettes, le nombre de builds dépasse 10¹².

### Exemple complet : Frappe Solaire (Lame-Solaire)

Base : mêlée en arc 120°, 150 % dégâts d'arme, 12 Lumen, pas de recharge, génère 8 Ferveur. Tags : `Mêlée`, `Physique`, `Lumière`, `Générateur`.

| Rang | Nœud | Effet |
|---|---|---|
| I | Lame Aiguisée | +20 % dégâts |
| I | Allonge | +1 tuile de portée |
| I | Économie | −4 Lumen |
| II | Arc Large | Arc 180° |
| II | Élan Ardent | +4 Ferveur générée |
| II | Frappe Rapide | +15 % vitesse d'attaque sur cette compétence |
| III | Rayonnement (fondamental) | Laisse une zone de lumière 2 s (20 % dégâts/s) |
| III | *Variante* Flamme Solaire | Convertit 100 % des dégâts en Feu, applique Brûlure |
| III | *Variante* Lame d'Onde | Projette une onde de 5 tuiles (devient `Projectile`) |
| IV | Brise-Armure | Chaque 3ᵉ frappe : −15 % armure sur la cible 4 s |
| IV | Combo Solaire | Si lancée après Tourbillon d'Aube : +40 % dégâts et +1 charge de Combo |
| IV | Soif de Lumière | 2 % vol de vie contre les cibles dans une zone de lumière |
| V | *Transformation* Frappe du Zénith | Chaque 4ᵉ Frappe devient un Zénith (400 %) sans consommer la Ferveur |
| V | *Transformation* Lame Éclatée | Tire 5 éclats en éventail (`Projectile` ×5, 60 % chacun) |
| V | *Transformation* Marteau de l'Aube | Frappe lente (0,6 s) au sol, zone 3 tuiles, étourdit 1 s, 380 % |

## 5. Barre d'action

```text
[Clic G] attaque de base   [Clic D] compétence au choix (optionnel)
[Q] [W] [E] [R] [T]         5 compétences principales choisies parmi les 10
[D] [F]                     2 compétences uniques choisies parmi les 5
[Espace] esquive            [1-4] consommables
```

Total : 7 compétences actives. Changement de barre : hors combat uniquement (ou 10 s sans subir de dégâts),
pour empêcher le « swap » de compétences en plein combat de boss.

## 6. Système de build : tags, modificateurs, déclencheurs

L'interaction entre compétences, objets, runes, Soleils et Lunes repose sur **trois primitives
data-driven**, les mêmes pour toutes les sources.

### 6.1 Tags

Chaque compétence, effet, projectile et invocation porte des tags :
`Mêlée, Projectile, Zone, Mouvement, Canalisation, Invocation, Aura, DoT, Contrôle, Générateur, Consommateur, Critique,`
`Physique, Feu, Givre, Foudre, Ombre, Lumière, Poison, Soin, Bouclier, Unique`.

### 6.2 Modificateurs

```text
Modifier {
  stat:        Damage | CritChance | CritDamage | AreaSize | Cooldown | Cost | Duration | ProjectileCount | ...
  kind:        Flat | Increased (additif) | More (multiplicatif) | Convert(from, to, %) | Override
  filter:      tags requis / exclus (ex. requiert [Critique, Projectile])
  condition:   None | TargetHpBelow(%) | SelfHpAbove(%) | BuffActive(id) | StackCount(res, n) | Moving | Stationary
  value:       f32
  source:      Item | Rune | Sun | Moon | Passive | SkillUpgrade | Buff
}
```

Pipeline de calcul (ordre fixe, identique partout) :
`base → Flat → conversions → Σ Increased → Π More → plafonds (ex. réduction de recharge ≤ 60 %, crit ≤ 100 %)`.

### 6.3 Déclencheurs

```text
Trigger {
  event:        OnHit | OnCrit | OnKill | OnDodge | OnPerfectBlock | OnCast(tags) | OnDamaged
                | OnLowHp(%) | Periodic(s) | OnStatusApplied(status) | OnSummonDeath | OnResourceFull(res)
  filter:       tags de la source
  chance:       0–1 (tirée par le RNG serveur)
  icd:          temps de recharge interne (obligatoire, ≥ 0,1 s)
  action:       CastSkill(id, scale) | ApplyStatus | GainResource | Heal | Shield | SpawnProjectile | ModifyNextCast
}
```

Garde-fous (performance + équilibrage) :

- **Profondeur de chaîne max = 3** : un déclenchement issu d'un déclenchement issu d'un déclenchement ne déclenche plus rien.
- ICD minimal 100 ms ; budget par personnage de 30 déclenchements par tick, excédent ignoré et comptabilisé en métrique.
- Les effets déclenchés ont le tag `Déclenché` et ne profitent pas des modificateurs « OnCast ».

### 6.4 Exemple de chaîne de build

```text
Frappe Solaire (Lame Éclatée : 5 projectiles)          → tags Projectile, Critique possible
  ↓ Rang IV « Brise-Armure »                             → plus de crit effectif
Rune critique (niveau 6) sur l'arme                      → +18 % chance crit [Projectile]
  ↓
Objet « Gantelets de l'Astre » : +90 % dégâts crit      → Modifier More CritDamage
  ↓
Soleil « Cœur de Supernova » : les crits ont 10 % de chance de faire exploser la cible (ICD 0,5 s)
  ↓
Lune « Lune Rousse » liée à ce Soleil : les explosions appliquent Brûlure et génèrent 5 Ferveur
  ↓
Unique « Zénith Absolu » : se déclenche automatiquement à 100 Ferveur (Facette « Automatique »)
```

## 7. Architecture technique du système

### 7.1 Données

```text
SkillDef    { id, evolution_id, slot_kind: Main|Unique, tags[], cost, cooldown_ms, cast_ms,
              targeting: Self|Direction|Point|Target, range, effects: EffectGraph }
UpgradeDef  { id, skill_id, rank 1..5, index 0..2, exclusive_group?, point_cost, ops: PatchOp[] }
PatchOp     = Add(path, v) | Mul(path, v) | Set(path, v) | AddTag(t) | RemoveTag(t)
              | AppendEffect(EffectNode) | ReplaceEffect(node_id, EffectNode) | AddTrigger(Trigger)
EffectNode  = Damage | Projectile | Area | Dash | Summon | ApplyStatus | Heal | Delay | Repeat | Branch(condition)
```

Définitions en fichiers de données versionnés (`content/skills/*.ron`), validés par un outil CI
(références, coûts, exclusivités, bornes des valeurs), puis compilés en binaire partagé serveur/client.

### 7.2 Compilation du build

Lorsque le build change (allocation, barre, équipement, rune, Soleil, Lune), le serveur **compile**
une `CompiledLoadout` : chaque compétence équipée devient un graphe d'effets aplati avec
modificateurs pré-agrégés par tags. Coût : quelques dizaines de µs, **jamais** dans la boucle de
lancement. Au lancement, le serveur n'exécute que le graphe compilé.

### 7.3 Exécution serveur

1. Réception de l'input `Cast(slot, aim, input_seq)`.
2. Validations : compétence équipée, recharge écoulée (horloge serveur), ressource suffisante, état (pas étourdi), portée, ligne de vue si requise, cadence d'inputs.
3. Débit de ressource, démarrage de la recharge, émission d'un événement `CastStarted` vers les clients dans l'AOI.
4. Résolution au tick d'impact : requêtes spatiales (grille), calcul des dégâts avec le RNG serveur, déclencheurs.
5. Émission d'événements compactés (`Hit` agrégés par tick, voir réseau).

### 7.4 Côté client

Le client connaît les `SkillDef` (pour l'interface et la prédiction visuelle) mais **ne calcule jamais**
les dégâts. Il anticipe l'animation et les FX du lancement local dès l'appui (prédiction cosmétique),
et annule proprement si le serveur rejette (`CastRejected(reason)` → la recharge affichée est corrigée).

### 7.5 Sécurité

- Le client envoie uniquement : slot pressé, direction/point visé, numéro de séquence.
- Allocations de points : requêtes validées (points disponibles, prérequis de rang, exclusivités), transaction en base, puis recompilation.
- Toute divergence (recharge contournée, cadence impossible) incrémente un score d'anomalie (voir anti-cheat).

### 7.6 Difficultés et solutions

| Difficulté | Solution |
|---|---|
| Explosion combinatoire illisible | Tags visibles dans l'interface, infobulles calculées côté serveur (« dégâts réels : 1 240–1 610 »), simulateur de mannequin en sanctuaire |
| Builds dominants | Télémétrie d'usage par nœud et par combinaison, taux de victoire de boss par build, équilibrage par configuration à chaud |
| Boucles infinies de déclencheurs | Profondeur max, ICD, budget par tick |
| Coût CPU des effets | Graphes compilés, pas d'allocation au lancement (pools d'effets), requêtes spatiales sur grille |
| Divergence client/serveur | Définitions générées depuis une source unique, hash de version vérifié à la connexion |
