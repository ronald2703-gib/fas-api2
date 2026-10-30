# TechGear Web (Django MVT)

Frontend y panel administrativo construido con Django para consumir la API de FastAPI.
https://fas-api2.onrender.com

## Ejecutar en local
```bash
# API (puerto 8000)
cd techgear_api && pip install -r requirements.txt
# .env: MONGO_URI=...  SECRET_KEY=...
uvicorn main:app --reload

# Frontend Django (puerto 8001)
cd techgear_web && pip install -r requirements.txt
# opcional .env: API_URL=http://127.0.0.1:8000
python manage.py migrate
python manage.py runserver 8001
```
Rutas: `/` catálogo, `/login/`, `/register/`, `/logout/`.
En Render define la variable `SECRET_KEY` de la API.

## Clase 5 – Dashboard CRUD (rol admin)
- `/dashboard/` lista los productos con estadísticas; solo accesible con rol `admin`.
- Crear (`POST /products`), editar (`PUT /products/{id}`) y eliminar (`DELETE /products/{id}`) llaman a la API FastAPI con el JWT guardado en la sesión.
- La API protege esas rutas con `require_admin`; `GET /products` sigue siendo público.
- El rol admin lo define el servidor con la variable `ADMIN_EMAILS` (en `techgear_api/.env` y en Render). Nadie puede registrarse como admin desde el formulario.

