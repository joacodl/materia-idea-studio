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
    elif page == "Historial":
        render_history_page(db)


def _authenticate(app_password: str) -> bool:
    st.title("Materia Content Studio")
    st.caption("Acceso privado")

    if not app_password:
        st.error("Falta configurar APP_PASSWORD en variables de entorno o en Secrets del deploy.")
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
