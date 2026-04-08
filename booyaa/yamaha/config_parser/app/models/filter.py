from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .address import Address
from .protocol import Protocol

filter_src_addr_table = Table('filter_src_addr', Base.metadata,
    Column('filter_id', Integer, ForeignKey('filters.id')),
    Column('address_id', Integer, ForeignKey('addresses.id'))
)

filter_dst_addr_table = Table('filter_dst_addr', Base.metadata,
    Column('filter_id', Integer, ForeignKey('filters.id')),
    Column('address_id', Integer, ForeignKey('addresses.id'))
)

class Filter(Base):
    __tablename__ = 'filters'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    idx: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    
    src_addr: Mapped[list[Address]] = relationship("Address", secondary=filter_src_addr_table, back_populates="filters_src")
    dst_addr: Mapped[list[Address]] = relationship("Address", secondary=filter_dst_addr_table, back_populates="filters_dst")
    protocol: Mapped[list[Protocol]] = relationship("Protocol", back_populates="filters")

    src_port: Mapped[str] = mapped_column(String, nullable=False)
    dst_port: Mapped[str] = mapped_column(String, nullable=False)
