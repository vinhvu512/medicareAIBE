from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.session import Base
from database.crud import create_user, delete_user
from schemas.user import UserCreate

DATABASE_URL = "postgresql://postgres:postgresql@localhost:5432/rmit-database"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tạo bảng nếu chưa có
Base.metadata.create_all(bind=engine)

def main():
    db = SessionLocal()

    # Tạo user mới
    print("Tạo user Alice...")
    user_data = UserCreate(name="Alice", email="alice@example.com")
    user = create_user(db, user_data)
    print(f"User created: {user.name}, {user.email}, ID: {user.id}")

    # Xóa user
    print(f"Xóa user ID: {user.id}...")
    # result = delete_user(db, user.id)
    print("Xóa thành công!" if result else "Không tìm thấy user!")

    db.close()

if __name__ == "__main__":
    main()
