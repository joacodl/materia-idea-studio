from __future__ import annotations

from collections import Counter


FORMAT_CYCLE = ["reel", "carousel", "post", "story"]
PILLARS = ["producto", "educativo", "proceso/cocina", "comunidad", "promocional"]


def build_opportunities(products: list, manual_posts: list, limit: int = 20) -> list[dict]:
    posted_product_names = {p.product_name.strip().lower() for p in manual_posts if p.product_name}
    brand_counter = Counter((p.brand or "").strip().lower() for p in manual_posts if p.brand)
    category_counter = Counter((p.category or "").strip().lower() for p in manual_posts if p.category)

    opportunities: list[dict] = []
    for idx, product in enumerate(products):
        product_name = (product.name or "").strip().lower()
        brand_name = (product.brand or "").strip().lower()
        category_name = (product.category or "").strip().lower()

        product_recently_posted = product_name in posted_product_names
        brand_recent_count = brand_counter.get(brand_name, 0)
        category_recent_count = category_counter.get(category_name, 0)

        reason_parts = []
        score = float(product.visual_score or 0.0)

        if not product_recently_posted:
            reason_parts.append("Producto no registrado recientemente en Instagram manual.")
            score += 2.0
        else:
            reason_parts.append("Producto ya registrado en posteos recientes; usar como continuidad.")

        if brand_recent_count == 0 and product.brand:
            reason_parts.append(f"La marca {product.brand} no aparece en los últimos posteos manuales.")
            score += 1.0

        if category_recent_count >= 3:
            reason_parts.append(f"La categoría {product.category} está sobreusada; proponer enfoque diferencial.")
            score -= 0.5
        else:
            reason_parts.append(f"La categoría {product.category} tiene margen para sumar variedad.")
            score += 0.6

        opportunities.append(
            {
                "product_id": product.id,
                "title": f"Idea con {product.name}",
                "reason": " ".join(reason_parts),
                "suggested_format": FORMAT_CYCLE[idx % len(FORMAT_CYCLE)],
                "pillar": PILLARS[idx % len(PILLARS)],
                "score": score,
                "status": "draft",
            }
        )

    opportunities.sort(key=lambda item: item["score"], reverse=True)
    return opportunities[:limit]
