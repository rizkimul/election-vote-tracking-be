from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import HTTPException
from datetime import datetime, timedelta
import uuid
from ..config import JWT_SECRET, JWT_ALGO, ACCESS_TOKEN_EXPIRE_MINUTES
from .. import models
from ..schemas import UserUpdate, PasswordChange
from sqlalchemy.orm import Session

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

    def create_token(self, identifier: str, user_id: int) -> dict:
        """Create JWT token and Refresh Token"""
        import time
        # Access Token
        expire = int(time.time()) + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        payload = {"sub": identifier, "exp": expire}
        access_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
        
        # Refresh Token
        refresh_token = self.create_refresh_token(user_id)
        
        return {
            "access_token": access_token, 
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    def create_refresh_token(self, user_id: int) -> str:
        """Generate and store a refresh token"""
        token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(days=7) # 7 days expiration
        
        db_token = models.RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        self.user_repo.db.add(db_token)
        self.user_repo.db.commit()
        return token

    def verify_refresh_token(self, token: str):
        """Verify refresh token validity"""
        db_token = self.user_repo.db.query(models.RefreshToken).filter(
            models.RefreshToken.token == token
        ).first()
        
        if not db_token:
            return None
            
        if db_token.revoked:
            return None
            
        if db_token.expires_at < datetime.utcnow():
            return None
            
        return db_token

    def revoke_refresh_token(self, token: str):
        """Revoke a refresh token"""
        db_token = self.user_repo.db.query(models.RefreshToken).filter(
            models.RefreshToken.token == token
        ).first()
        if db_token:
            db_token.revoked = True
            self.user_repo.db.commit()

    def refresh_access_token(self, refresh_token: str) -> dict:
        """Exchange refresh token for new access token"""
        db_token = self.verify_refresh_token(refresh_token)
        if not db_token:
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
            
        user = db_token.user
        identifier = user.username or user.nik
        
        # We can also decide to rotate the refresh token here if we want strict security
        # For now, let's keep the same refresh token until it expires
        
        import time
        expire = int(time.time()) + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        payload = {"sub": identifier, "exp": expire}
        access_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token, # Return same refresh token
            "token_type": "bearer"
        }

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

