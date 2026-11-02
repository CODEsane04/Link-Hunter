import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()


MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "link_hunter_db")

if not MONGODB_URL:
    raise ValueError("Missing MONGODB_URL in .env file")

#create the async mongoDb client
client = AsyncIOMotorClient(MONGODB_URL)

#get the db reference
db = client[DATABASE_NAME]

# define the collections

users_collection = db["users"]
history_collection = db["search_history"]

async def test_connection():
    try : 
        await client.admin.command('ping')
        print("sucessfully connected to mongoDB atlas")
    except Exception as e :
        print("mongodb connection error", e)

if __name__ == "__main__" :
    import asyncio
    asyncio.run(test_connection())