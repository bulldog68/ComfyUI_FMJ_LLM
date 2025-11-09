import os
import csv
import requests
import time
from pathlib import Path

# Chemin vers le dossier contenant les CSV
CSV_DIR = Path(__file__).parent / "csv"

def load_prompts_from_csv():
    """Charge tous les prompts depuis les fichiers CSV dans le dossier csv/"""
    prompts = {}
    if not CSV_DIR.exists():
        print(f"⚠️ Dossier {CSV_DIR} non trouvé. Aucun prompt chargé.")
        return prompts

    for csv_file in CSV_DIR.glob("*.csv"):
        try:
            with open(csv_file, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                if 'prompt_style' not in reader.fieldnames or 'system_prompt' not in reader.fieldnames:
                    print(f"⚠️ Fichier ignoré ({csv_file}): colonnes manquantes. Attendu: prompt_style, system_prompt")
                    continue
                for row in reader:
                    style = row['prompt_style'].strip()
                    system_prompt = row['system_prompt'].strip()
                    if style and system_prompt:
                        prompts[style] = system_prompt
        except Exception as e:
            print(f"❌ Erreur lecture {csv_file}: {e}")
    return prompts

class OllamaPromptNode:
    @classmethod
    def INPUT_TYPES(cls):
        # Recharger à chaque appel pour permettre l'ajout dynamique de CSV
        PROMPT_STYLES = load_prompts_from_csv()
        if not PROMPT_STYLES:
            # Fallback minimal si aucun CSV n’est trouvé (évite un crash)
            style_list = ["photo"]
        else:
            style_list = list(PROMPT_STYLES.keys())

        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "une femme rousse en robe jaune"}),
                "prompt_style": (style_list, {"default": style_list[0]}),
                "max_tokens": ("INT", {"default": 256, "min": 1, "max": 2048}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 10.0, "step": 0.1}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "unload_after_use": (["no", "yes"], {"default": "no"}),
            },
            "optional": {
                "model_name": ("STRING", {"default": "qwen3"}),
                "ollama_url": ("STRING", {"default": "http://localhost:11434"})
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("response", "debug_info")
    FUNCTION = "generate"
    CATEGORY = "FMJ"
    OUTPUT_NODE = True

    def generate(self, prompt, prompt_style, max_tokens, temperature, seed, unload_after_use, model_name="qwen3", ollama_url="http://localhost:11434"):
        url = f"{ollama_url.rstrip('/')}/api/generate"
        keep_alive = 0 if unload_after_use == "yes" else -1

        # Recharger les prompts à l'exécution
        PROMPT_STYLES = load_prompts_from_csv()
        system_instruction = PROMPT_STYLES.get(prompt_style)

        if system_instruction is None:
            error_msg = f"❌ Style non trouvé : '{prompt_style}'. Vérifiez les fichiers CSV dans {CSV_DIR}"
            return (error_msg, error_msg)

        # Construction du prompt selon le style
        if prompt_style == "qwen_edit":
            full_prompt = system_instruction + "\n" + prompt
        else:
            full_prompt = f"{system_instruction}\n\nSujet : {prompt}\n\nRéponse :"

        payload = {
            "model": model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "seed": seed
            },
            "keep_alive": keep_alive
        }

        try:
            start = time.time()
            response = requests.post(url, json=payload, timeout=300)
            elapsed = time.time() - start

            if response.status_code == 200:
                resp = response.json()
                text = resp.get("response", "").strip()
                debug = (f"✅ Style : {prompt_style}\nModèle : {model_name}\n⏱️ {elapsed:.1f}s")
                return (text, debug)
            else:
                return (f"❌ Erreur HTTP {response.status_code}", str(response.text))
        except Exception as e:
            return (f"❌ Exception", str(e))