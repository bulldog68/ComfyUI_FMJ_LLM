# ComfyUI_FMJ_LLM
Advanced nodes for interaction with Olama (text, vision, image editing), with dynamic management of prompts via CSV.
## 📦 Package : **ComfyUI_FMJ_LLM**
> **Auteur** : FMJ  
> **Description** : Nœuds avancés pour l’interaction avec **Ollama** (texte, vision, édition d’image), avec gestion dynamique des prompts via CSV.
> 
<img width="1579" height="1276" alt="Capture d’écran du 2025-11-09 16-41-45" src="https://github.com/user-attachments/assets/a3b8671c-5b1c-4632-a954-a606fdbe7b33" />

---

## 🔤 1. `🦙 Ollama Text Generator` — Génération de prompts textuels avancés

### 📌 Description
Génère des **prompts optimisés** ou du **texte créatif** en utilisant des **modèles de langage (LLM)** via Ollama.  
Idéal pour :
- Créer des prompts détaillés pour la génération d’images,
- Transformer un concept simple en description riche,
- Appliquer un style spécifique (photo, surréalisme, personnage, etc.).

### 🛠️ Fonctionnalités
- ✅ **Prompts délocalisés** : les instructions système sont chargées depuis des fichiers **CSV** dans le dossier `csv/`.
- ✅ **Ajout dynamique** : ajoutez un nouveau fichier `.csv` dans `csv/`, cliquez sur 🔄 **Refresh** dans ComfyUI, et le nouveau style apparaît dans la liste.
- ✅ **Supporte tous les modèles Ollama** : `qwen3`, `llama3`, `mistral`, etc.
- ✅ **Mode spécial `qwen_edit`** : pour affiner des prompts destinés à **Qwen Image Edit**.

### 📂 Structure attendue
```
csv/
├── photo.csv
├── surrealism.csv
├── character.csv
└── ... (un fichier par style)
```
> **Format CSV** : colonnes `prompt_style` (nom du style) et `system_prompt` (instruction système complète).

### ⚙️ Paramètres
| Paramètre | Type | Description |
|----------|------|------------|
| `prompt` | `STRING` | Le sujet ou le concept de base. |
| `prompt_style` | `LIST` | Le style à appliquer (chargé depuis `csv/`). |
| `model_name` | `STRING` | Nom du modèle Ollama (ex: `qwen3`). |
| `max_tokens`, `temperature`, `seed` | Contrôle de la génération |
| `unload_after_use` | Décharge le modèle après usage |

### 📤 Sorties
- `response` : le texte généré (prompt optimisé ou réponse).
- `debug_info` : infos de débogage (modèle, temps, etc.).

---

## 🖼️ 2. `👁️ Ollama Vision` — Analyse d’images multimodale

### 📌 Description
Analyse une **image fournie** en utilisant des **modèles multimodaux** (LLaVA, Moondream, Qwen-VL, etc.).  
Permet d’extraire :
- Une description détaillée,
- Une analyse de composition, de style, d’éclairage,
- Une liste d’objets ou de personnages.

### 🛠️ Fonctionnalités
- ✅ **Prompts délocalisés** : depuis le dossier `csvv/`.
- ✅ **Support universel** :
  - `moondream`, `llava` → utilise `/api/chat`,
  - `qwen*` (y compris `qwen3-vl:2b`) → utilise `/api/generate` + injection du token `<img></img>`.
- ✅ **Compatible avec les modèles Qwen-VL custom** (comme `qwen3-vl:2b`).

### 📂 Structure attendue
```
csvv/
├── detailed.csv
├── objects.csv
├── art_style.csv
└── ... (un fichier par type d'analyse)
```
> **Format CSV** : colonnes `description_type` et `system_prompt`.

### ⚙️ Paramètres
| Paramètre | Type | Description |
|----------|------|------------|
| `image` | `IMAGE` | L’image à analyser (obligatoire). |
| `description_type` | `LIST` | Type d’analyse (chargé depuis `csvv/`). |
| `model_name` | `STRING` | Modèle multimodal (ex: `qwen3-vl:2b`, `moondream`). |
| ... | Mêmes paramètres de génération que `OllamaPromptNode` |

### 📤 Sorties
- `description` : le texte d’analyse généré.
- `debug_info` : infos de débogage.

## 📝 Exemple de fichier CSV (`csv/photo.csv`)

```csv
prompt_style,system_prompt
photo,"You're an expert in generative AI prompts to create photos. Your objective is to transform a simple concept into a detailed and optimal prompt..."
```

---

Ce package vous donne une **flexibilité maximale** pour personnaliser vos workflows IA, tout en gardant une **maintenance simple** grâce au format CSV.
