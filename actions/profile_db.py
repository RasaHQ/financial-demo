import os
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, DateTime, REAL
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from random import choice, randrange, sample, randint
from numpy import arange
from datetime import datetime, timedelta
import pytz

utc = pytz.UTC

GENERAL_ACCOUNTS = {
    "recipient": [
        "katy parrow",
        "evan oslo",
        "william baker",
        "karen lancaster",
        "kyle gardner",
        "john jacob",
        "percy donald",
        "lisa macintyre",
    ],
    "vendor": ["target", "starbucks", "amazon",],
    "depositor": ["interest", "employer"],
}

ACCOUNT_NUMBER_LENGTH = 12
CREDIT_CARD_NUMBER_LENGTH = 14


Base = declarative_base()


class Account(Base):

    __tablename__ = "account"
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255))
    account_holder_name = Column(String(255))
    currency = Column(String(255))


class CreditCard(Base):

    __tablename__ = "creditcards"
    id = Column(Integer, primary_key=True)
    credit_card_name = Column(String(255))
    minimum_balance = Column(REAL)
    current_balance = Column(REAL)
    account_id = Column(Integer)


class Transaction(Base):

    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    amount = Column(REAL)
    from_account_number = Column(String(14))
    to_account_number = Column(String(14))


class RecipientRelationship(Base):

    __tablename__ = "recipient_relationships"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer)
    recipient_account_id = Column(Integer)
    recipient_nickname = Column(String(255))


def create_database(database_engine, database_name):
    try:
        database_engine.connect()
    except sa.exc.OperationalError:
        default_db_url = "postgresql://localhost/postgres"
        default_engine = sa.create_engine(default_db_url)
        conn = default_engine.connect()
        conn.execute("commit")
        conn.execute(f"CREATE DATABASE {database_name}")
        conn.close()


