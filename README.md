# Materia Content Studio

App privada en Streamlit para organizar contenido de Instagram **sin usar APIs externas**.

## Qué hace

1. Hace scraping público de `https://www.materiainsumos.com.ar`.
2. Guarda catálogo en SQLite (productos, precio visible, imagen, categoría, marca, variantes, disponibilidad).
3. Permite cargar posts de Instagram manualmente.
4. Permite cargar manual de marca por texto o PDF/TXT.
5. Analiza oportunidades con reglas locales (sin OpenAI/Anthropic).
6. Genera prompt packs listos para copiar y pegar:
   - Prompt en español para ChatGPT/Claude (manual)
   - Prompt en inglés para imagen de producto
   - Prompt en inglés para escena de cocina/proceso

---

## Variables de entorno

Usar solo estas variables:

- `APP_PASSWORD=`
- `STORE_BASE_URL=https://www.materiainsumos.com.ar`

No se requieren API keys.

---

## Uso local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=src streamlit run app.py
```

La base SQLite se crea automáticamente al abrir la app.

---

## Despliegue en Streamlit Community Cloud (recomendado)

1. Subí el repo a GitHub.
2. Entrá a https://share.streamlit.io y hacé clic en **New app**.
3. Seleccioná:
   - Repository: tu repo
   - Branch: `main`
   - Main file path: `app.py`
4. En **Advanced settings > Secrets** cargá:

```toml
APP_PASSWORD="tu_clave_privada"
STORE_BASE_URL="https://www.materiainsumos.com.ar"
```

5. Deploy.

Resultado esperado: abrís URL privada, ingresás contraseña, sincronizás tienda, cargás posts/manual y generás oportunidades + prompt packs.

---

## Páginas incluidas

- Inicio
- Sincronizar tienda
- Catálogo
- Instagram manual
- Manual de marca
- Oportunidades de contenido
- Generador de prompts
- Historial

---

## Arquitectura

- `src/materia_content_studio/app.py`: interfaz Streamlit y flujo completo
- `src/materia_content_studio/db.py`: modelos y persistencia SQLite
- `src/materia_content_studio/services/store_scraper.py`: scraping público con rate limiting + retries
- `src/materia_content_studio/services/store_selectors.py`: selectores modulares
- `src/materia_content_studio/services/opportunity_engine.py`: reglas de oportunidad
- `src/materia_content_studio/services/prompt_builder.py`: plantillas de prompts

---

## Aviso de scraping responsable

- Solo páginas públicas
- Sin bypass de protección anti-bot
- Con pausas entre requests y reintentos controlados
