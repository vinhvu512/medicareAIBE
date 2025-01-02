from llama_index.core.tools import FunctionTool
from sqlalchemy.orm import Session
from database.session import SessionLocal
from schemas.user import UserCreate
from models.user import User

class UserTool:
    def __init__(self):
        self.add_user_tool = FunctionTool.from_defaults(
            fn=self.add_user,
            description="Thêm người dùng mới. Truyền vào 'name' và 'email'"
        )
        self.delete_user_tool = FunctionTool.from_defaults(
            fn=self.request_delete_user,
            description="Yêu cầu xác nhận xóa người dùng. Truyền vào 'user_id'"
        )
        self.confirm_delete_tool = FunctionTool.from_defaults(
            fn=self.confirm_delete_user,
            description="Xác nhận xóa người dùng. Truyền vào 'user_id' và 'confirm' (True/False)"
        )

    def add_user(self, name: str, email: str) -> str:
        db: Session = SessionLocal()
        try:
            user_data = UserCreate(name=name, email=email)
            db_user = User(name=user_data.name, email=user_data.email)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return f"Người dùng {db_user.name} đã được thêm với ID {db_user.id}."
        except Exception as e:
            db.rollback()
            return f"Lỗi khi thêm người dùng: {str(e)}"
        finally:
            db.close()

    def request_delete_user(self, user_id: int) -> str:
        return f"Xác nhận xóa người dùng với ID {user_id}?"

    def confirm_delete_user(self, user_id: int, confirm: bool) -> str:
        if not confirm:
            return "Hành động xóa đã được huỷ."
        db: Session = SessionLocal()
        try:
            db_user = db.query(User).filter(User.id == user_id).first()
            if db_user:
                db.delete(db_user)
                db.commit()
                return f"Người dùng với ID {user_id} đã bị xóa."
            else:
                return "Không tìm thấy người dùng để xóa."
        except Exception as e:
            db.rollback()
            return f"Lỗi khi xóa người dùng: {str(e)}"
        finally:
            db.close()
