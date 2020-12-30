import os
import sqlalchemy as sa
from sqlalchemy import Column, Integer, JSON, ARRAY, String, DateTime, Boolean, Numeric
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

PROFILE_DB_NAME = os.environ.get("PROFILE_DB_NAME", "profile")

PROFILE_DB_URL = os.environ.get("PROFILE_DB_URL", "postgres://localhost/profile")
ENGINE = sa.create_engine(PROFILE_DB_URL)

try:
    ENGINE.connect()
except sa.exc.OperationalError:
    DEFAULT_DB_URL = "postgres://localhost/postgres"
    DEFAULT_ENGINE = sa.create_engine(DEFAULT_DB_URL)
    conn = DEFAULT_ENGINE.connect()
    conn.execute("commit")
    conn.execute(f"CREATE DATABASE {PROFILE_DB_NAME}")
    conn.close()

Base = declarative_base(bind=ENGINE)


class Account(Base):

    __tablename__ = "account"
    account_id = Column(Integer, primary_key=True)
    session_id = Column(String(255))
    account_holder_name = Column(String(255))
    currency = Column(String(255))


class CreditCard(Base):

    __tablename__ = "creditcards"
    credit_card_id = Column(Integer, primary_key=True)
    credit_card_name = Column(String(255))
    minimum_balance = Column(Numeric)
    current_balance = Column(Numeric)
    account_id = Column(String(255))


class Transaction(Base):

    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    amount = Column(Numeric)
    from_account_number = Column(String(14))
    to_account_number = Column(String(14))


class RecipientRelationship(Base):

    __tablename__ = "recipient_relationships"
    id = Column(Integer, primary_key=True)
    account_holder_id = Column(String(255))
    recipient_account_id = Column(String(12))
    recipient_nickname = Column(String(255))


def get_database_session(database_engine) -> Session:
    return sessionmaker(bind=database_engine, autoflush=True)()


CreditCard.__table__.create(ENGINE, checkfirst=True)
Transaction.__table__.create(ENGINE, checkfirst=True)
RecipientRelationship.__table__.create(ENGINE, checkfirst=True)
Account.__table__.create(ENGINE, checkfirst=True)

SESSION = sessionmaker(bind=ENGINE, autoflush=True)()
