import sys
import os

# Add app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import User
from app.services.auth_service import AuthService
from app.repositories.user_repo import UserRepository
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_users():
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        
        # Check if admin exists
        # Using a dummy 16 digit NIK for admin
        ADMIN_NIK = "3204000000000001" 
        current_admin = user_repo.get_by_nik(ADMIN_NIK)
        if current_admin:
            print(f"Admin user ({ADMIN_NIK}) already exists.")
            return

        # Create Admin
        hashed_pw = pwd_context.hash("admin123")
        admin_user = User(
            nik=ADMIN_NIK,
            name="Administrator",
            hashed_password=hashed_pw,
            role="admin"
        )
        db.add(admin_user)
        db.commit()
        print(f"Created user: {ADMIN_NIK} / admin123")

    except Exception as e:
        print(f"Error seeding users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
