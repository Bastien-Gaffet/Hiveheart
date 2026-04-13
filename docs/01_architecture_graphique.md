# Architecture Graphique de Mindustry
> Analyse technique pour inspiration de projet OpenGL / Vulkan

---

## 1. Vue d'ensemble

Mindustry est un jeu **2D top-down** basé sur une grille, open-source (licence GPL v3), développé en Java par Anuken. Son moteur graphique repose sur un framework maison appelé **Arc**, lui-même dérivé de **libGDX**, qui abstrait OpenGL ES 2.0 / 3.0 (OpenGL 3.0+ sur desktop, WebGL sur navigateur, Metal via ANGLE sur iOS).

Le code source graphique se situe principalement dans :
```
core/src/mindustry/graphics/
```

---

## 2. Stack technique

| Composant | Technologie |
|---|---|
| Langage | Java (JDK 17) |
| Framework | Arc (fork libGDX) |
| API graphique | OpenGL ES 2.0 / 3.0 (GL30 par défaut) |
| Shaders | GLSL (version minimale ~130, GL30 cible) |
| Audio | SoLoud (remplace le backend libGDX) |
| Desktop backend | SDL (remplace LWJGL+GLFW) |
| iOS | MetalANGLE (OpenGL → Metal) |
| Dépendances natives | GLEW, freetype, Box2D (jnigen) |
| Build | Gradle + outils de packing de sprites |

---

## 3. Pipeline de rendu 2D

### 3.1 Sprite Batching

Le cœur du rendu est le **SpriteBatch** hérité de libGDX/Arc. Son principe :

- Accumule les quads texturés (sprites) dans un **VBO** en mémoire CPU.
- Envoie un seul draw call GPU dès qu'une autre texture doit être bindée, ou que le buffer est plein.
- Réduit drastiquement les changements d'état GPU (`glBindTexture`, `glDrawArrays`).

Chaque vertex de sprite contient : position (x, y), coordonnées UV (u, v), et couleur (RGBA encodé en float).

```
[Vertex Buffer]
  position(2f) | texcoord(2f) | color(4f packed)  →  GPU
```

### 3.2 Texture Atlas

Tous les sprites du jeu sont packés dans un ou plusieurs **texture atlases** (feuilles de sprites). L'outil `tools:pack` (Gradle) effectue ce packing à la compilation :

```
./gradlew tools:pack
```

Cela évite les changements de texture pendant le rendu et maximise les batches.

### 3.3 Framebuffers (FBO)

Mindustry exploite intensivement les **Framebuffer Objects** pour :

- **Post-processing** : bloom, distorsion, effets lumineux sur les tirs et explosions.
- **Masques et transparences groupées** : rendre des groupes de sprites à 100% d'opacité dans un FBO, puis afficher le FBO avec une opacité globale.
- **Minimap** : rendu hors-écran de la carte pour mise à jour asynchrone.
- **Atmosphère planétaire** et boucliers animés (activés par défaut depuis la v156 sur Android).

Flux type d'un FBO :
```
fbo.begin()
  → clear(transparent)
  → batch.draw(sprites...)
fbo.end()
→ batch.draw(fbo.getColorTexture(), ...)  // rendu à l'écran
```

### 3.4 Caméra et projections

- Caméra **orthographique** 2D (pas de perspective).
- La matrice `camera.combined` (view × projection) est transmise au vertex shader via un uniform `u_projTrans`.
- Le système de coordonnées monde est converti en NDC `[-1, +1]` dans le vertex shader.
- La caméra supporte zoom, pan, et suit le joueur.

---

## 4. Shaders GLSL

### 4.1 Shader par défaut (SpriteBatch)

**Vertex shader minimal :**
```glsl
attribute vec4 a_position;
attribute vec4 a_color;
attribute vec2 a_texCoord0;

uniform mat4 u_projTrans;

varying vec4 v_color;
varying vec2 v_texCoords;

void main() {
    v_color = a_color;
    v_texCoords = a_texCoord0;
    gl_Position = u_projTrans * a_position;
}
```

**Fragment shader minimal :**
```glsl
varying vec4 v_color;
varying vec2 v_texCoords;
uniform sampler2D u_texture;

void main() {
    gl_FragColor = v_color * texture2D(u_texture, v_texCoords);
}
```

### 4.2 Shaders spécialisés (Shaders.java)

Mindustry définit de nombreux shaders dans `mindustry/graphics/Shaders.java` :

- **Shader de lumière** : calcul d'éclairage ambiant, lampes dynamiques des bâtiments.
- **Shader de distorsion** : effets de chaleur, explosions.
- **Shader de fog-of-war** : masquage progressif des zones non explorées (Erekir).
- **Shader de bouclier** : rendu hexagonal animé des force projectors.
- **Shader planète** : normales incorrectes corrigées pour OpenGL 2 (`gl30` par défaut depuis ~2022).

La cible est **GL 3.0 (GLSL 130)** minimum sur desktop, compatible ES 2.0 sur mobile.

---

## 5. Couches de rendu (Draw Layers)

Le rendu de la scène suit un **ordre de couches** strict pour assurer la bonne transparence et superposition. Les éléments typiques dans l'ordre de rendu :

```
1. Sol / tuiles de terrain (floors)
2. Blocs (bâtiments, murs)
3. Ombres des unités
4. Unités et projectiles
5. Effets de particules (flammes, fumée, débris)
6. Liquides (eau, lave, pétrole)
7. Lumières et bloom (FBO)
8. Fog of War (Erekir)
9. UI / HUD (caméra séparée)
```

Chaque couche peut changer le shader actif ou commuter de FBO.

---

## 6. Gestion des assets

- **Sprites** : PNG packés en atlas au build, chargés en texture GPU au démarrage.
- **Classes générées** : `Tex`, `Icon`, `Sounds`, `Musics` sont auto-générées à partir des fichiers d'assets dans `mindustry.gen`.
- **Polices** : Bitmap font + FreeType pour les langues à script complexe (CJK, etc.).
- **Packing runtime** : possible sur Android, mais peut causer des ANRs s'il est sur le thread principal (bug connu).

---

## 7. Compatibilité et optimisations

- Mindustry nécessite au minimum **OpenGL 2.1** avec l'extension `framebuffer_object`.
- Par défaut, il force **GL30** (OpenGL 3.0), qui active le mode strict GLSL.
- Sur les GPU Intel Windows, un contexte GL2 est utilisé en fallback pour contourner un bug de corruption mémoire pilote.
- iOS utilise **MetalANGLE** (traduction OpenGL → Metal), permettant >60 FPS.
- Optimisation notable en v156 : **rendu des build plans** (plans de construction).

---

## 8. Ce qui est transposable en OpenGL / Vulkan

| Pattern Mindustry | Équivalent OpenGL/Vulkan natif |
|---|---|
| SpriteBatch (batching) | VAO + VBO instancié, draw indirect |
| Texture Atlas | `GL_TEXTURE_2D_ARRAY` ou atlas manuel |
| Framebuffer Objects | OpenGL FBO / Vulkan Render Pass + Attachment |
| Shaders GLSL | GLSL (OpenGL) / SPIR-V via glslang (Vulkan) |
| Caméra orthographique | Matrice de projection orthographique (glm::ortho) |
| Couches de rendu | Multi-pass rendering / Subpasses Vulkan |
| Fog of War | Stencil buffer ou texture de masque |

---

*Sources : GitHub Anuken/Mindustry, GitHub Anuken/Arc, issues #6858, #7999, releases v153/v156*
