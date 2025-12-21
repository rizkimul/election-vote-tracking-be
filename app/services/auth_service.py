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

    def register(self, nik: str, name: str, password: str):
        if self.user_repo.get_by_nik(nik):
            raise ValueError("NIK already registered")
        hashed = self.hash_password(password)
        user = models.User(nik=nik, name=name, hashed_password=hashed)
        return self.user_repo.create(user)

    def create_token(self, nik: str) -> dict:
        import time
        expire = int(time.time()) + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        payload = {"sub": nik, "exp": expire}
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
        return {"access_token": token, "token_type": "bearer"}

    def authenticate(self, nik: str, password: str):
        user = self.user_repo.get_by_nik(nik)
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

