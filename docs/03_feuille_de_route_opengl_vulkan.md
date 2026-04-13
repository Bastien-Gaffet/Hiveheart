# Feuille de Route — Projet Jeu OpenGL / Vulkan
> Inspiré de l'architecture de Mindustry

---

## 1. Choix de l'API graphique : OpenGL vs Vulkan

| Critère | OpenGL | Vulkan |
|---|---|---|
| Courbe d'apprentissage | Modérée | Très élevée |
| Contrôle GPU | Partiel (driver gère beaucoup) | Total (explicit) |
| Multi-threading | Limité (contexte mono-thread) | Natif (command buffers parallèles) |
| Portabilité | Très bonne (desktop + mobile) | Bonne (desktop + Android) |
| Overhead CPU | Moyen | Très faible si bien utilisé |
| Adapté prototype | ✅ Oui | ⚠️ Long à bootstrapper |
| Recommandé pour ce projet | **Phase 1 : OpenGL** | **Phase 2 : Vulkan optionnel** |

**Recommandation** : commencer en OpenGL 3.3+ core profile. Si les performances deviennent un enjeu ou si le projet cible une plateforme mobile avancée, envisager Vulkan via une abstraction (SDL_GPU, WebGPU, ou bgfx).

---

## 2. Structure du projet suggérée

```
project/
├── src/
│   ├── core/
│   │   ├── Game.cpp / Game.h          ← boucle principale
│   │   ├── World.cpp / World.h        ← grille, tuiles, entités
│   │   └── Camera.cpp / Camera.h     ← caméra orthographique
│   ├── graphics/
│   │   ├── Renderer.cpp / Renderer.h  ← pipeline de rendu
│   │   ├── SpriteBatch.cpp            ← batching de quads
│   │   ├── Shader.cpp / Shader.h     ← compilation GLSL
│   │   ├── Texture.cpp / Texture.h   ← gestion textures / atlas
│   │   └── Framebuffer.cpp           ← FBO post-processing
│   ├── gameplay/
│   │   ├── Sector.cpp / Sector.h     ← secteur de carte
│   │   ├── TileMap.cpp               ← grille de tuiles
│   │   ├── Entity.cpp / Entity.h     ← entités (unités, bâtiments)
│   │   └── ResourceSystem.cpp        ← flux de ressources
│   └── ui/
│       └── HUD.cpp / HUD.h           ← interface joueur
├── assets/
│   ├── shaders/                       ← fichiers .vert / .frag
│   ├── textures/                      ← atlas PNG
│   └── maps/                          ← données de niveaux
└── CMakeLists.txt
```

---

## 3. Implémentation du SpriteBatch (OpenGL)

Inspiration directe de l'architecture Arc/libGDX.

### 3.1 Structure d'un vertex

```cpp
struct Vertex {
    float x, y;       // position monde
    float u, v;       // coordonnées UV dans l'atlas
    float r, g, b, a; // couleur RGBA [0..1]
};
```

### 3.2 Setup OpenGL

```cpp
// 1. Créer VAO + VBO dynamique
glGenVertexArrays(1, &vao);
glGenBuffers(1, &vbo);

glBindVertexArray(vao);
glBindBuffer(GL_ARRAY_BUFFER, vbo);
glBufferData(GL_ARRAY_BUFFER, MAX_SPRITES * 4 * sizeof(Vertex),
             nullptr, GL_DYNAMIC_DRAW);

// position
glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)0);
glEnableVertexAttribArray(0);
// UV
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)(2*sizeof(float)));
glEnableVertexAttribArray(1);
// couleur
glVertexAttribPointer(2, 4, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)(4*sizeof(float)));
glEnableVertexAttribArray(2);

// 2. IBO (indices triangles, réutilisable pour tous les quads)
// Chaque quad = 2 triangles = 6 indices
// Ordre : 0,1,2 / 2,3,0
```

### 3.3 Flush du batch

```cpp
void SpriteBatch::flush() {
    if (spriteCount == 0) return;

    glBindTexture(GL_TEXTURE_2D, currentTexture);
    glBindBuffer(GL_ARRAY_BUFFER, vbo);
    glBufferSubData(GL_ARRAY_BUFFER, 0,
                    spriteCount * 4 * sizeof(Vertex), vertices.data());

    glBindVertexArray(vao);
    glDrawElements(GL_TRIANGLES, spriteCount * 6, GL_UNSIGNED_INT, 0);

    spriteCount = 0;
    drawCalls++;
}
```

---

## 4. Shader de base (GLSL 330 core)

### vertex.glsl
```glsl
#version 330 core

layout(location = 0) in vec2 a_position;
layout(location = 1) in vec2 a_texCoord;
layout(location = 2) in vec4 a_color;

uniform mat4 u_projTrans;

out vec2 v_texCoord;
out vec4 v_color;

void main() {
    v_texCoord = a_texCoord;
    v_color = a_color;
    gl_Position = u_projTrans * vec4(a_position, 0.0, 1.0);
}
```

