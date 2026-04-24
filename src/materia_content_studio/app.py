from __future__ import annotations

from datetime import date
from pathlib import Path

import streamlit as st

from materia_content_studio.config import get_settings
from materia_content_studio.db import Database
from materia_content_studio.services.brand_manual import BrandManualParser
from materia_content_studio.services.opportunity_engine import build_opportunities
from materia_content_studio.services.prompt_builder import build_prompt_pack
from materia_content_studio.services.store_scraper import StoreScraperService
from materia_content_studio.services.store_selectors import get_selector_config
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

    settings.uploads_path.mkdir(parents=True, exist_ok=True)
    settings.brand_manual_path.mkdir(parents=True, exist_ok=True)

    db = Database(settings.database_path)
    db.init()

    st.title("Materia Content Studio")
    st.caption("Asistente editorial privado sin APIs externas")

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
            [
                "Inicio",
                "Sincronizar tienda",
                "Catálogo",
                "Instagram manual",
                "Manual de marca",
                "Oportunidades de contenido",
                "Generador de prompts",
                "Historial",
            ],
        )

    if page == "Inicio":
        render_home_page(db, settings.store_base_url)
    elif page == "Sincronizar tienda":
        render_sync_store_page(db, settings.store_base_url)
    elif page == "Catálogo":
        render_catalog_page(db)
    elif page == "Instagram manual":
        render_manual_instagram_page(db, settings.uploads_path)
    elif page == "Manual de marca":
        render_brand_manual_page(db, settings.brand_manual_path)
    elif page == "Oportunidades de contenido":
        render_opportunities_page(db)
    elif page == "Generador de prompts":
        render_prompt_generator_page(db)
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
        st.error("Falta configurar APP_PASSWORD en variables de entorno o en Secrets del deploy.")
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
        else:
            st.error("Contraseña incorrecta.")

    st.info("Ingresá la contraseña para usar la aplicación.")
    return False


def render_home_page(db: Database, store_base_url: str) -> None:
    st.subheader("Inicio")
    stats = db.get_dashboard()
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Productos", stats["products"])
    c2.metric("Categorías", stats["categories"])
    c3.metric("Marcas", stats["brands"])
    c4.metric("Posts IG manuales", stats["instagram_posts"])
    c5.metric("Oportunidades", stats["opportunities"])
    c6.metric("Última sync tienda", stats["last_store_sync"])

    st.info(
        f"Tienda configurada para scraping público: {store_base_url}. "
        "No se usan APIs externas ni claves de IA dentro de la app."
    )


def render_sync_store_page(db: Database, store_base_url: str) -> None:
    st.subheader("Sincronizar tienda")
    st.write("Esta sección hace scraping público de la tienda con rate limiting y reintentos.")

    if st.button("Sincronizar tienda", type="primary"):
        with st.spinner("Scrapeando tienda pública..."):
            scraper = StoreScraperService(store_base_url, selectors=get_selector_config())
            result = scraper.sync_products()
            count = db.upsert_products(result.products)
            db.add_sync_log("store_scrape", f"Productos: {count}, páginas visitadas: {result.visited_pages}")
        st.success(f"Sincronización completa. Productos guardados: {count}")
        if count == 0:
            st.warning("No se detectaron productos. Revisá selectores en services/store_selectors.py")
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
        st.info("Todavía no hay productos. Primero corré Sincronizar tienda.")
        return

    selected_category = st.selectbox("Filtrar por categoría", ["Todas"] + sorted({p.category for p in products}))
    selected_brand = st.selectbox("Filtrar por marca", ["Todas"] + sorted({p.brand for p in products}))

    for product in products:
        if selected_category != "Todas" and product.category != selected_category:
            continue
        if selected_brand != "Todas" and product.brand != selected_brand:
            continue
        with st.expander(f"{product.name} · {product.brand}"):
            st.write(f"**Categoría:** {product.category}")
            st.write(f"**Precio visible:** {product.price_text or '-'}")
            st.write(f"**Disponibilidad:** {product.availability_text or '-'}")
            st.write(f"**Variantes visibles:** {product.variants_text or '-'}")
            st.write(f"**Visual score:** {product.visual_score:.1f}")
            if product.description:
                st.write(product.description)
            st.link_button("Abrir producto", product.product_url)
            if product.image_url:
                st.image(product.image_url, width=220)


def render_manual_instagram_page(db: Database, uploads_path: Path) -> None:
    st.subheader("Instagram manual")

    with st.form("instagram_manual_form", clear_on_submit=True):
        title = st.text_input("Título o tema")
        caption = st.text_area("Caption")
        content_format = st.selectbox("Formato", ["reel", "post", "carousel", "story"])
        product_name = st.text_input("Producto involucrado")
        brand = st.text_input("Marca involucrada")
        category = st.text_input("Categoría involucrada")
        published_date = st.date_input("Fecha", value=date.today())
        image_upload = st.file_uploader("Captura opcional", type=["png", "jpg", "jpeg", "webp"])

        submitted = st.form_submit_button("Guardar post manual")

    if submitted:
        image_path = ""
        if image_upload:
            image_filename = f"ig_{int(date.today().strftime('%Y%m%d'))}_{image_upload.name}"
            save_path = uploads_path / image_filename
            save_path.write_bytes(image_upload.getvalue())
            image_path = str(save_path)

        db.save_manual_post(
            {
                "title": title,
                "caption": caption,
                "format": content_format,
                "product_name": product_name,
                "brand": brand,
                "category": category,
                "published_date": str(published_date),
                "image_path": image_path,
            }
        )
        st.success("Post manual guardado.")

    st.markdown("### Historial de posts manuales")
    for post in db.list_manual_posts():
        with st.container(border=True):
            st.write(f"**{post.title or 'Sin título'}** · {post.format} · {post.published_date}")
            st.write(post.caption)
            st.caption(f"Producto: {post.product_name or '-'} | Marca: {post.brand or '-'} | Categoría: {post.category or '-'}")
            if post.image_path and Path(post.image_path).exists():
                st.image(post.image_path, width=180)


