from sqlalchemy import Column, Integer, String, DateTime, REAL, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Transaction(Base):
    """Transactions table. `to/from` are `Account.id`"""

    __tablename__ = "transactions"
    id = Column(Integer(), primary_key=True)
    amount = Column(REAL())
    from_account = Column(Integer(), ForeignKey("account.id"))
    to_account = Column(Integer(), ForeignKey("account.id"))
    timestamp = Column(DateTime(), server_default=func.now())
