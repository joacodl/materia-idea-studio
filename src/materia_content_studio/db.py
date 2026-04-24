from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class SyncLog(Base):
    __tablename__ = "sync_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(40), index=True)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(300), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    brand: Mapped[str] = mapped_column(String(120), default="Sin marca", index=True)
    category: Mapped[str] = mapped_column(String(120), default="Sin categoría", index=True)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    stock: Mapped[int | None] = mapped_column(Integer, nullable=True)
    product_url: Mapped[str] = mapped_column(String(500), default="")
    created_at_remote: Mapped[str | None] = mapped_column(String(80), nullable=True)
    updated_at_remote: Mapped[str | None] = mapped_column(String(80), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    images: Mapped[list[ProductImage]] = relationship(back_populates="product", cascade="all, delete-orphan")


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    image_url: Mapped[str] = mapped_column(String(600))
    position: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped[Product] = relationship(back_populates="images")


class InstagramPost(Base):
    __tablename__ = "instagram_posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    posted_at: Mapped[str | None] = mapped_column(String(80), nullable=True)
    caption: Mapped[str] = mapped_column(Text, default="")
    post_type: Mapped[str] = mapped_column(String(40), default="POST")
    media_url: Mapped[str] = mapped_column(String(600), default="")
    permalink: Mapped[str] = mapped_column(String(600), default="")
    hashtags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class GeneratedIdea(Base):
    __tablename__ = "generated_ideas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    status: Mapped[str] = mapped_column(String(20), default="draft")
    idea_json: Mapped[dict] = mapped_column(JSON)


class Database:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{self.path}", future=True)

    def init(self) -> None:
        Base.metadata.create_all(self.engine)

    def session(self) -> Session:
        return Session(self.engine)

    def upsert_products(self, products: Iterable[dict]) -> int:
        count = 0
        with self.session() as db:
            for item in products:
                product = db.execute(
                    select(Product).where(Product.external_id == str(item["external_id"]))
                ).scalar_one_or_none()
                if not product:
                    product = Product(external_id=str(item["external_id"]))
                    db.add(product)
                product.name = item.get("name", "")
                product.description = item.get("description", "")
                product.brand = item.get("brand", "Sin marca")
                product.category = item.get("category", "Sin categoría")
                product.price = item.get("price")
                product.stock = item.get("stock")
                product.product_url = item.get("product_url", "")
                product.created_at_remote = item.get("created_at_remote")
                product.updated_at_remote = item.get("updated_at_remote")
                product.metadata_json = item.get("metadata_json")
                product.images.clear()
                for idx, image_url in enumerate(item.get("images", [])):
                    product.images.append(ProductImage(image_url=image_url, position=idx))
                count += 1
            db.commit()
        return count

    def upsert_instagram_posts(self, posts: Iterable[dict]) -> int:
        count = 0
        with self.session() as db:
            for item in posts:
                post = db.execute(
                    select(InstagramPost).where(InstagramPost.external_id == str(item["external_id"]))
                ).scalar_one_or_none()
                if not post:
                    post = InstagramPost(external_id=str(item["external_id"]))
                    db.add(post)
                post.posted_at = item.get("posted_at")
                post.caption = item.get("caption", "")
                post.post_type = item.get("post_type", "POST")
                post.media_url = item.get("media_url", "")
                post.permalink = item.get("permalink", "")
                post.hashtags = item.get("hashtags")
                post.metrics = item.get("metrics")
                count += 1
            db.commit()
        return count

    def save_generated_ideas(self, ideas: list[dict], status: str = "draft") -> None:
        with self.session() as db:
            for idea in ideas:
                db.add(GeneratedIdea(status=status, idea_json=idea))
            db.commit()

    def add_sync_log(self, source: str, details: dict | None = None) -> None:
        with self.session() as db:
            db.add(SyncLog(source=source, details=details))
            db.commit()

    def get_dashboard_stats(self) -> dict:
        with self.session() as db:
            products_count = db.scalar(select(func.count(Product.id))) or 0
            brands_count = db.scalar(select(func.count(func.distinct(Product.brand)))) or 0
            categories_count = db.scalar(select(func.count(func.distinct(Product.category)))) or 0
            instagram_count = db.scalar(select(func.count(InstagramPost.id))) or 0
            last_tienda_sync = db.execute(
                select(SyncLog).where(SyncLog.source == "tiendanube").order_by(SyncLog.synced_at.desc())
            ).scalars().first()
            return {
                "products": products_count,
                "brands": brands_count,
                "categories": categories_count,
                "instagram_posts": instagram_count,
                "last_tienda_sync": last_tienda_sync.synced_at.isoformat() if last_tienda_sync else "Nunca",
            }

    def list_products(self) -> list[Product]:
        with self.session() as db:
            return db.execute(select(Product).order_by(Product.updated_at_remote.desc().nullslast(), Product.name)).scalars().all()

    def list_instagram_posts(self, limit: int = 50) -> list[InstagramPost]:
        with self.session() as db:
            return db.execute(select(InstagramPost).order_by(InstagramPost.posted_at.desc()).limit(limit)).scalars().all()

    def list_generated_ideas(self, limit: int = 100) -> list[GeneratedIdea]:
        with self.session() as db:
            return db.execute(select(GeneratedIdea).order_by(GeneratedIdea.created_at.desc()).limit(limit)).scalars().all()
