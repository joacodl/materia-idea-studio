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
Aplicación privada (Streamlit) para crear ideas editoriales de Instagram usando:

- Catálogo de Tienda Nube
- Publicaciones recientes de Instagram
- Manual de marca (PDF/TXT)

La interfaz y los textos generados están pensados para español rioplatense. Los prompts de imagen se generan en inglés.

---

## Qué vas a lograr

Abrís una URL privada → ingresás contraseña → sincronizás catálogo + Instagram → generás ideas listas para publicar.

---

## 1) Variables de entorno (obligatorias y opcionales)

Copiá `.env.example` a `.env` y completá:

### Obligatorias

- `APP_PASSWORD` (contraseña para entrar a la app)

### Para conectores reales

- `TIENDANUBE_ACCESS_TOKEN`
- `TIENDANUBE_STORE_ID`
- `INSTAGRAM_ACCESS_TOKEN`
- `INSTAGRAM_BUSINESS_ACCOUNT_ID`

### Para generación con IA

- `OPENAI_API_KEY` (recomendado)

### Opcionales

- `OPENAI_MODEL`
- `ANTHROPIC_API_KEY`
- `ANTHROPIC_MODEL`
- `AUTO_SYNC_ON_STARTUP`
- `DATABASE_PATH`

> Si faltan credenciales de APIs, la app usa mock data y sigue funcionando para pruebas.

---

## 2) Uso local (rápido)
Aplicación interna construida con Streamlit para generar ideas editoriales de Instagram usando datos reales de:

- Tienda Nube (catálogo + imágenes)
- Instagram Graph API (posts recientes)
- Manual de marca (PDF/TXT)

> Toda la interfaz está en español y las ideas se generan en español rioplatense con voseo. Los prompts de imagen se generan en inglés.

## 1) Requisitos

- Python 3.11+
- Variables de entorno en `.env`

## 2) Instalación

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
No hace falta crear la base manualmente: la app crea SQLite automáticamente al iniciar.

---

## 3) Despliegue en Streamlit Community Cloud (recomendado)

### Paso a paso (no técnico)

1. Subí este proyecto a un repositorio de GitHub.
2. Entrá a [https://share.streamlit.io](https://share.streamlit.io) con tu cuenta.
3. Hacé clic en **New app**.
4. Elegí:
   - **Repository**: tu repo
   - **Branch**: `main` (o la rama que uses)
   - **Main file path**: `app.py`
5. Abrí **Advanced settings** → **Secrets** y pegá tus variables, por ejemplo:

```toml
APP_PASSWORD="tu_clave_privada"
TIENDANUBE_ACCESS_TOKEN="..."
TIENDANUBE_STORE_ID="..."
INSTAGRAM_ACCESS_TOKEN="..."
INSTAGRAM_BUSINESS_ACCOUNT_ID="..."
OPENAI_API_KEY="..."
AUTO_SYNC_ON_STARTUP="false"
DATABASE_PATH="data/materia_content_studio.db"
```

6. Hacé clic en **Deploy**.
7. Cuando abra la URL, te va a pedir contraseña. Sin contraseña correcta no muestra la app.

### Notas importantes para Streamlit Cloud

- No hardcodees secretos en el código.
- Usá siempre **Secrets** del panel.
- La base SQLite se crea sola al arrancar; no requiere comandos post-deploy.
- El storage en cloud puede ser efímero según plataforma/plan.

---

## 4) Despliegue en Render o Railway (alternativas)

Si preferís Render/Railway:

1. Conectá el repo de GitHub.
2. Configurá comando de start:
   - `PYTHONPATH=src streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
3. Cargá las mismas variables de entorno (`APP_PASSWORD`, tokens, keys).
4. Deploy.

La app también va a crear SQLite automáticamente al iniciar.

---

## 5) Seguridad de acceso

- La app exige `APP_PASSWORD` para abrir.
- Si la contraseña es incorrecta, no se accede al contenido.
- Si es correcta, se guarda sesión (`st.session_state`) y habilita navegación.

---
```

## 3) Variables de entorno

Completá al menos las credenciales que vayas a usar:

- `TIENDANUBE_ACCESS_TOKEN`
- `TIENDANUBE_STORE_ID`
- `INSTAGRAM_ACCESS_TOKEN`
- `INSTAGRAM_BUSINESS_ACCOUNT_ID`
- `OPENAI_API_KEY` o `ANTHROPIC_API_KEY`

Si faltan credenciales, la app usa mock data para que puedas probar el flujo completo.

## 4) Inicializar base de datos local

```bash
PYTHONPATH=src python scripts/init_db.py
```

## 5) Ejecutar

```bash
PYTHONPATH=src streamlit run app.py
```

## 6) Estructura del proyecto

```text
.
├── app.py
├── .env.example
├── requirements.txt
├── scripts/
│   └── init_db.py
├── docs/
│   ├── tiendanube_setup.md
│   └── instagram_setup.md
├── data/
├── docs/
│   ├── instagram_setup.md
│   └── tiendanube_setup.md
├── scripts/
│   └── init_db.py
├── requirements.txt
├── .env.example
└── src/materia_content_studio/
    ├── app.py
    ├── config.py
    ├── db.py
    └── services/
```

---

## 7) Flujo recomendado dentro de la app

1. Ingresar contraseña.
2. Ir a **Configuración** y subir manual de marca.
3. Ir a **Sincronización** y correr:
   - **Sincronizar catálogo**
   - **Sincronizar Instagram**
4. Ir a **Generador de ideas** y generar plan semanal.
5. Revisar en **Historial**.
        ├── brand_manual.py
        ├── idea_generator.py
        ├── instagram.py
        ├── mock_data.py
        ├── repetition.py
        └── tiendanube.py
```

## 7) Flujo recomendado

1. Ir a **Configuración** y subir manual de marca.
2. Ir a **Sincronización** y ejecutar:
   - `Sincronizar catálogo`
   - `Sincronizar Instagram`
3. Ir a **Generador de ideas** y hacer clic en `Generar ideas para esta semana`.
4. Revisar ideas en **Historial** y cambiar estado (draft/used/discarded, vía SQLite o extensión futura).

## 8) Base de datos SQLite

- Ruta por defecto: `data/materia_content_studio.db` (se crea localmente con `scripts/init_db.py`).
- Tablas:
  - `products`
  - `product_images`
  - `instagram_posts`
  - `generated_ideas`
  - `sync_logs`

## 9) Calidad de salida

El motor de ideas incorpora:

- contexto de catálogo real
- análisis de publicaciones recientes
- capa de repetición (productos/marcas/categorías)
- validación de tono por manual (si está cargado)

## 10) Notas de implementación

- El conector de Tienda Nube usa API REST con paginación.
- El conector de Instagram usa Graph API para media reciente.
- Si la API falla o faltan credenciales, se usa mock data para no frenar operación interna.
