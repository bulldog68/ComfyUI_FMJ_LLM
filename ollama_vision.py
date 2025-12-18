# ollama_vision.py
import torch
from PIL import Image as PILImage
import numpy as np
from io import BytesIO
import base64
import csv
from pathlib import Path
from ollama import Client

def tensor_to_base64(image_tensor):
    """Convertit un tenseur ComfyUI en base64."""
    image = image_tensor.squeeze(0)
    i = 255. * image.cpu().numpy()
    img = PILImage.fromarray(np.clip(i, 0, 255).astype(np.uint8))
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_bytes = base64.b64encode(buffered.getvalue())
    return str(img_bytes, 'utf-8')

CSVV_DIR = Path(__file__).parent / "csvv"

def load_vision_prompts():
    """Charge les prompts depuis csvv/*.csv"""
    prompts = {}
    if not CSVV_DIR.exists():
        return prompts
    for csv_file in CSVV_DIR.glob("*.csv"):
        try:
            with open(csv_file, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                if 'description_type' in reader.fieldnames and 'system_prompt' in reader.fieldnames:
                    for row in reader:
                        dtype = row['description_type'].strip()
                        prompt = row['system_prompt'].strip()
                        if dtype and prompt:
                            prompts[dtype] = prompt
        except Exception as e:
            print(f"❌ Erreur lecture {csv_file}: {e}")
    return prompts

class FMJLlmOllamaVision:
    """👁️ FMJ Llm Ollama Vision — Analyse d'images via modèles multimodaux (Qwen3-VL, Llava, etc.)."""
    
    @classmethod
    def INPUT_TYPES(cls):
        prompts = load_vision_prompts()
        desc_types = list(prompts.keys()) or ["_aucun_prompt_dans_csvv_"]
        return {
            "required": {
                "image": ("IMAGE",),
                "description_type": (desc_types, {"default": desc_types[0]}),
                "model_name": ("STRING", {"default": "qwen3-vl:2b"}),
                "ollama_url": ("STRING", {"default": "http://localhost:11434"}),
                "max_tokens": ("INT", {
                    "default": 512,
                    "min": 1,
                    "max": 16384,
                    "tooltip": "Nombre max de tokens pour la description."
                }),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 10.0, "step": 0.1}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "keep_alive": ("INT", {
                    "default": 5,
                    "min": -1,
                    "max": 120,
                    "tooltip": "Durée (min) de mise en cache du modèle."
                }),
                "request_timeout": ("INT", {
                    "default": 300,
                    "min": 30,
                    "max": 3600,
                    "tooltip": "Délai max (s) pour réponse. Augmentez pour Qwen3-VL."
                }),
            },
            "optional": {
                "override_prompt": ("STRING", {"multiline": True, "default": ""}),
                "disable_thinking": ("BOOLEAN", {"default": True, "label_on": "Désactiver le raisonnement", "label_off": "Laisser activer"})
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("description", "debug_info")
    FUNCTION = "describe_image"
    CATEGORY = "🌀FMJ"

    def describe_image(
        self,
        image,
        description_type,
        model_name,
        ollama_url,
        max_tokens,
        temperature,
        seed,
        keep_alive,
        request_timeout,
        override_prompt=None,
        disable_thinking=True
    ):
        prompts = load_vision_prompts()
        
        if override_prompt and override_prompt.strip():
            system_prompt = override_prompt.strip()
        else:
            system_prompt = prompts.get(description_type)
            
        if system_prompt is None:
            error_msg = f"❌ Type '{description_type}' introuvable. Vérifiez le dossier 'csvv/'."
            return (error_msg, error_msg)

        try:
            img_b64 = tensor_to_base64(image)
        except Exception as e:
            return (f"❌ Échec conversion image : {e}", str(e))

        # --- ✅ MÉTHODE COMPATIBLE QWEN3-VL : chat + messages structurés ---
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": "Analyse l'image suivante.",
                "images": [img_b64]  # L'image est attachée AU MESSAGE UTILISATEUR
            }
        ]

        extra_options = {
            "num_predict": max_tokens,
            "temperature": temperature,
            "seed": seed
        }

        # Désactiver la trace de raisonnement pour Qwen3-VL (recommandé)
        if disable_thinking:
            extra_options["think"] = False

        client = Client(host=ollama_url.rstrip('/'))

        try:
            response = client.chat(
                model=model_name,
                messages=messages,
                options=extra_options,
                keep_alive=f"{keep_alive}m"
                # Note : Ollama Python client ne permet pas de passer request_timeout directement,
                # mais une version récente le supporte via session. On se fie à l’appel standard.
            )

            desc = response.get("message", {}).get("content", "").strip()
            if not desc:
                desc = "⚠️ Description vide de la part du modèle (Qwen3-VL n’a rien généré)."

            debug = (
                f"✅ Vision réussie\n"
                f"Type : {description_type}\n"
                f"Modèle : {model_name}\n"
                f"Timeout : {request_timeout}s"
            )
            return (desc, debug)

        except Exception as e:
            error_detail = f"❌ Erreur Vision (Ollama) : {str(e)}"
            return (error_detail, error_detail)