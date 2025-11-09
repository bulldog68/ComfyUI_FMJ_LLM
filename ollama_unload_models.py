# ollama_unload_models.py

import requests

class OllamaUnloadModelsNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "unload_all_models": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "unload_all"
    CATEGORY = "FMJ"
    OUTPUT_NODE = True

    def unload_all(self, unload_all_models):
        if not unload_all_models:
            return ("⚠️ Inactif. Activez 'unload_all_models' pour lancer le déchargement.",)

        base_url = "http://localhost:11434"
        try:
            # Récupérer la liste des modèles
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                return (f"❌ Erreur : impossible de lister les modèles (HTTP {response.status_code})",)

            models = [m["name"] for m in response.json().get("models", [])]
            unloaded = []
            for model in models:
                try:
                    payload = {"model": model, "prompt": "", "keep_alive": 0}
                    requests.post(f"{base_url}/api/generate", json=payload, timeout=5)
                    unloaded.append(model)
                except:
                    pass
            return (f"✅ {len(unloaded)} modèle(s) déchargé(s) : {', '.join(unloaded[:3])}{'...' if len(unloaded) > 3 else ''}",)

        except Exception as e:
            return (f"❌ Exception : {str(e)}",)


NODE_CLASS_MAPPINGS = {
    "OllamaUnloadModelsNode": OllamaUnloadModelsNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OllamaUnloadModelsNode": "🧹 Ollama Unload All Models"
}