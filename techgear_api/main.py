from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database import get_database

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
    return {"message": "Bienvenido a TechGear API - Clase 1"}

@app.get("/test-db")
async def test_db():
    try:
        db = get_database()
        await db.command("ping")
        return {"status": "success", "message": "¡Conexión exitosa a MongoDB Atlas! 🚀"}
    except Exception as e:
        return {"status": "error", "message": f"No se pudo conectar a la base de datos: {str(e)}"}