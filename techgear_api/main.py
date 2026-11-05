import os
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from db.database import get_database
from models.schemas import UserCreate, UserLogin, TokenResponse, UserResponse, ProductCreate, ProductUpdate, ProductResponse, OrderCreate, OrderResponse, OrderStatusUpdate
from bson import ObjectId

app = FastAPI(title="TechGear API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    try:
        db = get_database()
        await db.command("ping")
        print("--------------------------------------------------")
        print("🚀 ¡Conexión exitosa a MongoDB Atlas! Base de datos lista.")
        print("--------------------------------------------------")
    except Exception as e:
        print("--------------------------------------------------")
        print(f"❌ Error al conectar a MongoDB Atlas: {e}")
        print("--------------------------------------------------")

@app.get("/")
def root():
    return {"message": "Bienvenido a TechGear API - Clase 2"}


# --- SEGURIDAD (JWT) ---
SECRET_KEY = os.getenv("SECRET_KEY", "cambia-esto-en-render")
ALGORITHM = "HS256"
# Correos que obtienen rol admin (separados por coma). Ej: ADMIN_EMAILS=tu@correo.com
ADMIN_EMAILS = {e.strip().lower() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()}
TOKEN_EXPIRE_MINUTES = 60
bearer_scheme = HTTPBearer()

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return f"{salt}${digest}"

def verify_password(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split("$")
    except ValueError:
        return False
    check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return hmac.compare_digest(check, digest)

def create_access_token(user_id: str, email: str, rol: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "rol": rol,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    db = get_database()
    if not ObjectId.is_valid(payload.get("sub", "")):
        raise HTTPException(status_code=401, detail="Token inválido")
    user = await db["users"].find_one({"_id": ObjectId(payload["sub"])})
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user

async def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("rol") != "admin":
        raise HTTPException(status_code=403, detail="Se requiere rol administrador")
    return current_user

def user_to_response(u: dict) -> dict:
    return {"id": str(u["_id"]), "nombre": u["nombre"], "email": u["email"], "rol": u["rol"]}

def product_to_response(p: dict) -> dict:
    return {
        "id": str(p["_id"]),
        "nombre": p["nombre"],
        "descripcion": p["descripcion"],
        "precio": p["precio"],
        "stock": p["stock"],
        "categoria": p["categoria"],
        "imagen": p.get("imagen") or None,
    }

def order_to_response(o: dict) -> dict:
    return {
        "id": str(o["_id"]),
        "usuario_id": o["usuario_id"],
        "items": o.get("items", []),
        "total": o.get("total", 0),
        "fecha": o["fecha"],
        "estado": o.get("estado", "pendiente"),
        "imagen": o.get("imagen") or None,
    }

# --- AUTENTICACIÓN ---
@app.post("/auth/login", response_model=TokenResponse, tags=["Autenticación"])
async def login(credentials: UserLogin):
    db = get_database()
    user = await db["users"].find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user.get("password", "")):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    if user["email"].lower() in ADMIN_EMAILS and user.get("rol") != "admin":
        await db["users"].update_one({"_id": user["_id"]}, {"$set": {"rol": "admin"}})
        user["rol"] = "admin"
    token = create_access_token(str(user["_id"]), user["email"], user["rol"])
    return {"access_token": token, "token_type": "bearer"}

# --- USUARIOS ---
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Usuarios"])
async def create_user(user: UserCreate):
    db = get_database()
    if await db["users"].find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese correo")
    data = user.model_dump()
    data["password"] = hash_password(data["password"])
    # El rol lo decide el servidor: nadie puede registrarse como admin desde afuera
    data["rol"] = "admin" if user.email.lower() in ADMIN_EMAILS else "cliente"
    result = await db["users"].insert_one(data)
    created = await db["users"].find_one({"_id": result.inserted_id})
    return user_to_response(created)

@app.get("/users/me", response_model=UserResponse, tags=["Usuarios"])
async def get_me(current_user: dict = Depends(get_current_user)):
    return user_to_response(current_user)

@app.get("/users", response_model=list[UserResponse], tags=["Usuarios"])
async def list_users(admin: dict = Depends(require_admin)):
    db = get_database()
    users = []
    async for u in db["users"].find():
        users.append(user_to_response(u))
    return users

# --- PRODUCTOS (CRUD) ---
@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, tags=["Productos"])
async def create_product(product: ProductCreate, admin: dict = Depends(require_admin)):
    db = get_database()
    result = await db["products"].insert_one(product.model_dump())
    created = await db["products"].find_one({"_id": result.inserted_id})
    return product_to_response(created)

@app.get("/products", response_model=list[ProductResponse], tags=["Productos"])
async def get_products():
    db = get_database()
    products = []
    async for p in db["products"].find():
        products.append(product_to_response(p))
    return products

@app.get("/products/{id}", response_model=ProductResponse, tags=["Productos"])
async def get_product(id: str):
    db = get_database()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID no válido")
    p = await db["products"].find_one({"_id": ObjectId(id)})
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product_to_response(p)

@app.put("/products/{id}", response_model=ProductResponse, tags=["Productos"])
async def update_product(id: str, product_update: ProductUpdate, admin: dict = Depends(require_admin)):
    db = get_database()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID no válido")
    
    update_data = {k: v for k, v in product_update.model_dump().items() if v is not None}
    if update_data:
        await db["products"].update_one({"_id": ObjectId(id)}, {"$set": update_data})
    
    p = await db["products"].find_one({"_id": ObjectId(id)})
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product_to_response(p)

@app.delete("/products/{id}", tags=["Productos"])
async def delete_product(id: str, admin: dict = Depends(require_admin)):
    db = get_database()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID no válido")
    result = await db["products"].delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"message": "Producto eliminado exitosamente"}

