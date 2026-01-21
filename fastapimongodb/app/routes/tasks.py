from fastapi import APIRouter
from datetime import datetime
from app.database import task_collection
from app.schemas import TaskCreate
from fastapi import Depends
from app.dependencies import oauth2_scheme
from app.database import blacklist_collection
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/tasks")
async def create_task(
    title: str,
    description: str,
    user_id: str = Depends(get_current_user)
):
    task = {
        "title": title,
        "description": description,
        "status": "pending",
        "owner": user_id,
        "created_at": datetime.utcnow()
    }
    result = await task_collection.insert_one(task)
    return {"id": str(result.inserted_id)}

@router.get("/tasks")
async def get_tasks(user_id: str = Depends(get_current_user)):
    tasks = []
    async for task in task_collection.find({"owner": user_id}):
        task["_id"] = str(task["_id"])
        tasks.append(task)
    return tasks

@router.put("/tasks/{task_id}")
async def update_task(
    task_id: str,
    title: str,
    description: str,
    user_id: str = Depends(get_current_user)
):
    result = await task_collection.update_one(
        {"_id": ObjectId(task_id), "owner": user_id},
        {"$set": {"title": title, "description": description}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"message": "Task updated"}

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    user_id: str = Depends(get_current_user)
):
    result = await task_collection.delete_one(
        {"_id": ObjectId(task_id), "owner": user_id}
    )

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"message": "Task deleted"}

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    await blacklist_collection.insert_one({"token": token})
    return {"message": "Logged out successfully"}