# Gameplay du Mode Campagne — Mindustry
> Analyse pour inspiration de conception de jeu

---

## 1. Concept global

Mindustry est un jeu de type **tower defense / gestion de ressources / RTS**, vue de dessus sur grille 2D. Le mode campagne est le cœur du jeu solo. L'objectif est de **conquérir une ou plusieurs planètes** en capturant des secteurs, en construisant des chaînes de production industrielle, et en défendant son noyau central (le **Core**) contre des vagues d'ennemis.

> *"Les éléments de base sont : extraction de ressources, transport et organisation, fabrication de matériaux, construction de défenses, production d'unités de combat, et recherche de technologies."*

---

## 2. Structure de la campagne

### 2.1 Les deux planètes

| Planète | Difficulté | Orientation | Contenu |
|---|---|---|---|
| **Serpulo** | Intermédiaire | Gestion / automation | 16 matériaux, 131 blocs, 35 unités, 272 secteurs |
| **Erekir** | Difficile | RTS / combat | 10 matériaux, 98 blocs, 15 unités, 17 secteurs jouables |

Le joueur peut basculer librement entre les deux planètes à tout moment.

### 2.2 Les secteurs

Chaque planète est divisée en **secteurs** :
- Des secteurs **procéduraux** (générés à partir d'une seed).
- Des secteurs **hand-crafted** (conçus à la main par les développeurs / la communauté) pour les points clés de progression.
- Serpulo : 29 secteurs de progression + ~243 secteurs procéduraux.
- Erekir : 17 secteurs de campagne, sans secteurs procéduraux accessibles normalement.

Un secteur peut être en mode **Survie** (résister aux vagues ennemies) ou **Attaque** (détruire une base ennemie).

---

## 3. Mécaniques de progression

### 3.1 L'arbre technologique (Tech Tree)

Exclusif à la campagne, le **Tech Tree** permet de débloquer de nouveaux blocs en dépensant des ressources accumulées dans les différents secteurs. Chaque secteur conquis ouvre de nouvelles technologies.

```
Secteur conquis → Ressources collectées → Nœud débloqué dans le Tech Tree
                                         → Nouveaux blocs disponibles pour construire
```

### 3.2 Les factions

- **Sharded** : le joueur (couleur or `#fad057`).
- **Crux** : faction ennemie de Serpulo.
- **Malis** : faction ennemie d'Erekir (couleur violette).
- **Derelict** : structures abandonnées (ruines utilisables).

### 3.3 Flux de ressources inter-secteurs

Un système de **Launch Pads** / **Landing Pads** permet de transférer des ressources entre secteurs. Cela crée une logistique planétaire :

```
Secteur A (production de cuivre)
    → Launch Pad → export vers Secteur B
Secteur B (production d'acier)
    → reçoit le cuivre via Landing Pad
```

Les exports sont exprimés en **unités par minute**. Si un secteur destinataire est perdu, les Launch Pads se synchronisent vers "The Sun" pour maintenir le rythme.

---

## 4. Gameplay d'un secteur — Boucle de jeu

### 4.1 Phase initiale : atterrissage

Le joueur débarque dans son **Core** (structure centrale). Ce Core est :
- La base de spawn des unités joueur.
- Le stockage central des ressources.
- La condition de défaite s'il est détruit.

Sur Serpulo : **Core: Shard** → unité de départ : vaisseau de construction.
Sur Erekir : **Core: Bastion** → unité de départ : Evoke.

### 4.2 Boucle principale

```
1. EXTRACTION      → Miner les ressources (foreuses, extracteurs, plasma bores)
2. TRANSPORT       → Convoyeurs, Ducts (Erekir), tuyaux pour les liquides
3. PRODUCTION      → Fonderies, fabriques, usines chimiques
4. ÉNERGIE         → Générateurs (solaire, vapeur, nucléaire, condenseurs Erekir)
5. DÉFENSE         → Tours de tir alimentées en munitions
6. UNITÉS          → Usines d'assemblage → armées automatisées
7. ATTAQUE         → Commandement des unités vers les bases ennemies
```

### 4.3 Les vagues ennemies

En mode survie, des vagues d'ennemis arrivent à intervalles réguliers par des **spawn points**. La difficulté s'intensifie au fil des vagues. Des paramètres de difficulté permettent de modifier :
- Les stats ennemies (5 niveaux).
- Le **Fog of War** (brouillard de guerre, activé par défaut sur Erekir).
- L'affichage ou non des spawns ennemis sur la minimap.
- L'IA de vague imprévisible (cibles aléatoires).

---

## 5. Spécificités d'Erekir

Erekir introduit des mécaniques distinctes par rapport à Serpulo :

### 5.1 Ressources différentes
- Ressources de base : **Béryllium** et **Graphite**.
- Liquides exclusifs : **Ozone**, **Hydrogène**, **Arkycite**, **Laitier (Slag)**.
- **Chaleur (Heat)** : ressource non-item, généré par certains blocs, accélère des usines si fournie en excès.

### 5.2 Transport plus rapide
- Les **Ducts** (conduits) : 15 items/seconde vs 11 pour les convoyeurs titanium de Serpulo.
- Les extracteurs produisent plus, mais les bâtiments coûtent aussi plus cher.

### 5.3 Fog of War
- Zones hors du Core obscurcies au départ (peut être désactivé).
- Encourage l'exploration active et le contrôle de territoire.

### 5.4 Focus RTS
- Tous les secteurs sont des maps d'**attaque** (objectif : détruire la base ennemie).
- Les unités Core ne peuvent pas être ciblées par l'ennemi sur Erekir.
- Elles peuvent transporter des blocs (payload) mais perdent leur furtivité en le faisant.
- Elles peuvent réparer des blocs mais pas attaquer.

---

## 6. Gestion de la carte mondiale

### 6.1 Invasions et territoire

Sur Serpulo, les secteurs conquis peuvent être **ré-attaqués** par l'ennemi. Un système de calcul en arrière-plan simule ces attaques pendant que le joueur est dans un autre secteur. Ce système est actuellement désactivé par défaut (v154+) et en cours de rework.

### 6.2 Abandon d'un secteur

- Abandonner un secteur **en cours** : explosion du Core, remise à zéro des vagues.
- Abandonner un secteur **à distance** : remise à zéro complète, toutes les structures détruites.
- Si un secteur est perdu lors d'une invasion : les structures du joueur deviennent des **ruines (derelict)**, récupérables lors d'un retour.

---

## 7. Paramètres de difficulté

| Paramètre | Description |
|---|---|
| Stats ennemies | 5 niveaux d'intensité |
| Fog of War | Brouillard de guerre (toggle) |
| Show Enemy Spawns | Points de spawn visibles sur minimap |
| Unpredictable Wave AI | Cibles aléatoires pour les unités ennemies |

---

## 8. Mécaniques inspirantes pour un projet jeu

| Concept Mindustry | Intérêt pour un nouveau projet |
|---|---|
| Boucle extraction → production → défense | Gameplay économique profond et engageant |
| Tech Tree lié aux secteurs | Progression narrative + récompense exploration |
| Logistique inter-secteurs | Couche stratégique méta-jeu |
| Fog of War sur Erekir | Tension et gestion de l'information |
| Modes survie ET attaque | Variété de gameplay sans changer les systèmes core |
| Dérelict ruins (ruines de parties précédentes) | Monde vivant, mémoire du joueur dans l'environnement |
| Unités RTS commandables | Transition douce tower defense → RTS |
| Heat comme ressource abstraite | Systèmes de ressources non-conventionnelles intéressants |

---

*Sources : mindustry-unofficial.fandom.com, mindustry.miraheze.org, Wikipedia, Apple App Store changelog, Steam News*
