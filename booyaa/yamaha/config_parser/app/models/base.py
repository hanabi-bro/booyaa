from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()














# from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# class Base(DeclarativeBase):
#     """宣言的マッピングの基底クラス."""
#     id: Mapped[int] = mapped_column(primary_key = True, comment = "ID")




### マイグレーション参考
# https://qiita.com/Snorlax/items/5f62a71d22c2d18ac022