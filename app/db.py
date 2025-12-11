from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

client = AsyncIOMotorClient(settings.MONGODB_URI)
master_db = client[settings.MASTER_DB]
# Note: dynamic org collections created under another DB or same DB as needed.
# For simplicity this example creates org collections under the same Mongo server, same DB 'tenant_data'.
tenant_db = client["tenant_data"]
