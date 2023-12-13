from sqlalchemy import Column, Integer, String, REAL
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CreditCard(Base):
    """Credit cards table. `account_id` is an `Account.id`"""

    __tablename__ = "creditcards"
    id = Column(Integer, primary_key=True)
    credit_card_name = Column(String(255))
    minimum_balance = Column(REAL)
    current_balance = Column(REAL)
    account_id = Column(Integer)
