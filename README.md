# Materia Content Studio

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
