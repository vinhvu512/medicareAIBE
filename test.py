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

url = "http://localhost:8000/register"
payload = {
    "m_username": "patient123",
    "m_email": "patient@example.com",
    "m_password": "SecurePass123!",
    "m_fullname": "John Doe",
    "m_date_of_birth": "1990-01-01",
    "m_gender": "Male",  # Changed from MALE to Male
    "m_user_type": "Patient",  # Changed from PATIENT to Patient
    "m_address": "123 Main St, City",
    "m_phone": "+84123456789",
    "m_profile_image": "https://example.com/profile.jpg"
}

response = requests.post(url, json=payload)
print(response.json())