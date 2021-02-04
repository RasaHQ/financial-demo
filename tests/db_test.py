import os
import sqlalchemy as sa
import pytest

from actions.profile_db import (
    GENERAL_ACCOUNTS,
    create_database,
    ProfileDB,
    Account,
)

PROFILE_DB_NAME = os.environ.get("PROFILE_DB_NAME", "profile")
PROFILE_DB_URL = os.environ.get("PROFILE_DB_URL", f"sqlite:///{PROFILE_DB_NAME}.db")
ENGINE = sa.create_engine(PROFILE_DB_URL)
create_database(ENGINE, PROFILE_DB_NAME)

profile_db = ProfileDB(ENGINE)
profile_db.create_tables()

session_id = "test"
profile_db.populate_profile_db(session_id)
currency = profile_db.get_currency(session_id)

account = profile_db.get_account_from_session_id(session_id)
account_number = profile_db.get_account_number(account)
account_from_number = profile_db.get_account_from_number(account_number)

recipient_names = profile_db.list_known_recipients(session_id)
recipient_name = recipient_names[0]
recipient = profile_db.get_recipient_from_name(session_id, recipient_name)
recipient_account_number = profile_db.get_account_number(recipient)

account_balance = profile_db.get_account_balance(session_id)
profile_db.transact(account_number, recipient_account_number, 100)
account_balance_now = profile_db.get_account_balance(session_id)

credit_cards = profile_db.list_credit_cards(session_id)
balance_types = profile_db.list_balance_types()


def test_profile_initialization():
    assert profile_db.check_session_id_exists(session_id)
    assert profile_db.check_general_accounts_populated(GENERAL_ACCOUNTS)
    assert profile_db.get_currency(session_id) == "$"


def test_account_from_account_number():
    assert account is account_from_number


def test_transact():
    assert account_balance_now == account_balance - 100


def test_cc_payment_1():
    credit_card_name = credit_cards[0]
    balance_type = balance_types[0]

    credit_card_balance = profile_db.get_credit_card_balance(
        session_id, credit_card_name, balance_type
    )
    profile_db.pay_off_credit_card(session_id, credit_card_name, credit_card_balance)
    credit_card_balance_now = profile_db.get_credit_card_balance(
        session_id, credit_card_name, balance_type
    )
    assert credit_card_balance_now == 0


def test_cc_payment_2():
    credit_card_name = credit_cards[1]
    balance_type = balance_types[1]

    credit_card_balance = profile_db.get_credit_card_balance(
        session_id, credit_card_name, balance_type
    )
    profile_db.pay_off_credit_card(session_id, credit_card_name, credit_card_balance)
    credit_card_balance_now = profile_db.get_credit_card_balance(
        session_id, credit_card_name, balance_type
    )
    assert credit_card_balance_now == 0
