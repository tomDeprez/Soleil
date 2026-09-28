# 13 — Architecture client et stratégie d'optimisation client

## 1. Responsabilités

Le client gère : rendu, animations, effets visuels, interpolation, prédiction (mouvement local),
interface, audio, entrées. **Aucune décision de jeu** : pas de calcul de dégâts, de loot, d'XP, de recharge faisant foi.

## 2. Pile

| Élément | Choix |
|---|---|
| Langage | TypeScript strict |
| Build | Vite (ES modules, code splitting par écran/région) |
| Rendu | PixiJS v8 (WebGL2, WebGPU si disponible) |
| Interface | DOM superposé au canvas avec **SolidJS** (réactivité fine, pas de DOM virtuel, faible coût de mise à jour) |
| Mouvement/collision partagés | Crate Rust `sim-movement` compilée en **WebAssembly** |
| Audio | Web Audio API (graph de mixage, bus par catégorie) |
| Stockage local | Cache API (assets), IndexedDB (paramètres hors ligne, cache de contenu) |

## 3. Organisation en threads

```text
Thread principal
 ├── Boucle requestAnimationFrame : input → prédiction (WASM) → interpolation → ECS client → rendu Pixi
 └── Interface SolidJS (mise à jour à 10–30 Hz max pour les données non critiques)

Worker Réseau
 ├── Socket (WebSocket / WebTransport), décodage binaire, table net_id
 └── Poste les snapshots décodés dans un SharedArrayBuffer (anneau) ou via messages transférables

Worker Assets
 └── Téléchargement, décodage d'images (createImageBitmap), décompression, mise en cache

Worker Audio (AudioWorklet si nécessaire pour les effets)
```

Le décodage réseau hors thread principal évite qu'un gros snapshot provoque une frame longue.
`SharedArrayBuffer` exige l'isolation cross-origin (en-têtes COOP/COEP) : prévu dans la configuration du serveur web/CDN.

## 4. ECS client

- Stockage en tableaux typés (Structure of Arrays : `Float32Array` pour positions, `Uint8Array` pour états…), capacité préallouée (8 192 entités).
- Systèmes : `NetApply` → `Interpolation` → `Animation` → `FxEmit` → `Culling` → `RenderSync` → `UiSync`.
- Les objets Pixi (sprites) sont **poolés** et associés aux entités visibles uniquement.

## 5. Rendu

### 5.1 Couches

```text
1. Sol (tilemap chunkée, rendue en textures de chunk 512×512 mises en cache)
2. Décors bas, ombres portées (sprites simples)
3. Télégraphes (au-dessus du sol, jamais coupés par le LOD)
4. Entités triées en Y (joueurs, monstres, objets au sol, décors hauts)
5. Projectiles et FX (additif)
6. Lumière (texture basse résolution ¼, multipliée) + FX de loot rare (couche dédiée)
7. Post-process (bloom, LUT, distorsion) selon qualité
8. Éléments monde de l'interface (barres, noms, nombres flottants) en bitmap fonts
9. Interface DOM
```

### 5.2 Techniques

