from .db.session import engine
from .models.base import Base
from .models import Address, Protocol, Filter, DynamicFilter, Nic

# テーブルの作成
Base.metadata.create_all(bind=engine)
