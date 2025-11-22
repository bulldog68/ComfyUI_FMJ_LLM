import requests

class FMJUnloadAllLLM:
    """🧹 FMJ Unload All LLM — Décharge tous les modèles Ollama (localhost:11434)."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "trigger": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "unload_all"
    CATEGORY = "🌀FMJ"

    def unload_all(self, trigger):
        OLLAMA_URL = "http://localhost:11434"  # URL fixe
        
        if not trigger:
            return ("⚠️ Déchargement non déclenché (trigger = False).",)
        
        try:
            # Étape 1 : Récupérer les modèles actuellement chargés
            response = requests.get(f"{OLLAMA_URL}/api/ps", timeout=10)
            response.raise_for_status()
            models_info = response.json()

            loaded_models = models_info.get("models", [])
            if not loaded_models:
                return ("✅ Aucun modèle chargé à décharger.",)

            # Étape 2 : Décharger chaque modèle actif
            unloaded_models = []
            for model_info in loaded_models:
                model_name = model_info["name"]
                try:
                    # On fait une requête "vide" avec keep_alive: 0 pour forcer le déchargement
                    requests.post(
                        f"{OLLAMA_URL}/api/generate",
                        json={"model": model_name, "keep_alive": 0},
                        timeout=5
                    )
                    unloaded_models.append(model_name)
                except Exception as e:
                    print(f"[Erreur] Impossible de décharger {model_name}: {e}")

            if unloaded_models:
                return (f"✅ Modèles déchargés : {', '.join(unloaded_models)}",)
            else:
                return ("⚠️ Aucun modèle n’a pu être déchargé.",)

        except requests.exceptions.RequestException as e:
            return (f"❌ Erreur de communication avec Ollama : {str(e)}",)
        except Exception as e:
            return (f"❌ Erreur inattendue : {str(e)}",)