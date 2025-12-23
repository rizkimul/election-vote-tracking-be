from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import HTTPException
from datetime import datetime, timedelta
from ..config import JWT_SECRET, JWT_ALGO, ACCESS_TOKEN_EXPIRE_MINUTES
from .. import models
from ..schemas import UserUpdate, PasswordChange

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def hash_password(self, password: str) -> str:
        return pwd_ctx.hash(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_ctx.verify(plain, hashed)

    def register(self, username: str, name: str, password: str, nik: str = None):
        """Register new user with username (SABADESA) or NIK (legacy)"""
        if self.user_repo.get_by_username(username):
            raise ValueError("Username already registered")
        hashed = self.hash_password(password)
        user = models.User(username=username, name=name, hashed_password=hashed, nik=nik)
        return self.user_repo.create(user)

    def create_token(self, identifier: str) -> dict:
        """Create JWT token using username or NIK as identifier"""
        import time
        expire = int(time.time()) + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        payload = {"sub": identifier, "exp": expire}
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
        return {"access_token": token, "token_type": "bearer"}

    def authenticate(self, username: str, password: str):
        """Authenticate user by username (primary) or NIK (fallback for legacy)"""
        # Try username first (SABADESA)
        user = self.user_repo.get_by_username(username)
        # Fallback to NIK for backward compatibility
        if not user:
            user = self.user_repo.get_by_nik(username)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user

    def decode_token(self, token: str):
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
            return payload
        except JWTError as e:
            with open("/tmp/auth_error.txt", "w") as f:
                f.write(str(e))
            return None

    def update_profile(self, user: models.User, data: UserUpdate):
        if data.name is not None:
            user.name = data.name
        if data.email is not None:
            user.email = data.email
        if data.phone is not None:
            user.phone = data.phone
        return self.user_repo.update(user)

    def change_password(self, user: models.User, data: PasswordChange):
        if not self.verify_password(data.current_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Password saat ini salah")
        user.hashed_password = self.hash_password(data.new_password)
        return self.user_repo.update(user)

