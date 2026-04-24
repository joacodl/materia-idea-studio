from __future__ import annotations

from datetime import datetime, timedelta, timezone


def mock_products() -> list[dict]:
    return [
        {
            "external_id": "tn-1001",
            "name": "Chocolate cobertura semiamargo 1kg",
            "description": "Cobertura para baños, moldeado y ganache estable.",
            "brand": "Mapricuber",
            "category": "Chocolates",
            "price": 14500,
            "stock": 18,
            "product_url": "https://materia.tiendanube.com/productos/chocolate-cobertura-semiamargo-1kg",
            "created_at_remote": "2026-03-20T10:00:00Z",
            "updated_at_remote": "2026-04-22T14:30:00Z",
            "images": [
                "https://images.unsplash.com/photo-1511381939415-e44015466834",
                "https://images.unsplash.com/photo-1606312619344-24a7cc2a6af9",
            ],
            "metadata_json": {"source": "mock"},
        },
        {
            "external_id": "tn-1002",
            "name": "Esencia de vainilla Naarden 500cc",
            "description": "Aporta aroma intenso en batidos, cremas y almíbares.",
            "brand": "Naarden",
            "category": "Esencias",
            "price": 8200,
            "stock": 42,
            "product_url": "https://materia.tiendanube.com/productos/esencia-de-vainilla-naarden",
            "created_at_remote": "2026-02-11T09:10:00Z",
            "updated_at_remote": "2026-04-19T12:11:00Z",
            "images": ["https://images.unsplash.com/photo-1470337458703-46ad1756a187"],
            "metadata_json": {"source": "mock"},
        },
        {
            "external_id": "tn-1003",
            "name": "Colorante liposoluble rojo 25g",
            "description": "Ideal para chocolates y baños grasos.",
            "brand": "Acuarel",
            "category": "Colorantes",
            "price": 5100,
            "stock": 35,
            "product_url": "https://materia.tiendanube.com/productos/colorante-liposoluble-rojo",
            "created_at_remote": "2026-04-01T11:30:00Z",
            "updated_at_remote": "2026-04-23T16:20:00Z",
            "images": ["https://images.unsplash.com/photo-1488477181946-6428a0291777"],
            "metadata_json": {"source": "mock"},
        },
    ]


def mock_instagram_posts() -> list[dict]:
    now = datetime.now(timezone.utc)
    return [
        {
            "external_id": "ig-3001",
            "posted_at": (now - timedelta(days=3)).isoformat(),
            "caption": "Hoy trabajamos cobertura semiamargo para baño espejo. Te mostramos cómo lograr brillo sin vetas.",
            "post_type": "REEL",
            "media_url": "https://images.unsplash.com/photo-1571115764595-644a1f56a55c",
            "permalink": "https://instagram.com/p/mock1",
            "hashtags": ["#chocolate", "#pasteleria", "#materiamartinez"],
            "metrics": {"likes": 214, "comments": 18},
        },
        {
            "external_id": "ig-3002",
            "posted_at": (now - timedelta(days=8)).isoformat(),
            "caption": "Tips para usar esencia de vainilla en budines de alta rotación.",
            "post_type": "CAROUSEL",
            "media_url": "https://images.unsplash.com/photo-1517686469429-8bdb88b9f907",
            "permalink": "https://instagram.com/p/mock2",
            "hashtags": ["#esencias", "#pasteleriaprofesional"],
            "metrics": {"likes": 176, "comments": 10},
        },
    ]
