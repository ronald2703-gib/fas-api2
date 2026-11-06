
⚡ TechGear

🛒 Tienda web de tecnología con catálogo, pedidos y panel de administración

Mostrar imagen Mostrar imagen Mostrar imagen Mostrar imagen Mostrar imagen

Mostrar imagen Mostrar imagen Mostrar imagen

🌐 Ver la tienda en vivo · 📖 Documentación de la API · 💻 Código


📑 Contenido
📝 Descripción
🚀 App desplegada
✨ Funcionalidades
🏗️ Arquitectura
🧰 Tecnologías y librerías
📁 Estructura del proyecto
⚙️ Instalación y ejecución
🔌 Endpoints de la API
🛡️ Manejo de excepciones
☁️ Despliegue
👨‍💻 Autor
📝 Descripción

TechGear es una tienda de tecnología dividida en dos partes que se comunican entre sí:

🔧 una API REST hecha con FastAPI y MongoDB, que guarda usuarios, productos y pedidos;
🎨 un frontend hecho con Django, que consume la API y ofrece la tienda y el panel de administración.

Cada persona ve algo distinto según su rol: visitante, cliente o administrador.

🚀 App desplegada
🧩 Parte	🔗 Enlace
🌐 Frontend (Vercel)	https://fas-api2.vercel.app/
⚙️ API (Render)	https://fas-api2.onrender.com
📖 Swagger / documentación	https://fas-api2.onrender.com/docs
💻 Repositorio (GitHub)	https://github.com/ronald2703-gib/fas-api2

⏳ Ojo: la API está en el plan gratuito de Render. Si lleva un rato sin uso, la primera petición puede tardar hasta un minuto en despertar.

✨ Funcionalidades
👤 Rol	🎯 Qué puede hacer
🙋 Visitante	Ver el catálogo 🔎, buscar y filtrar por categoría. Al pulsar Comprar 🛍️ lo lleva al login y, al entrar, vuelve al catálogo.
🛒 Cliente	Guardar productos como pedidos pendientes en Mis pedidos 📦, confirmar la compra ✅ (descuenta stock) o cancelar ❌. Cada pedido muestra la imagen del producto 🖼️.
🛠️ Administrador	Dashboard 📊 con estadísticas y CRUD de productos (crear, editar, eliminar) con imagen por archivo o URL.

🔐 Nadie puede registrarse como admin desde el formulario: el rol lo asigna la API según la variable ADMIN_EMAILS.

🏗️ Arquitectura
HTTP + JWT
👤 Usuario
🎨 Frontend DjangoVercel
⚙️ API FastAPIRender
🍃 MongoDB Atlas
🧰 Tecnologías y librerías
<details open> <summary><b>⚙️ API — <code>techgear_api</code></b></summary>
🐍 Python 3 y FastAPI con Uvicorn
🍃 MongoDB (Atlas) con Motor (driver asíncrono)
✅ Pydantic y pydantic-settings (validación), email-validator
🔑 PyJWT (autenticación con tokens JWT) y python-dotenv
</details> <details open> <summary><b>🎨 Frontend — <code>techgear_web</code></b></summary>
🟩 Django (plantillas, vistas, mensajes y sesión en cookie firmada, sin base de datos propia)
🌐 Requests (consumo de la API), python-dotenv, tzdata
💅 Bootstrap 5 y Bootstrap Icons (CDN) más CSS propio
</details> <details open> <summary><b>☁️ Despliegue</b></summary>
▲ Vercel → frontend
🟢 Render → API
🐙 GitHub → código y releases
</details>
📁 Estructura del proyecto
techgear/
├── 📂 techgear_api/              # ⚙️ API FastAPI
│   ├── main.py                   # Endpoints: usuarios, productos, pedidos
│   ├── models/schemas.py         # Modelos Pydantic y validaciones
│   ├── db/database.py            # Conexión a MongoDB
│   └── requirements.txt
├── 📂 techgear_web/              # 🎨 Frontend Django
│   ├── techgear_web/             # settings, urls, wsgi
│   ├── store/
│   │   ├── views.py              # Catálogo, login, dashboard, compras
│   │   ├── urls.py
│   │   ├── templates/store/      # Plantillas HTML
│   │   └── static/store/         # CSS e imágenes
│   ├── requirements.txt
│   ├── vercel.json
│   └── .env.example
└── 📄 README.md
⚙️ Instalación y ejecución en local

📋 Requisitos: Python 3.12+, una base de datos MongoDB (por ejemplo Atlas) y Git.

Autor🗽

--Ronald fernando luna vidarte--
-proyecto-- ⚡ TechGear
--ficha--: 3494620
--desarrollador--
     ✌️😎