### fragment.glsl
```glsl
#version 330 core

in vec2 v_texCoord;
in vec4 v_color;

uniform sampler2D u_texture;

out vec4 fragColor;

void main() {
    fragColor = v_color * texture(u_texture, v_texCoord);
}
```

---

## 5. Caméra orthographique

```cpp
// Matrice de projection orthographique (GLM)
// left, right, bottom, top, near, far
glm::mat4 projection = glm::ortho(
    -viewWidth / 2.0f,  +viewWidth / 2.0f,
    -viewHeight / 2.0f, +viewHeight / 2.0f,
    -1.0f, 1.0f
);

// Matrice de vue (translation + zoom)
glm::mat4 view = glm::scale(
    glm::translate(glm::mat4(1.0f), glm::vec3(-camX, -camY, 0.0f)),
    glm::vec3(zoom, zoom, 1.0f)
);

glm::mat4 combined = projection * view;
shader.setUniform("u_projTrans", combined);
```

---

## 6. Framebuffer pour post-processing

```cpp
// Création
GLuint fbo, colorTex;
glGenFramebuffers(1, &fbo);
glBindFramebuffer(GL_FRAMEBUFFER, fbo);
glGenTextures(1, &colorTex);
glBindTexture(GL_TEXTURE_2D, colorTex);
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
             GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,
                       GL_TEXTURE_2D, colorTex, 0);
glBindFramebuffer(GL_FRAMEBUFFER, 0);

// Usage
glBindFramebuffer(GL_FRAMEBUFFER, fbo);
  // → rendu de la scène ici
glBindFramebuffer(GL_FRAMEBUFFER, 0);
// → affichage de colorTex avec un shader de post-process
```

---

## 7. Texture Atlas

Créer un atlas manuellement ou avec un outil (TexturePacker, crunch, etc.) :

```
atlas.png          ← tous les sprites en une image
atlas.json         ← UV de chaque sprite { "name": "tile_grass", "x":0, "y":0, "w":16, "h":16 }
```

En code :
```cpp
struct TextureRegion {
    float u0, v0, u1, v1; // coordonnées normalisées [0..1]
};

// Calcul à partir de l'atlas
TextureRegion getTile(int px, int py, int pw, int ph,
                      int atlasW, int atlasH) {
    return {
        (float)px / atlasW,
        (float)py / atlasH,
        (float)(px + pw) / atlasW,
        (float)(py + ph) / atlasH
    };
}
```

---

## 8. Boucle de rendu — Ordre des couches (inspiré Mindustry)

```
Frame N :
  1. clear(screen)
  2. shader_default.bind()
  3. batch.begin()
     → draw tiles (sol, terrain)
     → draw blocks (bâtiments)
  4. batch.end() + flush()

  5. fbo_light.begin()
     shader_light.bind()
     → draw lights / bloom
  5. fbo_light.end()
     → composite sur screen

  6. batch.begin()
     → draw units + shadows
     → draw projectiles + FX
     → draw particles
  6. batch.end() + flush()

  7. [optionnel] shader_fog.bind()
     → draw fog of war texture

  8. HUD rendering (caméra séparée, projection écran)
```

---

## 9. Recommandations clés

1. **Commencer simple** : un seul shader, un seul atlas, SpriteBatch basique → puis itérer.
2. **Mesurer les draw calls** : chaque flush = 1 draw call. Viser < 20 par frame pour un jeu 2D.
3. **Utiliser SDL3 ou GLFW** pour la fenêtre et le contexte OpenGL — SDL3 est modulable vers SDL_GPU (Vulkan/Metal) sans changer le reste du code.
4. **GLM** pour les maths (matrices, vecteurs) — interface proche de GLSL.
5. **Profiler tôt** avec RenderDoc ou Mesa's apitrace pour détecter les goulots.
6. **Ne pas prématurément optimiser** le batching : un SpriteBatch naïf suffit jusqu'à ~50 000 sprites/frame.

---

## 10. Ressources utiles

| Ressource | URL |
|---|---|
| LearnOpenGL (référence complète) | https://learnopengl.com |
| Mindustry source (graphics) | https://github.com/Anuken/Mindustry/tree/master/core/src/mindustry/graphics |
| Arc framework (libGDX fork) | https://github.com/Anuken/Arc |
| libGDX SpriteBatch doc | https://libgdx.com/wiki/graphics/2d/spritebatch-textureregions-and-sprites |
| Vulkan Tutorial | https://vulkan-tutorial.com |
| RenderDoc (debugger GPU) | https://renderdoc.org |
| GLM (maths) | https://github.com/g-truc/glm |
| SDL3 | https://wiki.libsdl.org/SDL3 |

---

*Document généré pour projet jeu personnel — inspiré de l'analyse du code source de Mindustry (Anuken)*
