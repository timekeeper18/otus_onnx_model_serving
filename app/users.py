from typing import Dict, Optional
from app.models import UserRegister, UserOut
from app.auth import get_password_hash, verify_password
import logging

logger = logging.getLogger(__name__)

# In-memory БД
users_db: Dict[str, dict] = {}  # key = username
next_id = 1

def create_user(user_data: UserRegister) -> UserOut:
    global next_id
    if user_data.username in users_db:
        raise ValueError("Username already exists")
    hashed = get_password_hash(user_data.password)
    user_dict = {
        "id": next_id,
        "username": user_data.username,
        "hashed_password": hashed,
        "role": user_data.role if user_data.role in ["user", "admin"] else "user"
    }
    users_db[user_data.username] = user_dict
    next_id += 1
    logger.info(f"User created: {user_data.username} with role {user_dict['role']}")
    return UserOut(id=user_dict["id"], username=user_dict["username"], role=user_dict["role"])

def authenticate_user(username: str, password: str) -> Optional[UserOut]:
    user = users_db.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return UserOut(id=user["id"], username=user["username"], role=user["role"])

def seed_admin():
    """Создать admin-пользователя при старте, если не существует."""
    from app.config import settings
    try:
        admin_data = UserRegister(
            username=settings.ADMIN_USERNAME,
            password=settings.ADMIN_PASSWORD,
            role="admin"
        )
        create_user(admin_data)
        logger.info(f"Admin user seeded: {settings.ADMIN_USERNAME}")
    except ValueError:
        logger.info("Admin user already exists")