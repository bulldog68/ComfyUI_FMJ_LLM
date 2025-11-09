import requests
import base64
import torch
from io import BytesIO
from PIL import Image as PILImage
import time
import csv
from pathlib import Path

def tensor_to_base64(image_tensor):
    image = image_tensor.squeeze(0)
    image = torch.clamp(image * 255, 0, 255).byte()
    pil_img = PILImage.fromarray(image.cpu().numpy(), mode="RGB")
    buffered = BytesIO()
    pil_img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

CSVV_DIR = Path(__file__).parent / "csvv"

def load_vision_prompts():
    """Charge les prompts uniquement depuis csvv/*.csv"""
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
        except Exception:
            continue
    return prompts

class OllamaVisionNode:
    @classmethod
    def INPUT_TYPES(cls):
        prompts = load_vision_prompts()
        desc_types = list(prompts.keys())
        if not desc_types:
            desc_types = ["_aucun_fichier_dans_csvv_"]
        return {
            "required": {
                "image": ("IMAGE",),
                "description_type": (desc_types, {"default": desc_types[0]}),
                "max_tokens": ("INT", {"default": 256, "min": 1, "max": 4096}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 10.0, "step": 0.1}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "unload_after_use": (["no", "yes"], {"default": "no"}),
            },
            "optional": {
                "model_name": ("STRING", {"default": "moondream"}),
                "ollama_url": ("STRING", {"default": "http://localhost:11434"})
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("description", "debug_info")
    FUNCTION = "describe_image"
    CATEGORY = "FMJ"
    # ⚠️ OUTPUT_NODE = True EST INTENTIONNELLEMENT OMITTED pour permettre le rechargement dynamique

    def describe_image(self, image, description_type, max_tokens, temperature, seed, unload_after_use, model_name="moondream", ollama_url="http://localhost:11434"):
        url = f"{ollama_url.rstrip('/')}/api/chat"
        keep_alive = 0 if unload_after_use == "yes" else -1

        prompts = load_vision_prompts()
        base_prompt = prompts.get(description_type)

        if base_prompt is None:
            error_msg = f"❌ Prompt non trouvé pour '{description_type}'. Ajoutez un fichier CSV dans 'csvv/' et cliquez sur 🔄 Refresh."
            return (error_msg, error_msg)

        try:
            img_b64 = tensor_to_base64(image)
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": base_prompt, "images": [img_b64]}],
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "seed": seed
                },
                "keep_alive": keep_alive
            }

            start = time.time()
            response = requests.post(url, json=payload, timeout=300)
            elapsed = time.time() - start

            if response.status_code == 200:
                desc = response.json().get("message", {}).get("content", "").strip()
                debug = f"✅ Type : {description_type}\nModèle : {model_name}\n⏱️ {elapsed:.1f}s"
                return (desc, debug)
            else:
                return (f"❌ Erreur HTTP {response.status_code}", response.text)
        except Exception as e:
            return (f"❌ Exception", str(e))