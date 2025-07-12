import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import Base
from app.db.session import SessionLocal
from app.models import Nic, Filter, DynamicFilter, Address, Protocol



def main():
    db = SessionLocal()
    # ここでデータの挿入やクエリを行う
    db.commit()
    db.close()

if __name__ == "__main__":
    main()













"""
from app.db.session import SessionLocal
from app.models import User


def get_user(user_id: int):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()

if __name__ == "__main__":
    user = get_user(1)
    if user:
        print(f"Found user: {user.username}")
    else:
        print("User not found")
"""