import os
import sqlalchemy as sa

from random import choice, randrange, sample, randint
from numpy import arange
from datetime import datetime, timedelta
import pytz

from actions.profile_db import (
    SESSION as session,
    Account,
    CreditCard,
    Transaction,
    RecipientRelationship,
)

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


def get_account_number(id, credit_account=False):
    if credit_account:
        return f"%0.{CREDIT_CARD_NUMBER_LENGTH}d" % id
    else:
        return f"%0.{ACCOUNT_NUMBER_LENGTH}d" % id


def account_id_from_session_id(session_id):
    return (
        session.query(Account.account_id)
        .filter(Account.session_id == session_id)
        .first()
        .account_id
    )


def account_from_number(account_number):
    if len(account_number) == CREDIT_CARD_NUMBER_LENGTH:
        return (
            session.query(CreditCard)
            .filter(CreditCard.credit_card_id == int(account_number))
            .first()
        )
    else:
        return (
            session.query(Account)
            .filter(Account.account_id == int(account_number))
            .first()
        )


def session_id_exists(session_id):
    return session.query(
        session.query(Account.session_id)
        .filter(Account.session_id == session_id)
        .exists()
    ).scalar()


def get_account_balance(session_id):
    account_number = get_account_number(account_id_from_session_id(session_id))
    spent = float(
        session.query(sa.func.sum(Transaction.amount))
        .filter(Transaction.from_account_number(account_number))
        .all()[0][0]
    )
    earned = float(
        session.query(sa.func.sum(Transaction.amount))
        .filter(Transaction.to_account_number(account_number))
        .all()[0][0]
    )
    return earned - spent


def get_currency(session_id):
    return (
        session.query(Account.currency)
        .filter(Account.session_id == session_id)
        .first()[0]
    )


def get_credit_card_balance(session):
    account_id = account_id_from_session_id(session_id)
    return float(
        session.query(sa.func.sum(CreditCard.current_balance))
        .filter(CreditCard.account_id == account_id)
        .all()[0][0]
    )


def add_session_account(session_id):
    session.add(Account(session_id=session_id, account_holder_name="", currency="$"))


def add_credit_cards(session_id):

    credit_card_names = ["iron bank", "credit all", "emblem", "justice bank"]
    session_credit_cards = sample(
        credit_card_names, choice(list(range(1, len(credit_card_names))))
    )
    credit_cards = [
        CreditCard(
            credit_card_name=cardname,
            minimum_balance=choice([20, 30, 40]),
            current_balance=choice(
                [round(amount, 2) for amount in list(arange(20, 500, 0.01))]
            ),
            account_id=account_id_from_session_id(session_id),
        )
        for cardname in session_credit_cards
    ]
    session.add_all(credit_cards)


def general_accounts_populated(general_account_names):
    account_names = set(
        [name for list_names in general_account_names.values() for name in list_names]
    )
    existing_accounts = session.query(Account.account_holder_name).filter(
        Account.account_holder_name.in_(account_names)
    )
    existing_account_names = set(
        [account.account_holder_name for account in existing_accounts.all()]
    )
    return account_names == existing_account_names


def add_general_accounts(general_account_names):
    general_accounts = [
        Account(session_id=f"{prefix}_{id}", account_holder_name=name)
        for prefix, names in general_account_names.items()
        for id, name in enumerate(names)
    ]

    for account in general_accounts:
        session.merge(account)


def define_recipients(session_id):
    account_id = account_id_from_session_id(session_id)
    recipients = (
        session.query(Account.account_holder_name, Account.account_id)
        .filter(Account.session_id.startswith("recipient_"))
        .all()
    )
    session_recipients = sample(recipients, choice(list(range(3, len(recipients)))))
    relationships = [
        RecipientRelationship(
            account_holder_id=account_id,
            recipient_account_id=recipient.account_id,
            recipient_nickname=recipient.account_holder_name,
        )
        for recipient in recipients
    ]
    session.add_all(relationships)


def add_transactions(session_id):
    account_number = get_account_number(account_id_from_session_id(session_id))
    vendors = (
        session.query(Account).filter(Account.session_id.startswith("vendor_")).all()
    )
    depositors = (
        session.query(Account).filter(Account.session_id.startswith("depositor_")).all()
    )

    transactions = []

    start_date = utc.localize(datetime(2019, 1, 1))
    end_date = utc.localize(datetime.now())
    number_of_days = (end_date - start_date).days

    for vendor in vendors:
        rand_spend_amounts = sample(
            [round(amount, 2) for amount in list(arange(5, 50, 0.01))],
            number_of_days // 2,
        )

        rand_dates = [
            (start_date + timedelta(days=randrange(number_of_days))).isoformat()
            for x in range(0, len(rand_spend_amounts))
        ]

        spend_transactions = [
            Transaction(
                from_account_number=account_number,
                to_account_number=get_account_number(vendor.account_id),
                amount=amount,
                timestamp=date,
            )
            for amount, date in zip(rand_spend_amounts, rand_dates)
        ]

        session.add_all(spend_transactions)

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
            (start_date + timedelta(days=randrange(number_of_days))).isoformat()
            for x in range(0, len(rand_deposit_amounts))
        ]

        deposit_transactions = [
            Transaction(
                from_account_number=get_account_number(depositor.account_id),
                to_account_number=account_number,
                amount=amount,
                timestamp=date,
            )
            for amount, date in zip(rand_deposit_amounts, rand_dates)
        ]

        session.add_all(deposit_transactions)


def populate_profile_db(session_id):
    if not general_accounts_populated(GENERAL_ACCOUNTS):
        add_general_accounts(GENERAL_ACCOUNTS)
    if not session_id_exists(session_id):
        add_session_account(session_id)
        define_recipients(session_id)
        add_transactions(session_id)
        add_credit_cards(session_id)

    session.commit()
    return session
