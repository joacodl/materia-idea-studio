# Guía de conexión: Tienda Nube API

## Variables requeridas

- `TIENDANUBE_ACCESS_TOKEN`
- `TIENDANUBE_STORE_ID`
- `TIENDANUBE_USER_AGENT` (recomendado)

## Pasos

1. Creá una app privada en Tienda Nube desde tu panel de desarrolladores.
2. Copiá el `access token` y el `store id`.
3. Pegá ambos en `.env`.
4. En la app, abrí **Sincronización** y hacé clic en **Sincronizar catálogo**.

## Datos que se guardan

- nombre, descripción, marca, categoría
- variantes, precios, stock
- URL de producto
- imágenes
- fecha de creación/actualización

## Manejo de errores

Si falta credencial o la API no responde, la app pasa a datos mock para pruebas.
