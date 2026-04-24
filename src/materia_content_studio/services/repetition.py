from __future__ import annotations

from collections import Counter


def build_repetition_context(instagram_posts: list[dict], generated_ideas: list[dict]) -> dict:
    product_mentions = Counter()
    brand_mentions = Counter()
    category_mentions = Counter()

    for post in instagram_posts:
        caption = (post.get("caption") or "").lower()
        for token in caption.split():
            if len(token) > 4:
                product_mentions[token.strip(".,;:!?()[]")] += 1

    for idea in generated_ideas:
        for product in idea.get("products", []):
            product_mentions[product.lower()] += 1
        if idea.get("brand"):
            brand_mentions[idea["brand"].lower()] += 1
        if idea.get("category"):
            category_mentions[idea["category"].lower()] += 1

    return {
        "product_mentions": product_mentions.most_common(30),
        "brand_mentions": brand_mentions.most_common(20),
        "category_mentions": category_mentions.most_common(20),
    }


def explain_repetition_risk(idea: dict, repetition_context: dict) -> str:
    brand = (idea.get("brand") or "").lower()
    category = (idea.get("category") or "").lower()

    heavy_brands = {k for k, v in repetition_context.get("brand_mentions", []) if v >= 2}
    heavy_categories = {k for k, v in repetition_context.get("category_mentions", []) if v >= 3}

    if brand and brand in heavy_brands:
        return f"Esta idea se marca como continuación porque {idea.get('brand')} apareció seguido recientemente."
    if category and category in heavy_categories:
        return f"Esta idea se debe alternar porque la categoría {idea.get('category')} ya está bastante usada."
    return "Esta idea suma variedad y no repite una estructura reciente de forma directa."
