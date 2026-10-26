from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from db.database import get_database
from models.schemas import UserCreate, UserResponse, ProductCreate, ProductUpdate, ProductResponse, OrderCreate, OrderResponse
from bson import ObjectId
from datetime import datetime

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

# --- USUARIOS ---
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Usuarios"])
async def create_user(user: UserCreate):
    db = get_database()
    result = await db["users"].insert_one(user.model_dump())
    created = await db["users"].find_one({"_id": result.inserted_id})
    return {
        "id": str(created["_id"]),
        "nombre": created["nombre"],
        "email": created["email"],
        "rol": created["rol"]
    }

# --- PRODUCTOS (CRUD) ---
@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, tags=["Productos"])
async def create_product(product: ProductCreate):
    db = get_database()
    result = await db["products"].insert_one(product.model_dump())
    created = await db["products"].find_one({"_id": result.inserted_id})
    return {
        "id": str(created["_id"]),
        "nombre": created["nombre"],
        "descripcion": created["descripcion"],
        "precio": created["precio"],
        "stock": created["stock"],
        "categoria": created["categoria"]
    }

@app.get("/products", response_model=list[ProductResponse], tags=["Productos"])
async def get_products():
    db = get_database()
    products = []
    async for p in db["products"].find():
        products.append({
            "id": str(p["_id"]),
            "nombre": p["nombre"],
            "descripcion": p["descripcion"],
            "precio": p["precio"],
            "stock": p["stock"],
            "categoria": p["categoria"]
        })
    return products

@app.get("/products/{id}", response_model=ProductResponse, tags=["Productos"])
async def get_product(id: str):
    db = get_database()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID no válido")
    p = await db["products"].find_one({"_id": ObjectId(id)})
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {
        "id": str(p["_id"]),
        "nombre": p["nombre"],
        "descripcion": p["descripcion"],
        "precio": p["precio"],
        "stock": p["stock"],
        "categoria": p["categoria"]
    }

@app.put("/products/{id}", response_model=ProductResponse, tags=["Productos"])
async def update_product(id: str, product_update: ProductUpdate):
    db = get_database()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID no válido")
    
    update_data = {k: v for k, v in product_update.model_dump().items() if v is not None}
    if update_data:
        await db["products"].update_one({"_id": ObjectId(id)}, {"$set": update_data})
    
    p = await db["products"].find_one({"_id": ObjectId(id)})
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {
        "id": str(p["_id"]),
        "nombre": p["nombre"],
        "descripcion": p["descripcion"],
        "precio": p["precio"],
        "stock": p["stock"],
        "categoria": p["categoria"]
    }

@app.delete("/products/{id}", tags=["Productos"])
async def delete_product(id: str):
    db = get_database()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID no válido")
    result = await db["products"].delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"message": "Producto eliminado exitosamente"}

# --- PEDIDOS ---
@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, tags=["Pedidos"])
async def create_order(order: OrderCreate):
    db = get_database()
    total = sum(item.cantidad * item.precio_unitario for item in order.items)
    order_dict = order.model_dump()
    order_dict["total"] = total
    order_dict["fecha"] = datetime.now()
    
    result = await db["orders"].insert_one(order_dict)
    created = await db["orders"].find_one({"_id": result.inserted_id})
    return {
        "id": str(created["_id"]),
        "usuario_id": created["usuario_id"],
        "items": created["items"],
        "total": created["total"],
        "fecha": created["fecha"]
    }

@app.get("/orders", response_model=list[OrderResponse], tags=["Pedidos"])
async def get_orders():
    db = get_database()
    orders = []
    async for o in db["orders"].find():
        orders.append({
            "id": str(o["_id"]),
            "usuario_id": o["usuario_id"],
            "items": o["items"],
            "total": o["total"],
            "fecha": o["fecha"]
        })
    return orders