- **Atlas de textures** par région et par famille (2 048² max, 4 096² si supporté) générés au build (pipeline Aseprite → TexturePacker-like maison), pour que chaque couche soit rendue en quelques draw calls.
- **Batching** automatique Pixi : même atlas + même blend mode ⇒ un draw call. Objectif : < 100 draw calls par frame.
- **Tilemap** : sol pré-rendu en textures de chunk, re-rendu uniquement si modifié.
- **Instancing** pour les particules (un buffer d'instances par système, mise à jour GPU ou CPU en tableau typé).
- **Frustum culling** : seules les entités dans le rectangle de caméra + marge sont synchronisées vers Pixi (requête sur une grille client).
- **Occlusion** : les décors hauts deviennent translucides quand le joueur passe derrière (pas de calcul d'occlusion coûteux, simple test de rectangle).
- **Pixel-perfect** : rendu à la résolution interne, mise à l'échelle entière, `nearest` filtering ; option résolution de rendu réduite.
- Polices bitmap pour tout texte dans le monde (pas de `Text` Pixi dynamique par nombre de dégâts).

### 5.3 Particules

- Système maison sur tableaux typés : émetteurs data-driven (JSON compilé), pools fixes.
- Budget par niveau de qualité (voir [01 §13](01-game-design.md#13-fx)).
- Priorité : joueur local > télégraphes > boss > groupe > autres joueurs > ambiance. Quand le budget est atteint, les émetteurs de basse priorité réduisent leur taux ou s'arrêtent.
- WebGPU disponible : simulation en compute shader pour le mode Ultra.

## Optimisation

### 6.1 Objectifs

| Mesure | Cible |
|---|---|
| FPS | 60 stables (p99 frame < 20 ms) sur GPU intégré récent (Intel Iris Xe) en qualité Medium |
| Temps CPU par frame | < 8 ms (thread principal) |
| Draw calls | < 100 |
| GC | Aucune pause > 2 ms en combat ; allocations en combat ≈ 0 |
| Mémoire JS | < 300 Mo ; VRAM < 512 Mo en Medium |
| Chargement initial | < 5 Mo avant l'écran de connexion, < 20 Mo avant d'entrer en jeu |

### 6.2 Mesures

| Technique | Application |
|---|---|
| Object pooling | Sprites, particules, nombres flottants, événements réseau, vecteurs temporaires |
| Batching / atlas | §5.2 |
| Instancing | Particules, projectiles nombreux |
| Spatial partitioning | Grille client pour culling et sélection à la souris |
| Culling | Frustum, culling réseau (le serveur n'envoie pas l'invisible), culling d'animation (entités hors écran : pas d'avancement d'animation) |
| LOD | FX LOD, animations réduites pour les autres joueurs lointains, nombre de FX d'autres joueurs limité |
| Web Workers | Réseau, décodage d'assets |
| ECS | §4 |
| Zéro allocation | Pas de closures ni de tableaux créés dans la boucle ; structures réutilisées ; `for` indexés plutôt que `map/filter` dans les systèmes chauds |
| Structures adaptées | Tableaux typés, anneaux circulaires, bitsets |
| Chargement asynchrone | Assets streamés, `createImageBitmap` hors thread |
| Interface | Mises à jour DOM groupées et limitées en fréquence, virtualisation des listes (inventaire, classements, chat) |

### 6.3 Qualité adaptative

Moniteur de frame : si la moyenne glissante dépasse 14 ms pendant 2 s, le client descend
automatiquement le **budget FX** d'un cran (sans changer le préréglage affiché) ; il remonte après
10 s sous 10 ms. Désactivable dans les paramètres.

### 6.4 Outils

- Overlay de debug (F3) : FPS, temps par système, draw calls, entités, particules, mémoire, ping, octets/s.
- Télémétrie anonyme échantillonnée (FPS p50/p99, GPU, navigateur) envoyée au serveur de métriques (opt-out).

## 7. Streaming d'assets

### 7.1 Manifeste

```text
manifest.json (versionné, haché)
  regions/{id}: { tilesets[], atlases[], audio[], music[], size, neighbors[] }
  common: { ui, player_base, fx_common, fonts }
  monsters/{family}: { atlas, audio }
  mounts/{id}, cosmetics/{id}: chargés à la demande
```

Fichiers nommés par hash de contenu (cache HTTP immuable 1 an, CDN).

### 7.2 Priorités

| Priorité | Contenu | Moment |
|---|---|---|
| P0 | Interface, personnage local, FX communs, zone courante (sol + monstres présents) | Avant d'entrer en jeu |
| P1 | Monstres de la zone non encore vus, audio de la zone | Juste après l'entrée |
| P2 | Zones voisines | En arrière-plan, bande passante limitée, quand le joueur approche d'une transition |
| P3 | Montures/cosmétiques d'autres joueurs | À l'apparition dans l'AOI, avec sprite générique de repli |
| — | Zones lointaines | Jamais préchargées |

Déchargement : les atlas de régions non visitées depuis 5 min et non voisines sont libérés (VRAM).
Service Worker : mise en cache persistante des assets déjà téléchargés entre les sessions.

### 7.3 Données de contenu

Les définitions de contenu (compétences, objets de base, monstres) sont chargées par région également ;
les données sensibles (tables de loot, taux, conjonctions non découvertes) ne sont **jamais** envoyées au client.

## 8. Entrées

- Couche d'abstraction « actions » : `MoveToCursor, Skill1..7, Dodge, Interact, OpenInventory…`.
- Liaisons : clavier, souris, manette (Gamepad API, visée au stick droit, mouvement au stick gauche), 2 liaisons par action.
- Détection de conflit à la saisie, restauration par défaut, profils sauvegardés côté serveur.
- Mouvement : clic maintenu (déplacement vers le curseur), ou manette ; les compétences visent le curseur.

## 9. Audio

- Bus : Master → Musique, Effets, Voix, Ambiance, Interface.
- Sprites audio (plusieurs sons par fichier), décodés à la demande, pool de 32 voix, priorité et atténuation.
- Musique en stems synchronisés (exploration/combat/boss).
