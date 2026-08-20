import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

client = AsyncIOMotorClient(MONGO_URL)
database = client[MONGO_DB_NAME]

# Colecciones
productos_collection = database.get_collection("productos")
pedidos_collection = database.get_collection("pedidos")

async def test_connection():
    try:
        await client.admin.command('ping')
        print("¡Conexión exitosa a MongoDB Atlas!")
    except Exception as e:
        print(f"Error conectando a MongoDB: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())