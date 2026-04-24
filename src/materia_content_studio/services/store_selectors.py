from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SelectorConfig:
    product_link_selectors: tuple[str, ...] = (
        "a[href*='/productos/']",
        "a[href*='/producto/']",
        "a[href*='/product/']",
        "a.product-link",
    )
    name_selectors: tuple[str, ...] = ("h1", ".product-name", ".product_title", "meta[property='og:title']")
    image_selectors: tuple[str, ...] = (
        "meta[property='og:image']",
        ".product-gallery img",
        ".product-image img",
        "img.wp-post-image",
    )
    price_selectors: tuple[str, ...] = (".price", ".product-price", "[data-testid='price']", "meta[property='product:price:amount']")
    category_selectors: tuple[str, ...] = (".breadcrumbs a", ".product-category", "[data-category]")
    brand_selectors: tuple[str, ...] = (".brand", ".product-brand", "[data-brand]")
    description_selectors: tuple[str, ...] = (".product-description", ".description", "meta[name='description']")
    variant_selectors: tuple[str, ...] = ("select option", ".variant", ".product-variants li")
    availability_selectors: tuple[str, ...] = (".stock", ".availability", "[data-stock]", ".product-availability")


def get_selector_config() -> SelectorConfig:
    return SelectorConfig()
