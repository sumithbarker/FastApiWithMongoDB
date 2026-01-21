from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://localhost:27017"

client = AsyncIOMotorClient(MONGO_URL)
db = client.task_db
task_collection = db.tasks
user_collection = db.users
blacklist_collection = db.token_blacklist  
otp_collection = db.otp_requests            