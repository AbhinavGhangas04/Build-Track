import os
import bcrypt
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from database import get_db

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY", "changeme-use-a-long-random-string")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24

def create_token(company_id: int, company_name: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(
        {"sub": str(company_id), "name": company_name, "exp": expire},
        SECRET_KEY, algorithm=ALGORITHM
    )

async def get_current_company(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        company_id = int(payload["sub"])
    except (JWTError, KeyError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    row = await db.fetchrow("SELECT id, name FROM companies WHERE id=$1", company_id)
    if not row:
        raise HTTPException(status_code=401, detail="Company not found")
    return dict(row)

class RegisterRequest(BaseModel):
    company_name: str
    password: str

@router.post("/register")
async def register(body: RegisterRequest, db=Depends(get_db)):
    existing = await db.fetchrow(
        "SELECT id FROM companies WHERE LOWER(name)=LOWER($1)", body.company_name
    )
    if existing:
        raise HTTPException(status_code=400, detail="Company name already registered")
    hashed = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
    row = await db.fetchrow(
        "INSERT INTO companies (name, password_hash) VALUES ($1,$2) RETURNING id, name",
        body.company_name, hashed
    )
    token = create_token(row["id"], row["name"])
    return {"access_token": token, "token_type": "bearer", "company_name": row["name"]}

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    row = await db.fetchrow(
        "SELECT id, name, password_hash FROM companies WHERE LOWER(name)=LOWER($1)",
        form.username
    )
    if not row or not bcrypt.checkpw(form.password.encode(), row["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Invalid company name or password")
    token = create_token(row["id"], row["name"])
    return {"access_token": token, "token_type": "bearer", "company_name": row["name"]}

@router.get("/me")
async def me(company=Depends(get_current_company)):
    return company