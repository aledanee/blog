from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import Db_Operation
from passlib.hash import bcrypt
from typing import Optional
from fastapi.responses import JSONResponse

app = FastAPI()

# Enable CORS (Cross-Origin Resource Sharing)
origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],  # Include OPTIONS
    allow_headers=["*"],
)


class User(BaseModel):
    username: str
    email: str
    password: str
    profile_picture: Optional[str] = None


@app.post("/register")
async def register_user(user_data: User):
    conn = Db_Operation.connect_to_mysql("localhost", "root", "morootok", "blog")

    # Hash the password before storing
    hashed_password = bcrypt.hash(user_data.password)

    # Check if user already exists
    cursor = conn.cursor()
    query = "SELECT * FROM User WHERE username=%s OR email=%s"
    cursor.execute(query, (user_data.username, user_data.email))
    existing_user = cursor.fetchone()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists.")

    # Create a new user record
    query = "INSERT INTO User (username, email, password) VALUES (%s, %s, %s)"
    cursor.execute(query, (user_data.username, user_data.email, hashed_password))
    conn.commit()

    response = {"message": f"User '{user_data.username}' successfully registered"}
    return response

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


@app.options("/docs")
async def options_docs(request: Request, cors: CORSMiddleware = Depends()):
    print("OPTIONS request received for /docs")
    print(f"Headers: {dict(request.headers)}")
    print(f"Allowed Origins: {cors.allowed_origins}")

    response = JSONResponse(content={"message": "OPTIONS request accepted for /docs"})
    cors.config.apply(response)
    return response
