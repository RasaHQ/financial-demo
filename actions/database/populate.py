from typing import Text

from sqlalchemy.orm import Session

from actions.database.tables.account import Account


def populate(session: Session, rasa_session_id: Text) -> None:
    """
    Function is meant to be used when
    the user account is created for current session.
    """
    account = session.query(Account).filter(Account.session_id == rasa_session_id)
    # account = ...
    #
    # if account:
    #     return


def create_missing_user_account(session: Session, rasa_session_id: Text) -> None:
    account = Account(
        session_id=rasa_session_id,
        account_holder_name=f"current_user_{rasa_session_id}",
        currency="$",
        is_vendor=False,
    )
    session.add(account)
    session.commit()


# def add_credit_cards(self, session_id: Text):
#     """Populate the creditcard table for a given session_id"""
#     credit_card_names = ["iron bank", "credit all", "emblem", "justice bank"]
#     credit_cards = [
#         CreditCard(
#             credit_card_name=cardname,
#             minimum_balance=choice([20, 30, 40]),
#             current_balance=choice(
#                 [round(amount, 2) for amount in list(arange(20, 500, 0.01))]
#             ),
#             account_id=self.get_account_from_session_id(session_id).id,
#         )
#         for cardname in credit_card_names
#     ]
#     self.session.add_all(credit_cards)

# def populate_profile_db(self, session_id: Text):
#     """Initialize the database for a conversation session.
#     Will populate all tables with sample values.
#     If general accounts have already been populated, it will only
#     add account-holder-specific values to tables.
#     """
#
#     if not self.check_general_accounts_populated(GENERAL_ACCOUNTS):
#         self.add_general_accounts(GENERAL_ACCOUNTS)
#     if not self.check_session_id_exists(session_id):
#         self.add_session_account(session_id)
#         self.add_recipients(session_id)
#         self.add_transactions(session_id)
#         self.add_credit_cards(session_id)
#
#     self.session.commit()
#
# def add_transactions(self, session_id: Text):
#     # @vendor_update
#
#     """Populate transactions table for a session ID with random transactions"""
#     account_number = self.get_account_number(
#         self.get_account_from_session_id(session_id)
#     )
#     vendors = (
#         self.session.query(Account)
#         .filter(Account.session_id.startswith("vendor_"))
#         .all()
#     )
#     depositors = (
#         self.session.query(Account)
#         .filter(Account.session_id.startswith("depositor_"))
#         .all()
#     )
#
#     start_date = utc.localize(datetime(2019, 1, 1))
#     end_date = utc.localize(datetime.now())
#     number_of_days = (end_date - start_date).days
#
#     for vendor in vendors:
#         rand_spend_amounts = sample(
#             [round(amount, 2) for amount in list(arange(5, 50, 0.01))],
#             number_of_days // 2,
#         )
#
#         rand_dates = [
#             (start_date + timedelta(days=randrange(number_of_days)))
#             for x in range(0, len(rand_spend_amounts))
#         ]
#
#         spend_transactions = [
#             Transaction(
#                 from_account_number=account_number,
#                 to_account_number=self.get_account_number(vendor),
#                 amount=amount,
#                 timestamp=date,
#             )
#             for amount, date in zip(rand_spend_amounts, rand_dates)
#         ]
#
#         self.session.add_all(spend_transactions)
#
#     for depositor in depositors:
#         if depositor.account_holder_name == "interest":
#             rand_deposit_amounts = sample(
#                 [round(amount, 2) for amount in list(arange(5, 20, 0.01))],
#                 number_of_days // 30,
#             )
#         else:
#             rand_deposit_amounts = sample(
#                 [round(amount, 2) for amount in list(arange(1000, 2000, 0.01))],
#                 number_of_days // 14,
#             )
#
#         rand_dates = [
#             (start_date + timedelta(days=randrange(number_of_days)))
#             for x in range(0, len(rand_deposit_amounts))
#         ]
#
#         deposit_transactions = [
#             Transaction(
#                 from_account_number=self.get_account_number(depositor),
#                 to_account_number=account_number,
#                 amount=amount,
#                 timestamp=date,
#             )
#             for amount, date in zip(rand_deposit_amounts, rand_dates)
#         ]
#
#         self.session.add_all(deposit_transactions)

#     def add_session_account(self, session_id: Text, name: Optional[Text] = ""):
#         """Add a new account for a new session_id. Assumes no such account exists yet."""
#         self.session.add(
#             Account(session_id=session_id, account_holder_name=name, currency="$")
#         )
