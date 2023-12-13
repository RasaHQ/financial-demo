from sqlalchemy import Column, Integer, String, DateTime, REAL, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base

from actions.database.tables.account import Account

Base = declarative_base()


class Transaction(Base):
    """Transactions table. `to/from` are `Account.id`"""

    __tablename__ = "transactions"
    id = Column(Integer(), primary_key=True)
    amount = Column(REAL())
    from_account = Column(Integer(), ForeignKey(Account.id))
    to_account = Column(Integer(), ForeignKey(Account.id))
    timestamp = Column(DateTime(), server_default=func.now())
