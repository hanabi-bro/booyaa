from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer
from .base import Base
from .filter import Filter
from .dynamic_filter import DynamicFilter

class Nic(Base):
    __tablename__ = 'nics'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    idx: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    interface: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str | None] = mapped_column(String, nullable=True)
    
    filter_in: Mapped[list[Filter]] = relationship("Filter", back_populates="nic_filter_in")
    dynamic_filter_in: Mapped[list[DynamicFilter]] = relationship("DynamicFilter", back_populates="nic_dynamic_filter_in")
    filter_out: Mapped[list[Filter]] = relationship("Filter", back_populates="nic_filter_out")
    dynamic_filter_out: Mapped[list[DynamicFilter]] = relationship("DynamicFilter", back_populates="nic_dynamic_filter_out")
    
    mtu: Mapped[str] = mapped_column(String, nullable=False)
