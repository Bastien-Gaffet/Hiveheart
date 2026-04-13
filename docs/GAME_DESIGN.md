# Game Design Document — Hiveheart

## Concept

**Genre**: God game / ecological strategy / relaxing simulation
**Platform**: PC (priority), Web (future)
**Tagline**: Drag and drop bees to restore dying ecosystems.

The player is not a bee — they are the spirit of the hive, an invisible force that guides life. The world is sick. The player heals it one tile at a time.

---

## Core fantasy

> "With a single gesture, I can bring a dead meadow back to life."

The drag & drop input must feel like touching the world directly. Every action should produce a visible, satisfying reaction.

---

## Core gameplay loop

```
Observe the map
  → Select a bee from the hive
    → Drag it to a zone (flower, polluted tile, water, etc.)
      → Action executes (pollination, purification, etc.)
        → Ecological chain reaction triggers
          → Resources gained (nectar, pollen, hive energy)
            → Unlock new bees / abilities
              → Repeat
```

---

## Bee types

### MVP (build these first)

| Bee | Role | Mechanic |
|-----|------|----------|
| Worker | Pollinates flowers, collects nectar | Raises `fertility` on target tile |
| Scout | Reveals hidden zones, detects pollution sources | Removes fog of war, tags tiles |

### Later

| Bee | Role |
|-----|------|
| Architect | Builds pollen bridges and anti-pesticide barriers |
| Queen | Rare — triggers a growth burst on a full zone (not placed like a unit) |
| Chemist | Purifies polluted water, neutralizes toxins |
| Guardian | Defends against pests, fires, parasites |
| Traveler | Reconnects two distant biomes via a pollination route |

---

## Ecological chain reaction

This is the heart of the game. Actions must cascade.

Example:
1. Worker bee pollinates a flower
2. Flower grows → attracts a butterfly (passive event)
3. Butterfly pollinates a second plant
4. Second plant feeds a bird
5. Bird eats pests
6. Soil rebalances
7. Zone becomes self-sustaining → no bee needed anymore

The goal is to make the player feel like they are building a living system, not just clicking on tiles.

---

## Tile stats (per tile)

```python
tile = {
    "fertility":  float,  # 0.0 – 1.0 — drives flower growth
    "pollution":  float,  # 0.0 – 1.0 — damages fertility and flowers
    "humidity":   float,  # 0.0 – 1.0 — affects drought / water events
    "flowers":    float,  # 0.0 – N   — drives nectar production
    "biome":      str,    # "wasteland" | "meadow" | "forest" | "toxic" | "water"
}
```

---

## Biomes

| Biome | Fertility | Pollution | Description |
|-------|-----------|-----------|-------------|
| wasteland | 0.0–0.3 | 0.5–1.0 | Starting state, grey and dead |
| meadow | 0.5–0.8 | 0.0–0.3 | Restored grassland, flowers present |
| forest | 0.7–1.0 | 0.0–0.2 | Dense vegetation, high nectar output |
| toxic | 0.0–0.2 | 0.7–1.0 | Heavily polluted, spreads to neighbors |
| water | fixed | fixed | Cannot be pollinated, used for humidity |

Biome transitions happen automatically based on tile stats.

---

## Resources

| Resource | How earned | How spent |
|----------|-----------|-----------|
| Nectar | Flowers on fertile tiles | Spawn new bees |
| Pollen | Worker bees pollinating | Evolve bee abilities |
| Hive energy | Passive over time | Special actions (Queen burst, storm shield) |

**MVP**: implement nectar only.

---

## Threats

| Threat | Effect | Counter |
|--------|--------|---------|
| Pesticides | Kills flowers, blocks flight routes | Chemist bee, isolation corridors |
| Drought | Drops humidity, wilts flowers | Scout water sources, route moisture |
| Monoculture | Limits biodiversity, freezes flower count | Introduce variety with Traveler |
| Fire | Spreads across tiles, destroys fertility | Guardian bee |
| Urbanisation | Creates impassable zones | Reconnect via Traveler |
| Invasive species | Crowds out native plants | Guardian + Architect |
| Hive disease | Kills bees over time | Quarantine + Queen burst |
| Light pollution | Disrupts night bee activity | Architect barriers |

---

