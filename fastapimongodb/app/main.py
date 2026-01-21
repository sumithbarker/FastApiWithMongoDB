from fastapi import FastAPI

from app.routes import auth, tasks, admin

app = FastAPI(title="Task Manager API")

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(tasks.router, tags=["Tasks"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])