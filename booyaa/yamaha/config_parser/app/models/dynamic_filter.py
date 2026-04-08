from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .address import Address
from .protocol import Protocol
from .filter import Filter

dynamic_filter_src_addr_table = Table('dynamic_filter_src_addr', Base.metadata,
    Column('dynamic_filter_id', Integer, ForeignKey('dynamic_filters.id')),
    Column('address_id', Integer, ForeignKey('addresses.id'))
)

dynamic_filter_dst_addr_table = Table('dynamic_filter_dst_addr', Base.metadata,
    Column('dynamic_filter_id', Integer, ForeignKey('dynamic_filters.id')),
    Column('address_id', Integer, ForeignKey('addresses.id'))
)

class DynamicFilter(Base):
    __tablename__ = 'dynamic_filters'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    idx: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    
    src_addr: Mapped[list[Address]] = relationship("Address", secondary=dynamic_filter_src_addr_table, back_populates="dynamic_filters_src")
    dst_addr: Mapped[list[Address]] = relationship("Address", secondary=dynamic_filter_dst_addr_table, back_populates="dynamic_filters_dst")
    protocol: Mapped[list[Protocol]] = relationship("Protocol", back_populates="dynamic_filters")
    
    filter_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('filters.id'), nullable=True)
    in_list: Mapped[str | None] = mapped_column(String, nullable=True)
    out_list: Mapped[str | None] = mapped_column(String, nullable=True)