## World structure (locked decision)

Le monde est **infini**, généré procéduralement à la demande via un système de chunks (16×16 tiles). Seuls les chunks visibles sont en mémoire. Les chunks non-modifiés sont régénérés depuis la seed. Les chunks modifiés par le joueur sont sauvegardés (cloud).

La génération utilise trois couches de bruit Simplex superposées :
- **Couche 1** (grande échelle) → fertilité de base (vallées fertiles, crêtes arides)
- **Couche 2** (échelle moyenne) → pollution (taches industrielles, rivières toxiques)
- **Couche 3** (petite échelle) → humidité (zones humides, sources)

Les biomes émergent de la combinaison de ces trois valeurs — pas d'assignment arbitraire.

---

## Mission structure

Le monde est continu, mais le joueur progresse via des **missions localisées** : zones à restaurer avec un objectif précis et un état initial scriptés.

### Missions prévues (proto → release)

1. Jardin abandonné *(tutoriel — rythme lent, menaces absentes)*
2. Terres agricoles en monoculture
3. Forêt dégradée
4. Périphérie urbaine grise
5. Marais pollué
6. Montagne sous pression

Win condition par mission : atteindre un `biodiversity_score` cible avant effondrement du biome.

### Mode sandbox (post-proto)
Monde libre, pas d'objectif, nature se régénère en temps réel. Le joueur explore et construit.

---

## Sample mission objectives

- Revive 30 flower species
- Attract 5 bird species
- Clean a river
- Survive a pesticide wave
- Reconnect two separated biomes
- Bring the Queen back to a sterile zone
- Reach self-sustaining status on 3 zones simultaneously

---

## Entités passives (post-proto)

Des entités non-joueurs apparaissent automatiquement quand l'écosystème atteint certains seuils. Elles ne sont pas contrôlables — ce sont des récompenses visuelles et des bonus passifs qui donnent vie au monde.

| Entité | Seuil d'apparition | Effet passif |
|--------|-------------------|--------------|
| Papillon | `flowers > 2.0` sur une tile | Pollinise une tile adjacente au hasard |
| Oiseau | Zone avec `biome = "meadow"` ×3 adjacentes | Élimine passivement les parasites |
| Grenouille | `humidity > 0.7` + tile water à proximité | Boost humidité voisins |
| Abeille sauvage | `fertility > 0.8` + `pollution < 0.1` | Boost nectar ×1.2 sur la tile |

---

## Cycles saisonniers (post-proto)

Un cycle de 4 saisons affecte les règles écologiques globalement. Durée configurable (ex: 5 min de jeu = 1 saison).

| Saison | Effet |
|--------|-------|
| Printemps | `FLOWER_GROWTH_RATE ×2`, burst de fertilité |
| Été | Risque de sécheresse si `humidity < 0.3` |
| Automne | Fertilité –0.1 progressive sur forêts |
| Hiver | Fleurs dormantes, pas de papillons, nectar ÷2 |

Les saisons donnent du rythme sans menace agressive et motivent le joueur à agir avant l'hiver.

---

## Progression axes

### 1. Hive growth
Unlock new bee slots as nectar accumulates.

### 2. Bee evolution
Per bee type, choose specialisations:
- Faster movement
- Pollution resistance
- Wider pollination radius
- Night activity
- Cold resistance

### 3. World regeneration
More restored zones = new species appear = new biome types unlock = more stable weather.

---

## Drag & drop feel (critical)

- Pick a bee from the hive panel
- Drag across the map
- Drop on a tile or entity (flower, water, tree, polluted zone)
- Bee pathfinds to target and executes action
- Optional: draw patrol routes by dragging across multiple tiles

The player must feel: *"I am guiding life with my hands."*

---

## Tone & emotional hook

The game is relaxing but has stakes. The world is quietly dying. Every chain reaction the player creates is a small miracle.

Optional minimal narration: the planet narrates its own recovery across seasons.

Core message:
> Every flower matters. Every bee has a role. A small gesture can remake a world.

---

## What makes this game unique

Compared to other god games:
- Tactile drag & drop at the core
- Visible transformation of the world (grey → vivid)
- Ecological theme with real chain reactions
- Calm but strategically deep
- Satisfaction comes from *building systems*, not conquering opponents
