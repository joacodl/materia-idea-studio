from __future__ import annotations

from pathlib import Path

import streamlit as st

from materia_content_studio.config import get_settings
from materia_content_studio.db import Database
from materia_content_studio.services.brand_manual import BrandManualService
from materia_content_studio.services.idea_generator import IdeaGeneratorService
from materia_content_studio.services.instagram import InstagramService
from materia_content_studio.services.repetition import build_repetition_context
from materia_content_studio.services.tiendanube import TiendaNubeService


PALETTE_CSS = """
<style>
:root {
    --stone: #2A2A2A;
    --cacao: #8C7766;
    --ivory: #EEE9E3;
}
.stApp {
    background-color: var(--ivory);
    color: var(--stone);
}
h1, h2, h3 {
    color: var(--stone);
}
.stButton button {
    background-color: var(--cacao);
    color: var(--ivory);
    border: none;
}
</style>
"""


def run() -> None:
    st.set_page_config(page_title="Materia Content Studio", page_icon="🍰", layout="wide")
    st.markdown(PALETTE_CSS, unsafe_allow_html=True)

    settings = get_settings()

    if not _authenticate(settings.app_password):
        return

    db = Database(settings.database_path)
    db.init()

    settings = get_settings()
    db = Database(settings.database_path)
    db.init()

    st.set_page_config(page_title="Materia Content Studio", page_icon="🍰", layout="wide")
    st.markdown(PALETTE_CSS, unsafe_allow_html=True)
    st.title("Materia Content Studio")
    st.caption("Asistente editorial para Instagram de Materia Insumos Pasteleros")

    if settings.auto_sync_on_startup and "auto_synced" not in st.session_state:
        _sync_catalog(db, settings)
        _sync_instagram(db, settings)
        st.session_state["auto_synced"] = True

    with st.sidebar:
        if st.button("Cerrar sesión", use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()
        page = st.radio(
            "Navegación",
            ["Configuración", "Sincronización", "Catálogo", "Instagram", "Generador de ideas", "Historial"],
        )
    page = st.sidebar.radio(
        "Navegación",
        ["Configuración", "Sincronización", "Catálogo", "Instagram", "Generador de ideas", "Historial"],
    )

    if page == "Configuración":
        render_configuration_page(settings)
    elif page == "Sincronización":
        render_sync_page(db, settings)
    elif page == "Catálogo":
        render_catalog_page(db)
    elif page == "Instagram":
        render_instagram_page(db)
    elif page == "Generador de ideas":
        render_idea_generator_page(db, settings)
    elif page == "Historial":
        render_history_page(db)


def _authenticate(app_password: str) -> bool:
    st.title("Materia Content Studio")
    st.caption("Acceso privado")

    if not app_password:
        st.error("Falta configurar APP_PASSWORD en variables de entorno o secretos de Streamlit Cloud.")
        st.stop()

    if st.session_state.get("authenticated"):
        return True

    with st.form("login_form"):
        password_input = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Ingresar")

    if submitted:
        if password_input == app_password:
            st.session_state["authenticated"] = True
            st.success("Acceso concedido.")
            st.rerun()
        st.error("Contraseña incorrecta.")

    st.info("Ingresá la contraseña para continuar.")
    return False


def render_configuration_page(settings) -> None:
    st.subheader("Configuración")
    st.write("Completá variables de entorno (local) o Secrets (cloud) para habilitar conectores reales.")

    st.markdown("### Estado de credenciales")
    st.write(f"Acceso privado: {'✅ Configurado' if settings.has_app_password else '⚠️ Falta APP_PASSWORD'}")
def render_configuration_page(settings) -> None:
    st.subheader("Configuración")
    st.write("Completá las variables en tu archivo .env para habilitar conectores reales.")

    st.markdown("### Estado de credenciales")
    st.write(f"Tienda Nube: {'✅ Configurado' if settings.has_tiendanube_credentials else '⚠️ Faltan credenciales'}")
    st.write(f"Instagram Graph API: {'✅ Configurado' if settings.has_instagram_credentials else '⚠️ Faltan credenciales'}")
    st.write(f"Proveedor de IA: **{settings.ai_provider}**")

    st.markdown("### Manual de marca")
    brand_service = BrandManualService(Path("data/brand_manual_path.txt"))
    upload = st.file_uploader("Subí tu manual de marca (PDF o TXT)", type=["pdf", "txt"])
    if upload and st.button("Guardar manual"):
        path = brand_service.save_uploaded_file(upload.name, upload.getvalue())
        st.success(f"Manual guardado en {path}")
    if st.button("Ver texto detectado"):
        manual_text = brand_service.get_manual_text()
        st.text_area("Extracto del manual", value=manual_text[:4000], height=300)


def render_sync_page(db: Database, settings) -> None:
    st.subheader("Dashboard y sincronización")
    stats = db.get_dashboard_stats()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Última sync Tienda Nube", stats["last_tienda_sync"])
    c2.metric("Productos", stats["products"])
    c3.metric("Marcas", stats["brands"])
    c4.metric("Categorías", stats["categories"])
    c5.metric("Posts de Instagram", stats["instagram_posts"])

    col1, col2, col3 = st.columns(3)
    if col1.button("Generar ideas", use_container_width=True):
        st.info("Andá a la pestaña Generador de ideas.")
        st.switch_page("pages/placeholder.py") if False else st.info("Andá a la pestaña Generador de ideas.")
    if col2.button("Sincronizar catálogo", use_container_width=True):
        _sync_catalog(db, settings)
    if col3.button("Sincronizar Instagram", use_container_width=True):
        _sync_instagram(db, settings)


def _sync_catalog(db: Database, settings) -> None:
    with st.spinner("Sincronizando catálogo desde Tienda Nube..."):
        service = TiendaNubeService(settings)
        products = service.fetch_products(use_mock_on_error=True)
        count = db.upsert_products(products)
        db.add_sync_log("tiendanube", {"count": count, "mock": not settings.has_tiendanube_credentials})
    st.success(f"Catálogo sincronizado. Productos procesados: {count}")


def _sync_instagram(db: Database, settings) -> None:
    with st.spinner("Sincronizando Instagram..."):
        service = InstagramService(settings)
        posts = service.fetch_recent_posts(use_mock_on_error=True)
        count = db.upsert_instagram_posts(posts)
        db.add_sync_log("instagram", {"count": count, "mock": not settings.has_instagram_credentials})
    st.success(f"Instagram sincronizado. Publicaciones procesadas: {count}")


def render_catalog_page(db: Database) -> None:
    st.subheader("Catálogo")
    products = db.list_products()
    if not products:
        st.info("No hay productos guardados todavía. Usá Sincronización para cargar datos.")
        return

    filter_brand = st.selectbox("Filtrar por marca", ["Todas"] + sorted({p.brand for p in products}))
    filter_category = st.selectbox("Filtrar por categoría", ["Todas"] + sorted({p.category for p in products}))

    for product in products:
        if filter_brand != "Todas" and product.brand != filter_brand:
            continue
        if filter_category != "Todas" and product.category != filter_category:
            continue
        with st.expander(f"{product.name} · {product.brand}"):
            st.write(f"**Categoría:** {product.category}")
            st.write(f"**Precio:** ${product.price if product.price else '-'}")
            st.write(f"**Stock:** {product.stock if product.stock is not None else '-'}")
            st.write(product.description)
            if product.product_url:
                st.link_button("Ver producto", product.product_url)
            if product.images:
                st.image([img.image_url for img in product.images], width=140)


def render_instagram_page(db: Database) -> None:
    st.subheader("Instagram")
    posts = db.list_instagram_posts(limit=100)
    if not posts:
        st.info("No hay publicaciones analizadas todavía.")
        return
    for post in posts:
        with st.container(border=True):
            st.write(f"**Tipo:** {post.post_type} · **Fecha:** {post.posted_at}")
            st.write(post.caption)
            if post.hashtags:
                st.caption(" ".join(post.hashtags))
            if post.media_url:
                st.image(post.media_url, width=200)
            if post.permalink:
                st.link_button("Abrir en Instagram", post.permalink)


def render_idea_generator_page(db: Database, settings) -> None:
    st.subheader("Generador de ideas")

    products = db.list_products()
    instagram_posts = db.list_instagram_posts(limit=60)
    previous = [item.idea_json for item in db.list_generated_ideas(limit=200)]

    if not products:
        st.warning("Primero sincronizá el catálogo para generar ideas basadas en productos reales.")
        return

    mode = st.selectbox(
        "Base de generación",
        [
            "Plan semanal",
            "Producto específico",
            "Marca específica",
            "Categoría",
            "Productos nunca posteados",
            "Productos visualmente fuertes",
            "Productos nuevos",
        ],
    )
    quantity = st.slider("Cantidad de ideas", min_value=1, max_value=12, value=6)

    selected_products = [
        {
            "name": p.name,
            "brand": p.brand,
            "category": p.category,
            "description": p.description,
            "images": [img.image_url for img in p.images],
            "updated_at_remote": p.updated_at_remote,
        }
        for p in products
    ]
    selected_posts = [
        {"caption": p.caption, "post_type": p.post_type, "posted_at": p.posted_at, "hashtags": p.hashtags}
        for p in instagram_posts
    ]

    repetition_context = build_repetition_context(selected_posts, previous)
    brand_service = BrandManualService(Path("data/brand_manual_path.txt"))

    if st.button("Generar ideas para esta semana", type="primary"):
        generator = IdeaGeneratorService(settings)
        ideas = generator.generate_ideas(
            products=selected_products,
            instagram_posts=selected_posts,
            manual_text=brand_service.get_manual_text(),
            repetition_context=repetition_context,
            mode=mode,
            count=quantity,
        )
        db.save_generated_ideas(ideas)
        st.success(f"Se generaron {len(ideas)} ideas y se guardaron en historial.")
        for idx, idea in enumerate(ideas, start=1):
            st.markdown(f"### Idea {idx}: {idea.get('main_idea', 'Sin título')} ")
            st.write(f"**Producto(s):** {', '.join(idea.get('products', []))}")
            st.write(f"**Marca:** {idea.get('brand', '-')}")
            st.write(f"**Categoría:** {idea.get('category', '-')}")
            st.write(f"**Formato:** {idea.get('format', '-')}")
            st.write(f"**Pilar:** {idea.get('pillar', '-')}")
            st.write(f"**Dirección visual:** {idea.get('visual_direction', '-')}")
            st.write(f"**Texto on-screen:** {idea.get('on_screen_text', '-')}")
            st.write(f"**Caption:** {idea.get('caption', '-')}")
            st.write(f"**CTA:** {idea.get('cta', '-')}")
            st.write(f"**Hashtags:** {' '.join(idea.get('hashtags', []))}")
            st.write(f"**Prompt IA (producto):** `{idea.get('prompt_product_style', '-')}`")
            st.write(f"**Prompt IA (cocina):** `{idea.get('prompt_kitchen_style', '-')}`")
            if idea.get("shot_list"):
                st.write("**Shot list (reel):**")
                for shot in idea["shot_list"]:
                    st.write(f"- {shot}")
            st.info(idea.get("repetition_note", ""))
            st.caption(f"Por qué esta idea tiene sentido: {idea.get('rationale', '-')}")


def render_history_page(db: Database) -> None:
    st.subheader("Historial")
    ideas = db.list_generated_ideas(limit=200)
    if not ideas:
        st.info("Todavía no hay ideas generadas.")
        return

    status_filter = st.selectbox("Filtrar estado", ["Todos", "draft", "used", "discarded"])
    for record in ideas:
        if status_filter != "Todos" and record.status != status_filter:
            continue
        idea = record.idea_json
        with st.expander(f"{record.created_at.date()} · {idea.get('main_idea', 'Idea')}"):
            st.write(f"Estado: {record.status}")
            st.json(idea)
