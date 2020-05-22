from random import (
    choice,
    randint,
    randrange,
    sample,
)
from numpy import arange
from datetime import date, timedelta


def create_mock_profile():
    currency = "$"
    account_balance = 0

    credit_card_balance = {}
    transaction_history = {"spend": {}, "deposit": {}}

    credit_card_db = [
        "iron bank",
        "credit all",
        "gringots",
        "justice bank",
    ]
    deposit_db = [
        "employer",
        "interest",
    ]
    recipient_db = [
        "emma",
        "evan",
        "william",
        "karen",
        "kyle",
        "john",
        "percy",
        "lisa",
    ]
    vendor_db = [
        "target",
        "starbucks",
        "amazon",
    ]

    start_date = date(2019, 1, 1)
    end_date = date.today()
    number_of_days = (end_date - start_date).days

    for vendor in vendor_db:
        rand_spend_amounts = sample(
            [round(amount, 2) for amount in list(arange(5, 50, 0.01))],
            randint(1, 5),
        )

        rand_dates = [
            (
                start_date + timedelta(days=randrange(number_of_days))
            ).isoformat()
            for x in range(0, len(rand_spend_amounts))
        ]

        transaction_history["spend"][vendor] = [
            {"amount": amount, "date": date}
            for amount, date in zip(rand_spend_amounts, rand_dates)
        ]
        account_balance -= sum(rand_spend_amounts)

    for deposit in deposit_db:
        rand_deposit_amounts = sample(
            [round(amount, 2) for amount in list(arange(1000, 2000, 0.01))],
            randint(1, 5),
        )

        rand_dates = [
            (
                start_date + timedelta(days=randrange(number_of_days))
            ).isoformat()
            for x in range(0, len(rand_deposit_amounts))
        ]

        transaction_history["deposit"][deposit] = [
            {"amount": amount, "date": date}
            for amount, date in zip(rand_deposit_amounts, rand_dates)
        ]
        account_balance += sum(rand_deposit_amounts)

    for credit_card in credit_card_db:
        credit_card_balance[credit_card] = {
            "minimum balance": 20,
            "current balance": choice(
                [round(amount, 2) for amount in list(arange(20, 500, 0.01))]
            ),
        }

    mock_profile = {
        "account_balance": f"{account_balance:.2f}",
        "currency": currency,
        "transaction_history": transaction_history,
        "credit_card_balance": credit_card_balance,
        "known_recipients": recipient_db,
        "vendor_list": vendor_db,
    }
    return mock_profile