def render_brand_manual_page(db: Database, brand_manual_path: Path) -> None:
    st.subheader("Manual de marca")

    upload = st.file_uploader("Subí manual (PDF/TXT)", type=["pdf", "txt"])
    pasted_text = st.text_area("O pegá texto del manual")

    c1, c2 = st.columns(2)
    if c1.button("Guardar archivo") and upload:
        path = brand_manual_path / upload.name
        path.write_bytes(upload.getvalue())
        parsed = BrandManualParser.parse_file(path)
        db.save_brand_manual("file", upload.name, parsed)
        st.success("Manual guardado desde archivo.")

    if c2.button("Guardar texto pegado") and pasted_text.strip():
        db.save_brand_manual("text", "manual_paste", pasted_text.strip())
        st.success("Manual guardado desde texto.")

    st.markdown("### Entradas guardadas")
    for entry in db.list_brand_manual_entries()[:10]:
        with st.expander(f"{entry.created_at.date()} · {entry.source_type} · {entry.source_name}"):
            st.write(entry.content[:4000])


def render_opportunities_page(db: Database) -> None:
    st.subheader("Oportunidades de contenido")

    products = db.list_products()
    manual_posts = db.list_manual_posts()

    if st.button("Analizar oportunidades", type="primary"):
        if not products:
            st.warning("No hay catálogo cargado. Primero sincronizá tienda.")
        else:
            opportunities = build_opportunities(products, manual_posts, limit=24)
            db.save_opportunities(opportunities)
            st.success(f"Se guardaron {len(opportunities)} oportunidades.")

    opportunities_saved = db.list_opportunities()
    if not opportunities_saved:
        st.info("Todavía no hay oportunidades generadas.")
        return

    for opp in opportunities_saved:
        product_name = opp.product.name if opp.product else "Sin producto"
        with st.expander(f"{product_name} · {opp.pillar} · score {opp.score:.1f}"):
            st.write(f"**Formato sugerido:** {opp.suggested_format}")
            st.write(f"**Motivo:** {opp.reason}")
            st.write(f"**Estado:** {opp.status}")


def render_prompt_generator_page(db: Database) -> None:
    st.subheader("Generador de prompts")

    opportunities = db.list_opportunities()
    if not opportunities:
        st.info("Primero generá oportunidades de contenido.")
        return

    options = {f"{opp.id} · {opp.product.name if opp.product else opp.title}": opp for opp in opportunities if opp.product}
    if not options:
        st.warning("No hay oportunidades con producto asociado.")
        return

    selected_label = st.selectbox("Elegí una oportunidad", list(options.keys()))
    selected = options[selected_label]

    manual_entries = db.list_brand_manual_entries()
    brand_manual_text = manual_entries[0].content if manual_entries else ""

    if st.button("Generar prompt pack", type="primary"):
        pack = build_prompt_pack(selected.product, selected, brand_manual_text)
        db.save_prompt_pack(
            selected.id,
            pack["prompt_spanish"],
            pack["prompt_image_product"],
            pack["prompt_image_kitchen"],
        )
        st.success("Prompt pack generado y guardado.")

    prompts = db.list_prompt_packs()
    for item in prompts[:20]:
        with st.expander(f"Prompt pack · oportunidad {item.opportunity_id} · {item.created_at.date()}"):
            st.text_area("Prompt para ChatGPT/Claude (ES)", value=item.prompt_spanish, height=220)
            st.code(item.prompt_image_product, language="text")
            st.code(item.prompt_image_kitchen, language="text")
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

    opportunities = db.list_opportunities()
    if not opportunities:
        st.info("Sin historial todavía.")
        return

    for opp in opportunities:
        product_name = opp.product.name if opp.product else opp.title
        cols = st.columns([3, 1])
        with cols[0]:
            st.write(f"**{product_name}** · {opp.suggested_format} · {opp.pillar}")
            st.caption(opp.reason)
        with cols[1]:
            new_status = st.selectbox(
                f"Estado #{opp.id}",
                ["draft", "used", "discarded"],
                index=["draft", "used", "discarded"].index(opp.status if opp.status in ["draft", "used", "discarded"] else "draft"),
                key=f"status_{opp.id}",
            )
            if st.button("Guardar", key=f"save_status_{opp.id}"):
                db.update_opportunity_status(opp.id, new_status)
                st.success("Estado actualizado")
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
