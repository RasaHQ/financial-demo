from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class RecipientRelationship(Base):
    """Valid recipients table. `account_id` and `recipient_account_id` are `Account.id`'s"""

    __tablename__ = "recipient_relationships"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("account.id"))
    recipient_account_id = Column(Integer, ForeignKey("account.id"))
    recipient_nickname = Column(String(255))
