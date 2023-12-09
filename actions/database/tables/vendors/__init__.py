import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, DateTime, REAL, UniqueConstraint
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.engine.base import Engine

from sqlalchemy.ext.declarative import declarative_base

DECL_BASE = declarative_base()


class Vendor(DECL_BASE):
    __tablename__ = "vendor"
    __table_args__ = (UniqueConstraint("name"),)
    id = Column(Integer, primary_key=True)
    name = Column(String(80))
