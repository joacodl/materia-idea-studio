# Materia Content Studio

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

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=src streamlit run app.py
```

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