class ProfileDB:
    def __init__(self, db_engine):
        self.engine = db_engine
        self.create_tables()
        self.session = self.get_session()

    def get_session(self) -> Session:
        return sessionmaker(bind=self.engine, autoflush=True)()

    def create_tables(self):
        CreditCard.__table__.create(self.engine, checkfirst=True)
        Transaction.__table__.create(self.engine, checkfirst=True)
        RecipientRelationship.__table__.create(self.engine, checkfirst=True)
        Account.__table__.create(self.engine, checkfirst=True)

    def get_account(self, id):
        return self.session.query(Account).filter(Account.id == id).first()

    def get_account_from_session_id(self, session_id):
        return (
            self.session.query(Account).filter(Account.session_id == session_id).first()
        )

    @staticmethod
    def get_account_number(account):
        if type(account) is CreditCard:
            return f"%0.{CREDIT_CARD_NUMBER_LENGTH}d" % account.id
        else:
            return f"%0.{ACCOUNT_NUMBER_LENGTH}d" % account.id

    def get_account_from_number(self, account_number):
        if len(account_number) == CREDIT_CARD_NUMBER_LENGTH:
            return (
                self.session.query(CreditCard)
                .filter(CreditCard.id == int(account_number))
                .first()
            )
        else:
            return (
                self.session.query(Account)
                .filter(Account.id == int(account_number))
                .first()
            )

    def get_recipient_from_name(self, session_id, recipient_name):
        account = self.get_account_from_session_id(session_id)
        recipient = (
            self.session.query(RecipientRelationship)
            .filter(RecipientRelationship.account_id == account.id)
            .filter(RecipientRelationship.recipient_nickname == recipient_name.lower())
            .first()
        )
        recipient_account = self.get_account(recipient.recipient_account_id)
        return recipient_account

    def list_known_recipients(self, session_id):
        recipients = (
            self.session.query(RecipientRelationship.recipient_nickname)
            .filter(
                RecipientRelationship.account_id
                == self.get_account_from_session_id(session_id).id
            )
            .all()
        )
        return [recipient.recipient_nickname for recipient in recipients]

    def check_session_id_exists(self, session_id):
        return self.session.query(
            self.session.query(Account.session_id)
            .filter(Account.session_id == session_id)
            .exists()
        ).scalar()

    def get_account_balance(self, session_id):
        account_number = self.get_account_number(
            self.get_account_from_session_id(session_id)
        )
        spent = float(
            self.session.query(sa.func.sum(Transaction.amount))
            .filter(Transaction.from_account_number == account_number)
            .all()[0][0]
        )
        earned = float(
            self.session.query(sa.func.sum(Transaction.amount))
            .filter(Transaction.to_account_number == account_number)
            .all()[0][0]
        )
        return earned - spent

    def get_currency(self, session_id):
        return (
            self.session.query(Account.currency)
            .filter(Account.session_id == session_id)
            .first()[0]
        )

    def list_credit_cards(self, session_id):
        account = self.get_account_from_session_id(session_id)
        cards = (
            self.session.query(CreditCard)
            .filter(CreditCard.account_id == account.id)
            .all()
        )
        return [card.credit_card_name for card in cards]

    def get_credit_card(self, session_id, credit_card_name):
        account = self.get_account_from_session_id(session_id)
        return (
            self.session.query(CreditCard)
            .filter(CreditCard.account_id == account.id)
            .filter(CreditCard.credit_card_name == credit_card_name.lower())
            .first()
        )

    def get_credit_card_balance(
        self, session_id, credit_card_name, balance_type="current_balance"
    ):
        card = self.get_credit_card(session_id, credit_card_name)
        return getattr(card, balance_type)

    @staticmethod
    def list_balance_types():
        return [
            name
            for name in CreditCard.__table__.columns.keys()
            if name.endswith("balance")
        ]

    def pay_off_credit_card(self, session_id, credit_card_name, amount):
        account = self.get_account_from_session_id(session_id)
        account_number = self.get_account_number(account)
        credit_card = (
            self.session.query(CreditCard)
            .filter(CreditCard.account_id == account.id)
            .filter(CreditCard.credit_card_name == credit_card_name.lower())
            .first()
        )
        self.transact(
            account_number, self.get_account_number(credit_card), amount,
        )
        credit_card.current_balance -= amount
        if amount < credit_card.minimum_balance:
            credit_card.minimum_balance -= amount
        else:
            credit_card.minimum_balance = 0
        self.session.commit()

    def add_session_account(self, session_id, name=""):
        self.session.add(
            Account(session_id=session_id, account_holder_name=name, currency="$")
        )

    def add_credit_cards(self, session_id):

        credit_card_names = ["iron bank", "credit all", "emblem", "justice bank"]
        session_credit_cards = sample(
            credit_card_names, choice(list(range(2, len(credit_card_names))))
        )
        credit_cards = [
            CreditCard(
                credit_card_name=cardname,
                minimum_balance=choice([20, 30, 40]),
                current_balance=choice(
                    [round(amount, 2) for amount in list(arange(20, 500, 0.01))]
                ),
                account_id=self.get_account_from_session_id(session_id).id,
            )
            for cardname in session_credit_cards
        ]
        self.session.add_all(credit_cards)

    def check_general_accounts_populated(self, general_account_names):
        account_names = set(
            [
                name
                for list_names in general_account_names.values()
                for name in list_names
            ]
        )
        existing_accounts = self.session.query(Account.account_holder_name).filter(
            Account.account_holder_name.in_(account_names)
        )
        existing_account_names = set(
            [account.account_holder_name for account in existing_accounts.all()]
        )
        return account_names == existing_account_names

    def add_general_accounts(self, general_account_names):
        general_accounts = [
            Account(session_id=f"{prefix}_{id}", account_holder_name=name)
            for prefix, names in general_account_names.items()
            for id, name in enumerate(names)
        ]

        for account in general_accounts:
            self.session.merge(account)
        self.session.commit()

    def add_recipients(self, session_id):
        account = self.get_account_from_session_id(session_id)
        recipients = (
            self.session.query(Account.account_holder_name, Account.id)
            .filter(Account.session_id.startswith("recipient_"))
            .all()
        )
        session_recipients = sample(recipients, choice(list(range(3, len(recipients)))))
        relationships = [
            RecipientRelationship(
                account_id=account.id,
                recipient_account_id=recipient.id,
                recipient_nickname=recipient.account_holder_name,
            )
            for recipient in session_recipients
        ]
        self.session.add_all(relationships)

    def add_transactions(self, session_id):
        account_number = self.get_account_number(
            self.get_account_from_session_id(session_id)
        )
        vendors = (
            self.session.query(Account)
            .filter(Account.session_id.startswith("vendor_"))
            .all()
        )
        depositors = (
            self.session.query(Account)
            .filter(Account.session_id.startswith("depositor_"))
            .all()
        )

        start_date = utc.localize(datetime(2019, 1, 1))
        end_date = utc.localize(datetime.now())
        number_of_days = (end_date - start_date).days

        for vendor in vendors:
            rand_spend_amounts = sample(
                [round(amount, 2) for amount in list(arange(5, 50, 0.01))],
                number_of_days // 2,
            )

            rand_dates = [
                (start_date + timedelta(days=randrange(number_of_days)))
                for x in range(0, len(rand_spend_amounts))
            ]

            spend_transactions = [
                Transaction(
                    from_account_number=account_number,
                    to_account_number=self.get_account_number(vendor),
                    amount=amount,
                    timestamp=date,
                )
                for amount, date in zip(rand_spend_amounts, rand_dates)
            ]

            self.session.add_all(spend_transactions)

        for depositor in depositors:
            if depositor.account_holder_name == "interest":
                rand_deposit_amounts = sample(
                    [round(amount, 2) for amount in list(arange(5, 20, 0.01))],
                    number_of_days // 30,
                )
            else:
                rand_deposit_amounts = sample(
                    [round(amount, 2) for amount in list(arange(1000, 2000, 0.01))],
                    number_of_days // 14,
                )

            rand_dates = [
                (start_date + timedelta(days=randrange(number_of_days)))
                for x in range(0, len(rand_deposit_amounts))
            ]

            deposit_transactions = [
                Transaction(
                    from_account_number=self.get_account_number(depositor),
                    to_account_number=account_number,
                    amount=amount,
                    timestamp=date,
                )
                for amount, date in zip(rand_deposit_amounts, rand_dates)
            ]

            self.session.add_all(deposit_transactions)

    def populate_profile_db(self, session_id):
        if not self.check_general_accounts_populated(GENERAL_ACCOUNTS):
            self.add_general_accounts(GENERAL_ACCOUNTS)
        if not self.check_session_id_exists(session_id):
            self.add_session_account(session_id)
            self.add_recipients(session_id)
            self.add_transactions(session_id)
            self.add_credit_cards(session_id)

        self.session.commit()

    def transact(self, from_account_number, to_account_number, amount):
        timestamp = datetime.now()
        transaction = Transaction(
            from_account_number=from_account_number,
            to_account_number=to_account_number,
            amount=amount,
            timestamp=timestamp,
        )
        self.session.add(transaction)
        self.session.commit()
