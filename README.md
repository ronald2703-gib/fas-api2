```
 ████████╗███████╗ ██████╗██╗  ██╗ ██████╗ ███████╗ █████╗ ██████╗
 ╚══██╔══╝██╔════╝██╔════╝██║  ██║██╔════╝ ██╔════╝██╔══██╗██╔══██╗
    ██║   █████╗  ██║     ███████║██║  ███╗█████╗  ███████║██████╔╝
    ██║   ██╔══╝  ██║     ██╔══██║██║   ██║██╔══╝  ██╔══██║██╔══██╗
    ██║   ███████╗╚██████╗██║  ██║╚██████╔╝███████╗██║  ██║██║  ██║
    ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
```
 
# ⚡ TechGear
 
### 🛒 Tienda web de tecnología con catálogo, pedidos y panel de administración
 
> 🚀 **Release v1.0** · 🐍 Python · ⚙️ FastAPI · 🟩 Django · 🍃 MongoDB · ▲ Vercel · 🟢 Render
 
👉 **[🌐 Ver la tienda en vivo](https://fas-api2.vercel.app/)** · **[📖 Documentación de la API](https://fas-api2.onrender.com/docs)** · **[💻 Código en GitHub](https://github.com/ronald2703-gib/fas-api2)**
 
---
 
## 📝 Descripción
 
**TechGear** es una tienda de tecnología dividida en dos partes que se hablan entre sí:
 
- 🔧 Una **API REST** hecha con **FastAPI** y **MongoDB**, que guarda usuarios, productos y pedidos.
- 🎨 Un **frontend** hecho con **Django**, que consume la API y ofrece la tienda y el panel de administración.
Cada persona ve algo distinto según su rol: **visitante**, **cliente** o **administrador**. 🎭
 
---
 
## 🚀 App desplegada
 
| 🧩 Parte | 🔗 Enlace |
|---|---|
| 🌐 Frontend (Vercel) | https://fas-api2.vercel.app/ |
| ⚙️ API (Render) | https://fas-api2.onrender.com |
| 📖 Swagger / documentación | https://fas-api2.onrender.com/docs |
| 💻 Repositorio (GitHub) | https://github.com/ronald2703-gib/fas-api2 |
 
> ⏳ **Ojo:** la API está en el plan gratuito de Render. Si lleva un rato sin uso, la primera petición puede tardar hasta un minuto en despertar. ¡Paciencia! 😴➡️😎
 
---
 
## ✨ Funcionalidades
 
| 👤 Rol | 🎯 Qué puede hacer |
|---|---|
| 🙋 **Visitante** | Ver el catálogo 🔎, buscar y filtrar por categoría. Al pulsar **Comprar** 🛍️ lo lleva al login y, al entrar, vuelve al catálogo. |
| 🛒 **Cliente** | Guardar productos como pedidos *pendientes* en **Mis pedidos** 📦, **confirmar la compra** ✅ (descuenta stock) o **cancelar** ❌. Cada pedido muestra la imagen del producto 🖼️. |
| 🛠️ **Administrador** | Dashboard 📊 con estadísticas y CRUD de productos (crear ➕, editar ✏️, eliminar 🗑️) con imagen por archivo o URL. |
 
> 🔐 Nadie puede registrarse como admin desde el formulario: el rol lo asigna la API según la variable `ADMIN_EMAILS`.
 
---
 
## 🏗️ Arquitectura
 
```
   👤 Usuario
       │
       ▼
┌─────────────────────┐        HTTP + JWT        ┌─────────────────────┐        ┌──────────────────┐
│ 🎨 Frontend Django  │ ───────────────────────► │ ⚙️  API FastAPI     │ ─────► │ 🍃 MongoDB Atlas │
│     (Vercel)        │ ◄─────────────────────── │     (Render)        │ ◄───── │                  │
└─────────────────────┘                          └─────────────────────┘        └──────────────────┘
```
 
---
 
## 🧰 Tecnologías y librerías
 
### ⚙️ API (`techgear_api`)
- 🐍 **Python 3** y **FastAPI** con **Uvicorn**
- 🍃 **MongoDB** (Atlas) con **Motor** (driver asíncrono)
- ✅ **Pydantic** y pydantic-settings (validación) y **email-validator**
- 🔑 **PyJWT** (tokens JWT) y **python-dotenv**
### 🎨 Frontend (`techgear_web`)
- 🟩 **Django** (plantillas, vistas, mensajes y sesión en cookie firmada, sin base de datos propia)
- 🌐 **Requests** (consumo de la API), **python-dotenv** y **tzdata**
- 💅 **Bootstrap 5**, **Bootstrap Icons** (CDN) y CSS propio
### ☁️ Despliegue
- ▲ **Vercel** → frontend
- 🟢 **Render** → API
- 🐙 **GitHub** → código y releases
---
 
## 📁 Estructura del proyecto
 
```
techgear/
├── 📂 techgear_api/              ⚙️ API FastAPI
│   ├── main.py                   Endpoints: usuarios, productos, pedidos
│   ├── models/schemas.py         Modelos Pydantic y validaciones
│   ├── db/database.py            Conexión a MongoDB
│   └── requirements.txt
├── 📂 techgear_web/              🎨 Frontend Django
│   ├── techgear_web/             settings, urls, wsgi
│   ├── store/
│   │   ├── views.py              Catálogo, login, dashboard, compras
│   │   ├── urls.py
│   │   ├── templates/store/      Plantillas HTML
│   │   └── static/store/         CSS e imágenes
│   ├── requirements.txt
│   ├── vercel.json
│   └── .env.example
└── 📄 README.md
```
 
---
 
## ⚙️ Instalación y ejecución en local
 
📋 **Requisitos:** Python 3.12+, una base de datos MongoDB (por ejemplo Atlas) y Git.
 
```bash
git clone https://github.com/ronald2703-gib/fas-api2.git
cd fas-api2
```
 
### 1️⃣ API (puerto 8000)
 
```bash
cd techgear_api
python -m venv venv
venv\Scripts\activate          # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```
 
Crea el archivo `techgear_api/.env`:
 
```env
MONGO_URI=mongodb+srv://usuario:clave@cluster.mongodb.net/?appName=Cluster0
SECRET_KEY=un-texto-largo-y-aleatorio
ADMIN_EMAILS=tucorreo@gmail.com
```
 
```bash
uvicorn main:app --reload
```
 
📖 Documentación en http://127.0.0.1:8000/docs
 
### 2️⃣ Frontend (puerto 8001) — en otra terminal
 
```bash
cd techgear_web
pip install -r requirements.txt
```
 
Copia `.env.example` a `.env`:
 
```env
API_URL=http://127.0.0.1:8000
DEBUG=True
```
 
```bash
python manage.py runserver 8001
```
 
🌐 Abre http://127.0.0.1:8001
 
🧭 **Rutas del frontend:** `/` catálogo · `/login/` · `/register/` · `/logout/` · `/mis-pedidos/` (cliente) · `/dashboard/` (admin)
 
---
 
## 🔌 Endpoints de la API
 
| Método | Ruta | 🔒 Acceso |
|---|---|---|
| `POST` | `/users`, `/auth/login` | 🌍 Público |
| `GET` | `/users/me` | 🔑 Autenticado |
| `GET` | `/users` | 🛠️ Admin |
| `GET` | `/products`, `/products/{id}` | 🌍 Público |
| `POST` `PUT` `DELETE` | `/products` | 🛠️ Admin |
| `POST` | `/orders` | 🔑 Autenticado |
| `GET` | `/orders/me` | 🔑 Sus propios pedidos |
| `PATCH` | `/orders/{id}/estado` | 🔑 Dueño del pedido o admin |
| `GET` | `/orders` | 🛠️ Admin |
 
---
 
## 🛡️ Manejo de excepciones
 
| ⚠️ Situación | ✅ Qué hace la app |
|---|---|
| 📡 **API caída o dormida** | Muestra un aviso en el catálogo, login, dashboard y Mis pedidos, en vez de una página de error. |
| 📦 **Producto sin stock** | El catálogo muestra **Agotado**; la API rechaza pedidos o confirmaciones sin stock suficiente y el usuario ve el mensaje. |
| 🔄 **Confirmación de compra** | Descuenta el stock de forma atómica y revierte si algún producto falla. |
| ⏰ **Sesión vencida (401)** | Cierra la sesión y redirige al login. |
| 🔐 **Seguridad** | La API toma el precio y el usuario del pedido (base de datos y token), no del cliente; las rutas de admin exigen rol `admin`; el parámetro `next` del login solo acepta rutas del mismo sitio. |
 
---
 
## 🔎 SEO y accesibilidad
 
- 🏷️ Título y **meta descripción** propios en cada página, etiqueta `canonical` y `robots.txt`.
- 🙈 Las páginas privadas (login, dashboard, pedidos) llevan `noindex`.
- ♿ Campos con etiqueta, encabezados en orden, textos alternativos en imágenes, contraste de colores AA y enlace "Saltar al contenido".
- ⚡ Fuentes y scripts sin bloquear la carga, y archivos estáticos con caché de un año.
---
 
## ☁️ Despliegue
 
### ⚙️ API en Render
Servicio web conectado al repositorio (carpeta `techgear_api`) con las variables de entorno `MONGO_URI`, `SECRET_KEY` y `ADMIN_EMAILS`.
 
### 🎨 Frontend en Vercel
Importar el repositorio con **Root Directory** `techgear_web` (Vercel detecta Django solo) y definir:
 
- `SECRET_KEY` → `python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"`
- `API_URL` → `https://fas-api2.onrender.com`
🔁 Cada `git push` a `main` redespliega ambos servicios automáticamente.
 
---
 
## 🗽 Autor
 
| 📌 Dato | 💬 Información |
|---|---|
| 👤 **Autor** | Ronald Fernando Luna Vidarte |
| 🚀 **Proyecto** | ⚡ TechGear |
| 🪪 **Ficha** | 3494620 |
| 💻 **Desarrollador** | ✌️😎 |
| 🐙 **GitHub** | [@ronald2703-gib](https://github.com/ronald2703-gib) |
 
---
 
<p align="center">⭐ Hecho con ❤️ y mucho café ☕ · <b>TechGear v1.0</b> ⭐</p>
 
