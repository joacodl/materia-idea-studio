from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, create_engine, func, select
from typing import Iterable

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class SyncLog(Base):
    __tablename__ = "sync_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(60), index=True)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    details: Mapped[str] = mapped_column(Text, default="")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(140), unique=True, index=True)


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(140), unique=True, index=True)
    source: Mapped[str] = mapped_column(String(40), index=True)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(320), index=True)
    product_url: Mapped[str] = mapped_column(String(700), unique=True, index=True)
    image_url: Mapped[str] = mapped_column(String(700), default="")
    price_text: Mapped[str] = mapped_column(String(120), default="")
    availability_text: Mapped[str] = mapped_column(String(250), default="")
    category: Mapped[str] = mapped_column(String(140), default="Sin categoría", index=True)
    brand: Mapped[str] = mapped_column(String(140), default="Sin marca", index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    variants_text: Mapped[str] = mapped_column(Text, default="")
    visual_score: Mapped[float] = mapped_column(Float, default=0.0)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class InstagramManualPost(Base):
    __tablename__ = "instagram_manual_posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(220), default="")
    caption: Mapped[str] = mapped_column(Text, default="")
    format: Mapped[str] = mapped_column(String(30), index=True)
    product_name: Mapped[str] = mapped_column(String(220), default="", index=True)
    brand: Mapped[str] = mapped_column(String(140), default="", index=True)
    category: Mapped[str] = mapped_column(String(140), default="", index=True)
    published_date: Mapped[str] = mapped_column(String(30), default="")
    image_path: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class BrandManualEntry(Base):
    __tablename__ = "brand_manual_entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_type: Mapped[str] = mapped_column(String(20), default="text")
    source_name: Mapped[str] = mapped_column(String(250), default="")
    content: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ContentOpportunity(Base):
    __tablename__ = "content_opportunities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(300))
    reason: Mapped[str] = mapped_column(Text)
    suggested_format: Mapped[str] = mapped_column(String(40))
    pillar: Mapped[str] = mapped_column(String(60))
    score: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    product: Mapped[Product | None] = relationship()
    prompt_pack: Mapped[PromptPack | None] = relationship(back_populates="opportunity", uselist=False)


class PromptPack(Base):
    __tablename__ = "prompt_packs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("content_opportunities.id"), unique=True)
    prompt_spanish: Mapped[str] = mapped_column(Text)
    prompt_image_product: Mapped[str] = mapped_column(Text)
    prompt_image_kitchen: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    opportunity: Mapped[ContentOpportunity] = relationship(back_populates="prompt_pack")
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

    def upsert_products(self, products: list[dict]) -> int:
        with self.session() as db:
            for item in products:
                category_name = item.get("category") or "Sin categoría"
                brand_name = item.get("brand") or "Sin marca"
                self._ensure_category(db, category_name)
                self._ensure_brand(db, brand_name)

                existing = db.execute(select(Product).where(Product.product_url == item["product_url"])).scalar_one_or_none()
                if not existing:
                    existing = Product(product_url=item["product_url"], name=item.get("name") or "Producto sin nombre")
                    db.add(existing)
                existing.name = item.get("name") or existing.name
                existing.image_url = item.get("image_url") or ""
                existing.price_text = item.get("price_text") or ""
                existing.availability_text = item.get("availability_text") or ""
                existing.category = category_name
                existing.brand = brand_name
                existing.description = item.get("description") or ""
                existing.variants_text = item.get("variants_text") or ""
                existing.visual_score = float(item.get("visual_score") or 0.0)
                existing.last_seen_at = datetime.now(timezone.utc)
            db.commit()
        return len(products)

    def add_sync_log(self, source: str, details: str) -> None:
        with self.session() as db:
            db.add(SyncLog(source=source, details=details))
            db.commit()

    def save_manual_post(self, payload: dict) -> None:
        with self.session() as db:
            db.add(InstagramManualPost(**payload))
            db.commit()

    def save_brand_manual(self, source_type: str, source_name: str, content: str) -> None:
        with self.session() as db:
            db.add(BrandManualEntry(source_type=source_type, source_name=source_name, content=content))
            db.commit()

    def save_opportunities(self, opportunities: list[dict]) -> None:
        with self.session() as db:
            for item in opportunities:
                db.add(ContentOpportunity(**item))
            db.commit()

    def save_prompt_pack(self, opportunity_id: int, prompt_spanish: str, prompt_image_product: str, prompt_image_kitchen: str) -> None:
        with self.session() as db:
            existing = db.execute(select(PromptPack).where(PromptPack.opportunity_id == opportunity_id)).scalar_one_or_none()
            if existing:
                existing.prompt_spanish = prompt_spanish
                existing.prompt_image_product = prompt_image_product
                existing.prompt_image_kitchen = prompt_image_kitchen
            else:
                db.add(
                    PromptPack(
                        opportunity_id=opportunity_id,
                        prompt_spanish=prompt_spanish,
                        prompt_image_product=prompt_image_product,
                        prompt_image_kitchen=prompt_image_kitchen,
                    )
                )
            db.commit()

    def update_opportunity_status(self, opportunity_id: int, status: str) -> None:
        with self.session() as db:
            record = db.get(ContentOpportunity, opportunity_id)
            if record:
                record.status = status
                db.commit()

    def get_dashboard(self) -> dict:
        with self.session() as db:
            last_sync = db.execute(
                select(SyncLog).where(SyncLog.source == "store_scrape").order_by(SyncLog.synced_at.desc())
            ).scalars().first()
            return {
                "products": db.scalar(select(func.count(Product.id))) or 0,
                "categories": db.scalar(select(func.count(Category.id))) or 0,
                "brands": db.scalar(select(func.count(Brand.id))) or 0,
                "instagram_posts": db.scalar(select(func.count(InstagramManualPost.id))) or 0,
                "opportunities": db.scalar(select(func.count(ContentOpportunity.id))) or 0,
                "last_store_sync": last_sync.synced_at.isoformat() if last_sync else "Nunca",
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
            return db.execute(select(Product).order_by(Product.visual_score.desc(), Product.name.asc())).scalars().all()

    def list_manual_posts(self) -> list[InstagramManualPost]:
        with self.session() as db:
            return db.execute(select(InstagramManualPost).order_by(InstagramManualPost.created_at.desc())).scalars().all()

    def list_brand_manual_entries(self) -> list[BrandManualEntry]:
        with self.session() as db:
            return db.execute(select(BrandManualEntry).order_by(BrandManualEntry.created_at.desc())).scalars().all()

    def list_opportunities(self) -> list[ContentOpportunity]:
        with self.session() as db:
            return db.execute(select(ContentOpportunity).order_by(ContentOpportunity.score.desc(), ContentOpportunity.created_at.desc())).scalars().all()

    def list_prompt_packs(self) -> list[PromptPack]:
        with self.session() as db:
            return db.execute(select(PromptPack).order_by(PromptPack.created_at.desc())).scalars().all()

    @staticmethod
    def _ensure_category(db: Session, name: str) -> None:
        if not db.execute(select(Category).where(Category.name == name)).scalar_one_or_none():
            db.add(Category(name=name))

    @staticmethod
    def _ensure_brand(db: Session, name: str) -> None:
        if not db.execute(select(Brand).where(Brand.name == name)).scalar_one_or_none():
            db.add(Brand(name=name))
            return db.execute(select(Product).order_by(Product.updated_at_remote.desc().nullslast(), Product.name)).scalars().all()

    def list_instagram_posts(self, limit: int = 50) -> list[InstagramPost]:
        with self.session() as db:
            return db.execute(select(InstagramPost).order_by(InstagramPost.posted_at.desc()).limit(limit)).scalars().all()

    def list_generated_ideas(self, limit: int = 100) -> list[GeneratedIdea]:
        with self.session() as db:
            return db.execute(select(GeneratedIdea).order_by(GeneratedIdea.created_at.desc()).limit(limit)).scalars().all()
