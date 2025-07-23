"""
Authentication API endpoints: register, login, logout, and current user info.

Uses password hashing (bcrypt), JWT tokens for authentication, and FastAPI security utilities.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os

from src.db import SessionLocal
from src.models import User, UserRole
from src.repositories import UserRepository

# ========================
# CONFIGURATION CONSTANTS
# ========================
SECRET_KEY = os.environ.get("SECRET_KEY", "change_this_secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

# Password hashing scheme using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# For FastAPI OAuth2 dependency
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# ========================
# Pydantic Schemas
# ========================
class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True

class UserRegister(BaseModel):
    username: str = Field(..., example="teacher1")
    full_name: str = Field(..., example="John Doe")
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole = Field(default=UserRole.teacher)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# ================
# PASSWORD UTILS
# ================
# PUBLIC_INTERFACE
def get_password_hash(password: str) -> str:
    """Hash the given password using bcrypt."""
    return pwd_context.hash(password)

# PUBLIC_INTERFACE
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that a plain password matches its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)

# =========================
# TOKEN/JWT UTILS
# =========================
# PUBLIC_INTERFACE
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# PUBLIC_INTERFACE
def get_db():
    """Yield a database session generator for FastAPI dependencies."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# PUBLIC_INTERFACE
def get_user_by_username(db: Session, username: str):
    """Get a User by their username."""
    return db.query(User).filter(User.username == username).first()

# PUBLIC_INTERFACE
def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user with username and password."""
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

# PUBLIC_INTERFACE
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Retrieve the current user using JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# PUBLIC_INTERFACE
@router.post("/register", response_model=UserOut, summary="Register a new user", description="Create a new user with username, password (hashed), full name, email, and role.")
def register(user: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter((User.username == user.username) | (User.email == user.email)).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already registered.")
    hashed_password = get_password_hash(user.password)
    new_user = {
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "hashed_password": hashed_password,
        "role": user.role
    }
    db_user = UserRepository().create(db, new_user)
    return db_user

# PUBLIC_INTERFACE
@router.post("/login", response_model=Token, summary="Login and retrieve JWT token", description="Authenticate user and get JWT access token for future API calls.")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# PUBLIC_INTERFACE
@router.post("/logout", summary="Logout user (stateless JWT)", description="Client side should discard the JWT; server has no session to destroy. (Optional placeholder endpoint)")
def logout(request: Request):
    # This is a placeholder, as JWT is stateless and logout is handled client-side.
    return {"message": "Successfully logged out. Please discard the token client-side."}

# PUBLIC_INTERFACE
@router.get("/me", response_model=UserOut, summary="Get current user info", description="Retrieve the profile of the currently authenticated user.")
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
