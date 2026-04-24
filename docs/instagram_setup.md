# Guía de conexión: Instagram Graph API

## Variables requeridas

- `INSTAGRAM_ACCESS_TOKEN`
- `INSTAGRAM_BUSINESS_ACCOUNT_ID`

## Precondiciones

- Cuenta de Instagram Business conectada a una página de Facebook.
- Token con permisos para lectura de media (según configuración de Meta).

## Pasos

1. Configurá una app en Meta for Developers.
2. Obtené token de acceso válido para Graph API.
3. Obtené el ID de cuenta Business de Instagram.
4. Guardá credenciales en `.env`.
5. Ejecutá **Sincronizar Instagram** dentro de la app.

## Datos que se guardan

- fecha del post
- caption
- tipo (post/reel/carousel)
- URL de imagen o thumbnail
- hashtags detectados
- métricas si están disponibles (likes/comments)

## Manejo de errores

Si faltan credenciales o falla la API, la app usa mock data para mantener el flujo de trabajo.
