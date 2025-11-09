# __init__.py

from .ollama_manager import OllamaManagerNode
from .ollama_unload_models import OllamaUnloadModelsNode
from .ollama_prompt import OllamaPromptNode
from .ollama_vision import OllamaVisionNode

NODE_CLASS_MAPPINGS = {
    "OllamaManagerNode": OllamaManagerNode,
    "OllamaUnloadModelsNode": OllamaUnloadModelsNode,
    "OllamaPromptNode": OllamaPromptNode,
    "OllamaVisionNode": OllamaVisionNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OllamaManagerNode": "⚙️ Ollama Config",
    "OllamaUnloadModelsNode": "🧹 Ollama Unload All Models",
    "OllamaPromptNode": "🦙 Ollama Text Generator",
    "OllamaVisionNode": "👁️ Ollama Vision"
}