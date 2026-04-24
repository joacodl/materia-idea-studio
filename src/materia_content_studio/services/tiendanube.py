from __future__ import annotations

from collections.abc import Iterator

import requests

from materia_content_studio.config import Settings
from materia_content_studio.services.mock_data import mock_products

BASE_URL = "https://api.tiendanube.com/v1"


class TiendaNubeService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def fetch_products(self, use_mock_on_error: bool = True) -> list[dict]:
        if not self.settings.has_tiendanube_credentials:
            return mock_products()

        headers = {
            "Authentication": f"bearer {self.settings.tiendanube_access_token}",
            "User-Agent": self.settings.tiendanube_user_agent,
            "Content-Type": "application/json",
        }

        products: list[dict] = []
        try:
            for payload in self._paginate_products(headers):
                products.append(self._normalize_product(payload))
        except requests.RequestException:
            if use_mock_on_error:
                return mock_products()
            raise
        return products

    def _paginate_products(self, headers: dict) -> Iterator[dict]:
        page = 1
        while True:
            response = requests.get(
                f"{BASE_URL}/{self.settings.tiendanube_store_id}/products",
                headers=headers,
                params={"page": page, "per_page": 50, "fields": "id,name,description,categories,brand,variants,images,canonical_url,created_at,updated_at"},
                timeout=30,
            )
            response.raise_for_status()
            items = response.json()
            if not items:
                break
            for item in items:
                yield item
            page += 1

    def _normalize_product(self, item: dict) -> dict:
        variants = item.get("variants", [])
        first_variant = variants[0] if variants else {}
        categories = item.get("categories", [])
        category_name = categories[0].get("name", {}).get("es", "Sin categoría") if categories else "Sin categoría"
        brand = item.get("brand") or "Sin marca"
        name = item.get("name", {}).get("es") or item.get("name", {}).get("en") or "Producto sin nombre"
        description = item.get("description", {}).get("es") or item.get("description", {}).get("en") or ""
        images = [img.get("src") for img in item.get("images", []) if img.get("src")]

        return {
            "external_id": str(item.get("id")),
            "name": name,
            "description": description,
            "brand": brand,
            "category": category_name,
            "price": float(first_variant.get("price")) if first_variant.get("price") else None,
            "stock": int(first_variant.get("stock")) if first_variant.get("stock") is not None else None,
            "product_url": item.get("canonical_url", ""),
            "created_at_remote": item.get("created_at"),
            "updated_at_remote": item.get("updated_at"),
            "images": images,
            "metadata_json": {"variants": variants},
        }
