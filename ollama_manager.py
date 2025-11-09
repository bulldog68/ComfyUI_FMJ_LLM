# ollama_manager.py

import requests

def get_ollama_models(base_url="http://localhost:11434"):
    try:
        response = requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model["name"] for model in data.get("models", []) if "name" in model]
    except Exception as e:
        print(f"⚠️ OllamaManager: impossible de charger les modèles : {e}")
    return ["llama3", "qwen3", "moondream", "llava", "phi3"]

class OllamaManagerNode:
    @classmethod
    def INPUT_TYPES(cls):
        models = get_ollama_models()
        if not models:
            models = ["llama3"]
        return {
            "required": {
                "ollama_url": ("STRING", {"default": "http://localhost:11434"}),
                "selected_model": (models, {"default": models[0]}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("model_name", "ollama_url")
    FUNCTION = "output_config"
    CATEGORY = "FMJ"
    OUTPUT_NODE = False

    def output_config(self, ollama_url, selected_model):
        return (selected_model, ollama_url)


NODE_CLASS_MAPPINGS = {
    "OllamaManagerNode": OllamaManagerNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OllamaManagerNode": "⚙️ Ollama Config"
}