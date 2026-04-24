from __future__ import annotations


def build_prompt_pack(product, opportunity, brand_manual_text: str) -> dict:
    short_manual = (brand_manual_text or "").strip()[:1800]

    prompt_spanish = f"""
Actuá como estratega de contenidos para Materia Insumos Pasteleros (Martínez, Buenos Aires).

Contexto del producto:
- Producto: {product.name}
- Marca: {product.brand}
- Categoría: {product.category}
- Precio visible: {product.price_text or 'No visible'}
- Disponibilidad: {product.availability_text or 'No visible'}
- Descripción: {product.description or 'Sin descripción'}
- Variantes: {product.variants_text or 'Sin variantes visibles'}

Objetivo editorial:
- Formato sugerido: {opportunity.suggested_format}
- Pilar de contenido: {opportunity.pillar}
- Motivo de oportunidad: {opportunity.reason}

Indicaciones de tono:
- Español rioplatense con voseo.
- Frases cortas, claras, cálidas y profesionales.
- Evitá clichés de marketing.
- Explicá para qué sirve el producto, cómo se usa y por qué importa.

Manual de marca (resumen):
{short_manual or 'No cargado.'}

Necesito que me devuelvas:
1) 3 opciones de caption.
2) 3 CTAs.
3) 10 hashtags relevantes.
4) Idea de guion breve para reel y variante para post/carrusel.
""".strip()

    prompt_image_product = (
        f"Editorial food product photography of {product.name}, warm natural light, stone and ivory palette, "
        f"clean artisanal composition, realistic textures, no catalog look, 4:5 aspect ratio"
    )

    prompt_image_kitchen = (
        f"Documentary pastry kitchen scene using {product.name}, hands in action, ingredients visible, "
        f"natural imperfections, warm tones, clean but real environment, 9:16 aspect ratio"
    )

    return {
        "prompt_spanish": prompt_spanish,
        "prompt_image_product": prompt_image_product,
        "prompt_image_kitchen": prompt_image_kitchen,
    }
