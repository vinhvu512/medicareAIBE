# from database.session import engine
# import sqlalchemy

# try:
#     # Try connecting
#     with engine.connect() as connection:
#         print("Database connection successful!")
#         result = connection.execute(sqlalchemy.text("SELECT 1"))
#         print(result.fetchone())
# except Exception as e:
#     print("Connection failed:")
#     print(e)


# from sqlalchemy import inspect
# from database.session import engine

# def check_database_tables():
#     inspector = inspect(engine)
    
#     print("=== Database Tables ===")
#     for table_name in inspector.get_table_names():
#         print(f"\nTable: {table_name}")
#         print("Columns:")
#         for column in inspector.get_columns(table_name):
#             print(f"  - {column['name']}: {column['type']}")
        
#         print("Foreign Keys:")
#         for fk in inspector.get_foreign_keys(table_name):
#             print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

# if __name__ == "__main__":
#     check_database_tables()


# from sqlalchemy import create_engine, text
# from dotenv import load_dotenv
# import os

# def test_database_connection():
#     try:
#         # Load environment variables
#         load_dotenv()
        
#         # Create connection URL
#         DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
#         print(DATABASE_URL)
        
#         # Create engine
#         engine = create_engine(DATABASE_URL)
        
#         # Test connection
#         with engine.connect() as connection:
#             result = connection.execute(text("SELECT version();"))
#             version = result.scalar()
            
#             # Get list of tables
#             tables = connection.execute(text("""
#                 SELECT table_name 
#                 FROM information_schema.tables 
#                 WHERE table_schema='public'
#             """))
            
#             print("Database connection successful!")
#             print(f"PostgreSQL version: {version}")
#             print("\nAvailable tables:")
#             for table in tables:
#                 print(f"- {table[0]}")
            
#     except Exception as e:
#         print("Connection failed!")
#         print(f"Error: {str(e)}")

# if __name__ == "__main__":
#     test_database_connection()







# from sqlalchemy import create_engine
# from sqlalchemy.sql import text

# DATABASE_URL = "postgresql://avnadmin:AVNS_QSsTUYqH5WT0YzWIW5U@medicare-ai-dev-myfirstproject.e.aivencloud.com:23928/defaultdb"

# def test_connection():
#     try:
#         engine = create_engine(DATABASE_URL)
#         with engine.connect() as conn:
#             result = conn.execute(text("SELECT 1"))
#             print("Connection successful!")
#     except Exception as e:
#         print(f"Connection failed: {str(e)}")

# if __name__ == "__main__":
#     test_connection()



import requests
import json

def test_signup_doctors():
    url = "http://localhost:8000/api/auth/signup"
    doctors_data = [
        {
            "username": "nguyenhoang",
            "email": "nguyenhoang@gmail.com",
            "password": "1234",
            "fullname": "Nguyễn Hoàng",
            "date_of_birth": "1995-03-15",
            "gender": "Male",
            "user_type": "Patient",
            "address": "24 Lê Lợi, Quận 1, TP. Hồ Chí Minh",
            "phone": "+84123456790",
            "profile_image": "https://example.com/nguyenhoang-profile.jpg"
        },
        {
            "username": "tranminhthu",
            "email": "tranminhthu@gmail.com",
            "password": "1234",
            "fullname": "Trần Minh Thư",
            "date_of_birth": "1988-07-10",
            "gender": "Female",
            "user_type": "Patient",
            "address": "78 Nguyễn Thị Minh Khai, Quận 3, TP. Hồ Chí Minh",
            "phone": "+84123456791",
            "profile_image": "https://example.com/tranminhthu-profile.jpg"
        },
        {
            "username": "phamquanghuy",
            "email": "phamquanghuy@gmail.com",
            "password": "1234",
            "fullname": "Phạm Quang Huy",
            "date_of_birth": "1992-12-05",
            "gender": "Male",
            "user_type": "Patient",
            "address": "56 Cách Mạng Tháng 8, Quận 10, TP. Hồ Chí Minh",
            "phone": "+84123456792",
            "profile_image": "https://example.com/phamquanghuy-profile.jpg"
        },
        {
            "username": "ledoantrang",
            "email": "ledoantrang@gmail.com",
            "password": "1234",
            "fullname": "Lê Đoan Trang",
            "date_of_birth": "1990-09-20",
            "gender": "Female",
            "user_type": "Patient",
            "address": "45 Nguyễn Văn Trỗi, Phú Nhuận, TP. Hồ Chí Minh",
            "phone": "+84123456793",
            "profile_image": "https://example.com/ledoantrang-profile.jpg"
        },
        {
            "username": "hoangtuankiet",
            "email": "hoangtuankiet@gmail.com",
            "password": "1234",
            "fullname": "Hoàng Tuấn Kiệt",
            "date_of_birth": "1985-06-15",
            "gender": "Male",
            "user_type": "Patient",
            "address": "67 Phan Xích Long, Bình Thạnh, TP. Hồ Chí Minh",
            "phone": "+84123456794",
            "profile_image": "https://example.com/hoangtuankiet-profile.jpg"
        }
    ]

    headers = {
        'Content-Type': 'application/json'
    }

    for doctor in doctors_data:
        try:
            response = requests.post(url, json=doctor, headers=headers)
            print(f"Signing up doctor {doctor['username']}:")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}\n")
        except Exception as e:
            print(f"Error signing up doctor {doctor['username']}: {str(e)}\n")

if __name__ == "__main__":
    test_signup_doctors()