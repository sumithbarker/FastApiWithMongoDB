from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId

from app.database import user_collection
from app.auth import hash_password
from app.dependencies import require_role

router = APIRouter()

# 1️⃣ Create Admin (Admin-only)
@router.post("/register")
async def create_admin(
    email: str,
    password: str,
    admin=Depends(require_role("admin"))
):
    existing_user = await user_collection.find_one({"email": email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    await user_collection.insert_one({
        "email": email,
        "hashed_password": hash_password(password),
        "role": "admin",
        "is_active": True
    })

    return {"message": "Admin created successfully"}


# 2️⃣ List All Users (Admin-only)
@router.get("/users")
async def list_users(admin=Depends(require_role("admin"))):
    users = []

    async for user in user_collection.find():
        users.append({
            "id": str(user["_id"]),
            "email": user["email"],
            "role": user["role"],
            "is_active": user["is_active"]
        })

    return users


# 3️⃣ Deactivate User (Admin-only)
@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    admin=Depends(require_role("admin"))
):
    result = await user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": False}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deactivated"}


# 4️⃣ Activate User (Admin-only)
@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    admin=Depends(require_role("admin"))
):
    result = await user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": True}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User activated"}