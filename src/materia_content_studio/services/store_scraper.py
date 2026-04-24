from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from materia_content_studio.services.store_selectors import SelectorConfig


@dataclass(slots=True)
class ScrapeResult:
    products: list[dict]
    visited_pages: int


class StoreScraperService:
    def __init__(
        self,
        base_url: str,
        selectors: SelectorConfig,
        request_timeout: int = 20,
        delay_seconds: float = 0.8,
        max_pages: int = 40,
    ):
        self.base_url = base_url.rstrip("/")
        self.selectors = selectors
        self.request_timeout = request_timeout
        self.delay_seconds = delay_seconds
        self.max_pages = max_pages
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Materia Content Studio Bot/1.0 (+public scraping, contact local admin)",
                "Accept-Language": "es-AR,es;q=0.9",
            }
        )

    def sync_products(self) -> ScrapeResult:
        catalog_pages = self._discover_catalog_pages()
        product_links = self._extract_product_links(catalog_pages)
        products: list[dict] = []
        for link in sorted(product_links):
            details = self._scrape_product_page(link)
            if details:
                products.append(details)
        return ScrapeResult(products=products, visited_pages=len(catalog_pages) + len(product_links))

    def _discover_catalog_pages(self) -> list[str]:
        candidates = [
            self.base_url,
            urljoin(self.base_url + "/", "productos"),
            urljoin(self.base_url + "/", "tienda"),
            urljoin(self.base_url + "/", "shop"),
        ]

        discovered: list[str] = []
        seen = set()
        for url in candidates:
            if url in seen:
                continue
            seen.add(url)
            response_text = self._safe_get(url)
            if response_text:
                discovered.append(url)
                soup = BeautifulSoup(response_text, "html.parser")
                for anchor in soup.select("a[href]"):
                    href = anchor.get("href", "")
                    absolute = self._normalize_url(href)
                    if not absolute:
                        continue
                    if absolute in seen:
                        continue
                    if self._is_same_domain(absolute) and any(token in absolute.lower() for token in ["categoria", "productos", "shop", "tienda"]):
                        seen.add(absolute)
                        discovered.append(absolute)
                    if len(discovered) >= self.max_pages:
                        break
            if len(discovered) >= self.max_pages:
                break
        return discovered

    def _extract_product_links(self, pages: Iterable[str]) -> set[str]:
        links: set[str] = set()
        for page in pages:
            html = self._safe_get(page)
            if not html:
                continue
            soup = BeautifulSoup(html, "html.parser")
            for selector in self.selectors.product_link_selectors:
                for anchor in soup.select(selector):
                    href = anchor.get("href", "")
                    absolute = self._normalize_url(href)
                    if absolute and self._is_product_url(absolute):
                        links.add(absolute)
        return links

    def _scrape_product_page(self, url: str) -> dict | None:
        html = self._safe_get(url)
        if not html:
            return None
        soup = BeautifulSoup(html, "html.parser")

        name = self._extract_text(soup, self.selectors.name_selectors)
        if not name:
            name = "Producto sin nombre"
        image_url = self._extract_asset_url(soup, self.selectors.image_selectors)
        price_text = self._extract_text(soup, self.selectors.price_selectors)
        category = self._extract_category(soup)
        brand = self._extract_text(soup, self.selectors.brand_selectors) or "Sin marca"
        description = self._extract_text(soup, self.selectors.description_selectors)
        variants_text = self._extract_variants(soup)
        availability_text = self._extract_text(soup, self.selectors.availability_selectors)

        return {
            "name": name,
            "product_url": url,
            "image_url": image_url,
            "price_text": price_text,
            "category": category,
            "brand": brand,
            "description": description,
            "variants_text": variants_text,
            "availability_text": availability_text,
            "visual_score": self._calculate_visual_score(image_url, description, availability_text),
        }

    def _safe_get(self, url: str) -> str:
        for attempt in range(3):
            try:
                response = self.session.get(url, timeout=self.request_timeout)
                if response.status_code >= 400:
                    time.sleep(self.delay_seconds)
                    continue
                time.sleep(self.delay_seconds)
                return response.text
            except requests.RequestException:
                time.sleep(self.delay_seconds * (attempt + 1))
        return ""

    def _extract_text(self, soup: BeautifulSoup, selectors: tuple[str, ...]) -> str:
        for selector in selectors:
            node = soup.select_one(selector)
            if not node:
                continue
            if node.name == "meta":
                value = node.get("content", "").strip()
            else:
                value = node.get_text(" ", strip=True)
            if value:
                return value
        return ""

    def _extract_asset_url(self, soup: BeautifulSoup, selectors: tuple[str, ...]) -> str:
        for selector in selectors:
            node = soup.select_one(selector)
            if not node:
                continue
            if node.name == "meta":
                href = node.get("content", "")
            else:
                href = node.get("src", "")
            absolute = self._normalize_url(href)
            if absolute:
                return absolute
        return ""

    def _extract_variants(self, soup: BeautifulSoup) -> str:
        options: list[str] = []
        for selector in self.selectors.variant_selectors:
            for node in soup.select(selector):
                text = node.get_text(" ", strip=True)
                if text and text.lower() not in {"elegí", "seleccionar"}:
                    options.append(text)
        unique = list(dict.fromkeys(options))
        return " | ".join(unique[:10])

    def _extract_category(self, soup: BeautifulSoup) -> str:
        breadcrumbs = []
        for selector in self.selectors.category_selectors:
            for node in soup.select(selector):
                text = node.get_text(" ", strip=True)
                if text and len(text) > 2:
                    breadcrumbs.append(text)
        if breadcrumbs:
            return breadcrumbs[-1]
        return "Sin categoría"

    def _calculate_visual_score(self, image_url: str, description: str, availability_text: str) -> float:
        score = 0.0
        if image_url:
            score += 2.0
        if description and len(description) > 80:
            score += 1.0
        if availability_text:
            score += 0.5
        return score

    def _normalize_url(self, href: str) -> str:
        if not href:
            return ""
        absolute = urljoin(self.base_url + "/", href)
        parsed = urlparse(absolute)
        if parsed.scheme not in {"http", "https"}:
            return ""
        return absolute.split("#")[0]

    def _is_same_domain(self, url: str) -> bool:
        return urlparse(url).netloc == urlparse(self.base_url).netloc

    def _is_product_url(self, url: str) -> bool:
        path = urlparse(url).path.lower()
        return any(token in path for token in ["producto", "productos", "product"])
