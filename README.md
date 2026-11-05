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
# opcional .env (ver .env.example): API_URL=http://127.0.0.1:8000
python manage.py runserver 8001   # ya no hace falta "migrate": no usa base de datos propia
```
Rutas: `/` catálogo, `/login/`, `/register/`, `/logout/`, `/mis-pedidos/` (cliente), `/dashboard/` (admin).
En Render define la variable `SECRET_KEY` de la API.

## Clase 5 – Dashboard CRUD (rol admin)
- `/dashboard/` lista los productos con estadísticas; solo accesible con rol `admin`.
- Crear (`POST /products`), editar (`PUT /products/{id}`) y eliminar (`DELETE /products/{id}`) llaman a la API FastAPI con el JWT guardado en la sesión.
- La API protege esas rutas con `require_admin`; `GET /products` sigue siendo público.
- El rol admin lo define el servidor con la variable `ADMIN_EMAILS` (en `techgear_api/.env` y en Render). Nadie puede registrarse como admin desde el formulario.



## Compras y pedidos (cliente)
- Sin sesión, el catálogo es público y el botón **Comprar** lleva a `/login/` (y vuelve al catálogo al entrar).
- Con sesión de cliente, **Comprar** guarda el producto como pedido *pendiente* en `/mis-pedidos/`, donde se puede **confirmar la compra** (descuenta stock) o **cancelar**.
- Cada pedido lleva una imagen (por defecto la del producto). El admin sube la imagen del producto en el formulario (archivo o URL).
- La API toma precio y nombre del producto en la base de datos y el usuario del token JWT: el cliente no puede falsearlos.
- Endpoints: `POST /orders`, `GET /orders/me`, `PATCH /orders/{id}/estado`, `GET /orders` (solo admin).

## Despliegue del front en Vercel
1. Subir el repo a GitHub y en Vercel: **Add New → Project** → importar el repo.
2. **Root Directory:** `techgear_web` (Vercel detecta Django por `manage.py`; no requiere más configuración).
3. **Environment Variables:**
   - `SECRET_KEY` → clave nueva (`python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"`)
   - `API_URL` → `https://fas-api2.onrender.com`
4. Deploy. Cada `git push` a `main` vuelve a desplegar.
5. La API sigue en Render: tras cambiar `techgear_api/`, Render se redepliega con el push.
