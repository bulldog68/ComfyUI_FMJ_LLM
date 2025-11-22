## 📦 Package : **ComfyUI_FMJ_LLM**
> **Auteur** : FMJ  
> **Description** : Nœuds avancés pour l’interaction avec **Ollama** (texte, vision, édition d’image), avec gestion dynamique des prompts via CSV.
<img width="1163" height="1209" alt="Capture d’écran du 2025-11-10 13-50-10" src="https://github.com/user-attachments/assets/91e2b3b6-f1b8-42bb-829c-d06b63daa545" />
# 🧠 **ComfyUI FMJ LLM** — Intégration Ollama native dans ComfyUI

> **Générez, améliorez, analysez et décrivez vos prompts avec l’IA locale — directement dans ComfyUI.**

Ce pack de nœuds personnalisés permet d’**intégrer Ollama** (modèles comme `llama3`, `qwen3`, `moondream`, `llava`, etc.) **directement dans vos workflows ComfyUI**, sans dépendance externe ni service cloud. Tout reste **100 % local**.

---

## 🌟 Fonctionnalités principales

### 🔹 1. **Génération de prompts textuels avancés** (`🦙FMJ Ollama Prompt Generator`)
- Choisissez parmi **5 styles de sortie** :  
  - `photo` → prompt réaliste pour photographie  
  - `surrealism` → description onirique et artistique  
  - `character` → description détaillée de personnage  
  - `qwen_edit` → reformulation précise pour **Qwen Image Edit** (respect des règles strictes)  
  - `enhancer` → optimisation automatique pour Stable Diffusion  
- Contrôle fin : `temperature`, `max_tokens`, `seed`
- Compatible avec **tous les modèles texte** (ex: `qwen3`, `llama3`, `mistral`)

---

### 🔹 2. **Analyse d’image par IA vision** (`👁️ FMJ Llm Ollama Vision`)
- Branchez n’importe quelle image (`IMAGE`) → obtenez une description générée par un **modèle vision-langage** (`moondream`, `qwen3-vl:2b`, `llava`, etc.)
- Choisissez **ce que vous voulez extraire** :  
  - `simple` → description courte  
  - `detailed` → description riche  
  - `composition` → analyse de cadrage  
  - `objects` → liste d’objets  
  - `characters` → description de personnages  
  - `art_style` → style artistique (photo, peinture, anime…)  
  - `lighting` → analyse de l’éclairage  
- Parfait pour **rétroaction visuelle**, **reconstruction d’image**, ou **enrichissement de prompt**

---

### 🔹 3. **Gestion centralisée d’Ollama** (`⚙️ FMJ Llm Config`)
- Sélectionnez **l’URL d’Ollama** (par défaut : `http://localhost:11434`)
- Liste **dynamique des modèles installés** → choisissez celui à utiliser
- Branchez la sortie vers les autres nœuds → configuration **unifiée et modulaire**

---

### 🔹 4. **Nettoyage mémoire à la demande** (`🧹 FMJ Unload All LLM`)
- **Décharge tous les modèles** d’Ollama de la mémoire → libère la RAM/VRAM
- Idéal **avant un long workflow** ou pour **changer de modèle lourd**
- Aucun risque de rechargement automatique

---

## 📦 Compatibilité

- ✅ **Ollama ≥ v0.13** (testé sur Linux, Windows)

---

> 💡 **Tout tourne en local.** Vos images, vos prompts, vos données restent **sur votre machine**.
> 💡 **Installer Ollama avant le node. https://ollama.com/
