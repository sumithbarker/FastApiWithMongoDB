from fastapi import APIRouter, HTTPException, Depends
from app.database import user_collection
from app.auth import verify_password, create_access_token
from app.dependencies import oauth2_scheme
from app.auth import hash_password

router = APIRouter()

@router.post("/login")
async def login(email: str, password: str):
    user = await user_collection.find_one({"email": email, "is_active": True})

    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "user_id": str(user["_id"]),
        "role": user["role"]
    })

    return {"access_token": token, "token_type": "bearer"}

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    await blacklist_collection.insert_one({"token": token})
    return {"message": "Logged out successfully"}

@router.post("/register")
async def register_user(email: str, password: str):
    user = {
        "email": email,
        "hashed_password": hash_password(password),
        "role": "user",
        "is_active": True
    }
    await user_collection.insert_one(user)
    return {"message": "User registered"}

@router.post("/forgot-password")
async def forgot_password(email: str):
    otp = str(random.randint(100000, 999999))

    await otp_collection.insert_one({
        "email": email,
        "otp": otp,
        "expires_at": datetime.utcnow() + timedelta(minutes=5)
    })

    # send_email(email, otp)  ← mocked / real SMTP
    return {"message": "OTP sent to email"}

@router.post("/reset-password")
async def reset_password(email: str, otp: str, new_password: str):
    record = await otp_collection.find_one({"email": email, "otp": otp})

    if not record or record["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    await user_collection.update_one(
        {"email": email},
        {"$set": {"hashed_password": hash_password(new_password)}}
    )

    await otp_collection.delete_many({"email": email})
    return {"message": "Password reset successful"}