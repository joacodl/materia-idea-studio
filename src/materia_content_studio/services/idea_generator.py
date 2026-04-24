from __future__ import annotations

import json
from random import choice

from anthropic import Anthropic
from openai import OpenAI

from materia_content_studio.config import Settings
from materia_content_studio.services.repetition import explain_repetition_risk

FORMAT_OPTIONS = ["Reel 9:16", "Post 4:5", "Carousel 4:5", "Story 9:16"]
PILLARS = ["producto", "educativo", "proceso/cocina", "comunidad", "promocional"]


class IdeaGeneratorService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def generate_ideas(
        self,
        products: list[dict],
        instagram_posts: list[dict],
        manual_text: str,
        repetition_context: dict,
        mode: str,
        count: int = 5,
    ) -> list[dict]:
        if self.settings.ai_provider == "openai":
            return self._generate_with_openai(products, instagram_posts, manual_text, repetition_context, mode, count)
        if self.settings.ai_provider == "anthropic":
            return self._generate_with_anthropic(products, instagram_posts, manual_text, repetition_context, mode, count)
        return self._generate_mock(products, repetition_context, mode, count)

    def _prompt(self, products: list[dict], instagram_posts: list[dict], manual_text: str, repetition_context: dict, mode: str, count: int) -> str:
        return (
            "Sos editor/a de contenidos de Materia Insumos Pasteleros (Martínez, Buenos Aires). "
            "Devolvé JSON puro con una clave 'ideas' que contenga una lista. "
            "Todo en español rioplatense con voseo, excepto prompts visuales que deben ir en inglés. "
            "Evitá clichés y explicá uso real del producto. "
            f"Modo: {mode}. Cantidad: {count}.\n"
            "Cada idea debe incluir: products, brand, category, format, pillar, main_idea, visual_direction, on_screen_text, "
            "caption, cta, hashtags, prompt_product_style, prompt_kitchen_style, shot_list, rationale.\n"
            f"Productos: {json.dumps(products[:20], ensure_ascii=False)}\n"
            f"Instagram reciente: {json.dumps(instagram_posts[:20], ensure_ascii=False)}\n"
            f"Manual de marca: {manual_text[:3000]}\n"
            f"Contexto de repetición: {json.dumps(repetition_context, ensure_ascii=False)}"
        )

    def _generate_with_openai(self, products: list[dict], instagram_posts: list[dict], manual_text: str, repetition_context: dict, mode: str, count: int) -> list[dict]:
        client = OpenAI(api_key=self.settings.openai_api_key)
        response = client.responses.create(
            model=self.settings.openai_model,
            input=self._prompt(products, instagram_posts, manual_text, repetition_context, mode, count),
            temperature=0.7,
        )
        text = response.output_text
        payload = json.loads(text)
        ideas = payload.get("ideas", [])
        for idea in ideas:
            idea["repetition_note"] = explain_repetition_risk(idea, repetition_context)
        return ideas

    def _generate_with_anthropic(self, products: list[dict], instagram_posts: list[dict], manual_text: str, repetition_context: dict, mode: str, count: int) -> list[dict]:
        client = Anthropic(api_key=self.settings.anthropic_api_key)
        message = client.messages.create(
            model=self.settings.anthropic_model,
            max_tokens=4000,
            temperature=0.7,
            messages=[{"role": "user", "content": self._prompt(products, instagram_posts, manual_text, repetition_context, mode, count)}],
        )
        payload = json.loads(message.content[0].text)
        ideas = payload.get("ideas", [])
        for idea in ideas:
            idea["repetition_note"] = explain_repetition_risk(idea, repetition_context)
        return ideas

    def _generate_mock(self, products: list[dict], repetition_context: dict, mode: str, count: int) -> list[dict]:
        ideas: list[dict] = []
        selected = products[: max(count, 1)]
        for idx, product in enumerate(selected, start=1):
            format_choice = choice(FORMAT_OPTIONS)
            is_reel = format_choice.startswith("Reel")
            idea = {
                "products": [product.get("name")],
                "brand": product.get("brand"),
                "category": product.get("category"),
                "format": format_choice,
                "pillar": choice(PILLARS),
                "main_idea": f"Mostrar {product.get('name')} en un caso real de producción para {mode}.",
                "visual_direction": "Luz natural cálida, encuadre limpio, texturas reales y manos en acción.",
                "on_screen_text": f"Cómo usar {product.get('name')} sin complicarte",
                "caption": (
                    f"Si querés resultados parejos en pastelería, probá {product.get('name')}. "
                    "Te mostramos para qué sirve, en qué momento sumarlo y cómo impacta en el resultado final."
                ),
                "cta": "Si lo querés para tu producción o para revender, escribinos y te asesoramos.",
                "hashtags": ["#materiainsumos", "#pasteleria", "#martinez", f"#{product.get('category', '').lower()}"],
                "prompt_product_style": (
                    f"Editorial food photography of {product.get('name')}, warm natural light, stone and ivory palette, "
                    "clean composition, realistic texture, no catalog style, 4:5 aspect ratio"
                ),
                "prompt_kitchen_style": (
                    f"Documentary pastry kitchen scene using {product.get('name')}, hands working, visible ingredients, "
                    "natural imperfections, warm tones, artisanal mood, 9:16 aspect ratio"
                ),
                "shot_list": [
                    "Plano detalle del producto y etiqueta",
                    "Manos incorporando el producto en preparación",
                    "Resultado final con textura en primer plano",
                ]
                if is_reel
                else [],
                "rationale": (
                    "Se eligió por potencial visual del envase y por utilidad técnica en recetas de alta rotación."
                ),
            }
            idea["repetition_note"] = explain_repetition_risk(idea, repetition_context)
            ideas.append(idea)
            if idx >= count:
                break
        return ideas