# --- PEDIDOS ---
@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, tags=["Pedidos"])
async def create_order(order: OrderCreate, current_user: dict = Depends(get_current_user)):
    """Crea un pedido PENDIENTE para el usuario autenticado.
    Precio y nombre se toman del producto en la base de datos (no del cliente)."""
    db = get_database()
    items, total, imagen = [], 0.0, order.imagen or None
    for it in order.items:
        if not ObjectId.is_valid(it.product_id):
            raise HTTPException(status_code=400, detail="ID de producto no válido")
        p = await db["products"].find_one({"_id": ObjectId(it.product_id)})
        if not p:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        if p.get("stock", 0) < it.cantidad:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para «{p['nombre']}»")
        items.append({
            "product_id": it.product_id,
            "nombre": p["nombre"],
            "cantidad": it.cantidad,
            "precio_unitario": p["precio"],
        })
        total += it.cantidad * p["precio"]
        imagen = imagen or p.get("imagen") or None
    doc = {
        "usuario_id": str(current_user["_id"]),
        "items": items,
        "total": round(total, 2),
        "fecha": datetime.now(timezone.utc),
        "estado": "pendiente",
        "imagen": imagen,
    }
    result = await db["orders"].insert_one(doc)
    created = await db["orders"].find_one({"_id": result.inserted_id})
    return order_to_response(created)

@app.get("/orders/me", response_model=list[OrderResponse], tags=["Pedidos"])
async def get_my_orders(current_user: dict = Depends(get_current_user)):
    db = get_database()
    cursor = db["orders"].find({"usuario_id": str(current_user["_id"])}).sort("fecha", -1)
    return [order_to_response(o) async for o in cursor]

@app.get("/orders", response_model=list[OrderResponse], tags=["Pedidos"])
async def get_orders(admin: dict = Depends(require_admin)):
    db = get_database()
    cursor = db["orders"].find().sort("fecha", -1)
    return [order_to_response(o) async for o in cursor]

@app.patch("/orders/{id}/estado", response_model=OrderResponse, tags=["Pedidos"])
async def update_order_status(id: str, body: OrderStatusUpdate, current_user: dict = Depends(get_current_user)):
    """Confirma la compra o cancela un pedido pendiente (solo su dueño o un admin)."""
    db = get_database()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID no válido")
    o = await db["orders"].find_one({"_id": ObjectId(id)})
    es_dueno = o is not None and o["usuario_id"] == str(current_user["_id"])
    if not o or not (es_dueno or current_user.get("rol") == "admin"):
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if o.get("estado", "pendiente") != "pendiente":
        raise HTTPException(status_code=400, detail="Solo se pueden modificar pedidos pendientes")

    if body.estado == "comprado":
        # Descuenta stock de forma atomica; si algun item falla, revierte los anteriores
        descontados = []
        for it in o["items"]:
            if not ObjectId.is_valid(it.get("product_id", "")):
                raise HTTPException(status_code=400, detail="El pedido tiene un producto inválido")
            r = await db["products"].update_one(
                {"_id": ObjectId(it["product_id"]), "stock": {"$gte": it["cantidad"]}},
                {"$inc": {"stock": -it["cantidad"]}},
            )
            if r.modified_count == 0:
                for d in descontados:
                    await db["products"].update_one({"_id": ObjectId(d["product_id"])}, {"$inc": {"stock": d["cantidad"]}})
                nombre = it.get("nombre", "un producto")
                raise HTTPException(status_code=400, detail=f"Stock insuficiente para «{nombre}»")
            descontados.append(it)

    await db["orders"].update_one(
        {"_id": o["_id"]},
        {"$set": {"estado": body.estado, "fecha_estado": datetime.now(timezone.utc)}},
    )
    updated = await db["orders"].find_one({"_id": o["_id"]})
    return order_to_response(updated)
