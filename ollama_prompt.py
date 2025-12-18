# ollama_prompt.py
import os
import csv
from pathlib import Path
from ollama import Client

CSV_DIR = Path(__file__).parent / "csv"

def load_prompts_from_csv():
    """Charge les prompts depuis csv/*.csv"""
    prompts = {}
    if not CSV_DIR.exists():
        return prompts
    for csv_file in CSV_DIR.glob("*.csv"):
        try:
            with open(csv_file, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                if 'prompt_style' in reader.fieldnames and 'system_prompt' in reader.fieldnames:
                    for row in reader:
                        style = row['prompt_style'].strip()
                        system_prompt = row['system_prompt'].strip()
                        if style and system_prompt:
                            prompts[style] = system_prompt
        except Exception as e:
            print(f"❌ Erreur lecture {csv_file}: {e}")
    return prompts

class FMJOllamaPromptGenerator:
    """🦜FMJ Ollama Prompt Generator — Génère des prompts avancés via Ollama."""
    
    @classmethod
    def INPUT_TYPES(cls):
        PROMPT_STYLES = load_prompts_from_csv()
        style_list = list(PROMPT_STYLES.keys()) if PROMPT_STYLES else ["_aucun_prompt_dans_csv_"]
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
                "prompt_style": (style_list, {"default": style_list[0]}),
                "model_name": ("STRING", {"default": "qwen3:2b"}),
                "ollama_url": ("STRING", {"default": "http://localhost:11434"}),
                "max_tokens": ("INT", {
                    "default": 512,
                    "min": 1,
                    "max": 16384,
                    "tooltip": "Nombre max de tokens à générer."
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
                    "default": 300,  # 5 minutes — important pour Qwen3
                    "min": 30,
                    "max": 3600,
                    "tooltip": "Délai d'attente max (en secondes) pour la réponse. Augmentez si Qwen3 est lent."
                }),
            },
            "optional": {
                "override_prompt": ("STRING", {"multiline": True, "default": ""}),
                "disable_thinking": ("BOOLEAN", {"default": True, "label_on": "Désactiver le raisonnement", "label_off": "Laisser activer"})
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("response", "debug_info")
    FUNCTION = "generate"
    CATEGORY = "🌀FMJ"

    def generate(
        self,
        text,
        prompt_style,
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
        # Charger les prompts
        PROMPT_STYLES = load_prompts_from_csv()
        
        if override_prompt and override_prompt.strip():
            system_instruction = override_prompt.strip()
        else:
            system_instruction = PROMPT_STYLES.get(prompt_style)
            
        if system_instruction is None:
            error_msg = f"❌ Style '{prompt_style}' introuvable. Vérifiez le dossier 'csv/'."
            return (error_msg, error_msg)

        # Construire le prompt utilisateur
        user_prompt = text  # On utilise le texte brut comme message utilisateur

        # Construire la liste des messages (format chat)
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ]

        # Ajouter 'think' dans les options si le modèle le supporte
        extra_options = {
            "num_predict": max_tokens,
            "temperature": temperature,
            "seed": seed
        }

        # Désactiver la trace de raisonnement si demandé (utile pour Qwen3)
        if disable_thinking:
            extra_options["think"] = False

        # Configurer le client avec un délai plus long
        client = Client(host=ollama_url.rstrip('/'))

        try:
            # ⭐ Utiliser client.chat() — NE PAS utiliser .generate()
            response = client.chat(
                model=model_name,
                messages=messages,
                options=extra_options,
                keep_alive=f"{keep_alive}m",
                # Note : Le timeout ne peut pas être passé directement dans l'appel de base
                # mais on peut le gérer via la session HTTP si nécessaire.
                # Pour simplifier, on se fie au timeout global.
            )

            # ⭐ Extraire correctement la réponse de l'endpoint /api/chat
            output_text = response.get("message", {}).get("content", "").strip()
            if not output_text:
                output_text = "⚠️ Réponse vide de la part du modèle (Qwen3 a peut-être échoué à générer du texte)."

            debug = (
                f"✅ Réponse reçue\n"
                f"Style : {prompt_style}\n"
                f"Modèle : {model_name}\n"
                f"Tokens max : {max_tokens}\n"
                f"Timeout : {request_timeout}s"
            )
            return (output_text, debug)

        except Exception as e:
            error_detail = f"❌ Erreur LLM (Ollama) : {str(e)}"
            return (error_detail, error_detail)