# from typing import Any, Text, Dict, List
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
# from rasa_sdk.events import SlotSet

#######

import os
from typing import Dict, Text, Any, List
import logging
from dateutil import parser
import sqlalchemy as sa

from rasa_sdk.interfaces import Action
from rasa_sdk.events import (
    SlotSet,
    EventType,
    ActionExecuted,
    SessionStarted,
    Restarted,
    FollowupAction,
    UserUtteranceReverted,
)
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.parsing import (
    parse_duckling_time_as_interval,
    parse_duckling_time,
    get_entity_details,
    parse_duckling_currency,
)

from actions.profile_db import create_database, ProfileDB
# from actions.custom_forms import CustomFormValidationAction

logger = logging.getLogger(__name__)

# The profile database is created/connected to when the action server starts
# It is populated the first time `ActionSessionStart.run()` is called .

PROFILE_DB_NAME = os.environ.get("PROFILE_DB_NAME", "profile")
PROFILE_DB_URL = os.environ.get("PROFILE_DB_URL", f"sqlite:///{PROFILE_DB_NAME}.db")
ENGINE = sa.create_engine(PROFILE_DB_URL)
create_database(ENGINE, PROFILE_DB_NAME)

profile_db = ProfileDB(ENGINE)

NEXT_FORM_NAME = {
    "pay_cc": "cc_payment_form",
    "transfer_money": "transfer_money_form",
    "search_transactions": "transaction_search_form",
    "check_earnings": "transaction_search_form",
}

FORM_DESCRIPTION = {
    "cc_payment_form": "credit card payment",
    "transfer_money_form": "money transfer",
    "transaction_search_form": "transaction search",
}


class ActionPayCC(Action):

    def name(self) -> Text:
        return "action_pay_cc"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        credit_card = tracker.get_slot("credit_card")
        amount_of_money = tracker.get_slot("amount-of-money")
        time = tracker.get_slot("time")

        return []
        # slots = {
        #     "credit_card": None,
        #     "account_type": None,
        #     "amount-of-money": None,
        #     "time": None,
        #     "time_formatted": None,
        #     "start_time": None,
        #     "end_time": None,
        #     "start_time_formatted": None,
        #     "end_time_formatted": None,
        #     "grain": None,
        #     "number": None,
        # }
        #
        # if tracker.get_slot("zz_confirm_form") == "yes":
        #     credit_card = tracker.get_slot("credit_card")
        #     amount_of_money = float(tracker.get_slot("amount-of-money"))
        #     amount_transferred = float(tracker.get_slot("amount_transferred"))
        #     profile_db.pay_off_credit_card(
        #         tracker.sender_id, credit_card, amount_of_money
        #     )
        #
        #     dispatcher.utter_message(response="utter_cc_pay_scheduled")
        #
        #     slots["amount_transferred"] = amount_transferred + amount_of_money
        # else:
        #     dispatcher.utter_message(response="utter_cc_pay_cancelled")
        #
        # return [SlotSet(slot, value) for slot, value in slots.items()]



# class ActionPayCC(Action):
#     """Pay credit card."""
#
#     def name(self) -> Text:
#         """Unique identifier of the action"""
#         return "action_pay_cc"
#
#     async def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict]:
#         """Executes the action"""
#
#         slots = {
#             "AA_CONTINUE_FORM": None,
#             "zz_confirm_form": None,
#             "credit_card": None,
#             "account_type": None,
#             "amount-of-money": None,
#             "time": None,
#             "time_formatted": None,
#             "start_time": None,
#             "end_time": None,
#             "start_time_formatted": None,
#             "end_time_formatted": None,
#             "grain": None,
#             "number": None,
#         }
#
#         if tracker.get_slot("zz_confirm_form") == "yes":
#             credit_card = tracker.get_slot("credit_card")
#             amount_of_money = float(tracker.get_slot("amount-of-money"))
#             amount_transferred = float(tracker.get_slot("amount_transferred"))
#             profile_db.pay_off_credit_card(
#                 tracker.sender_id, credit_card, amount_of_money
#             )
#
#             dispatcher.utter_message(response="utter_cc_pay_scheduled")
#
#             slots["amount_transferred"] = amount_transferred + amount_of_money
#         else:
#             dispatcher.utter_message(response="utter_cc_pay_cancelled")
#
#         return [SlotSet(slot, value) for slot, value in slots.items()]

#
# class ValidatePayCCForm(CustomFormValidationAction):
#     """Validates Slots of the cc_payment_form"""
#
#     def name(self) -> Text:
#         """Unique identifier of the action"""
#         return "validate_cc_payment_form"

    # def amount_from_balance(
    #     self, dispatcher, tracker, credit_card_name, balance_type
    # ) -> Dict[Text, Any]:
    #     amount_balance = profile_db.get_credit_card_balance(
    #         tracker.sender_id, credit_card_name, balance_type
    #     )
    #     account_balance = profile_db.get_account_balance(tracker.sender_id)
    #     if account_balance < float(amount_balance):
    #         dispatcher.utter_message(response="utter_insufficient_funds")
    #         return {"amount-of-money": None}
    #     return {
    #         "amount-of-money": f"{amount_balance:.2f}",
    #         "payment_amount_type": f"(your {balance_type})",
    #     }

    # async def validate_amount_of_money(
    #     self,
    #     value: Text,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: Dict[Text, Any],
    # ) -> Dict[Text, Any]:
    #     """Validates value of 'amount-of-money' slot"""
    #     if not value:
    #         return {"amount-of-money": None}
    #
    #     account_balance = profile_db.get_account_balance(tracker.sender_id)
    #     # check if user asked to pay the full or the minimum balance
    #     if type(value) is str:
    #         credit_card_name = tracker.get_slot("credit_card")
    #         if credit_card_name:
    #             credit_card = profile_db.get_credit_card(
    #                 tracker.sender_id, credit_card_name
    #             )
    #         else:
    #             credit_card = None
    #         balance_types = profile_db.list_balance_types()
    #         if value and value.lower() in balance_types:
    #             balance_type = value.lower()
    #             if not credit_card:
    #                 dispatcher.utter_message(
    #                     f"I see you'd like to pay the {balance_type}."
    #                 )
    #                 return {"amount-of-money": balance_type}
    #             slots_to_set = self.amount_from_balance(
    #                 dispatcher, tracker, credit_card_name, balance_type
    #             )
    #             if float(slots_to_set.get("amount-of-money")) == 0:
    #                 dispatcher.utter_message(
    #                     response="utter_nothing_due", **slots_to_set
    #                 )
    #                 return {
    #                     "amount-of-money": None,
    #                     "credit_card": None,
    #                     "payment_amount_type": None,
    #                 }
    #             return slots_to_set
    #
    #     try:
    #         entity = get_entity_details(
    #             tracker, "amount-of-money"
    #         ) or get_entity_details(tracker, "number")
    #         amount_currency = parse_duckling_currency(entity)
    #         if not amount_currency:
    #             raise TypeError
    #         if account_balance < float(amount_currency.get("amount-of-money")):
    #             dispatcher.utter_message(response="utter_insufficient_funds")
    #             return {"amount-of-money": None}
    #         return amount_currency
    #     except (TypeError, AttributeError):
    #         pass
    #
    #     dispatcher.utter_message(response="utter_no_payment_amount")
    #     return {"amount-of-money": None}

    # async def validate_credit_card(
    #     self,
    #     value: Text,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: Dict[Text, Any],
    # ) -> Dict[Text, Any]:
    #     """Validates value of 'credit_card' slot"""
    #     if value and value.lower() in profile_db.list_credit_cards(tracker.sender_id):
    #         amount = tracker.get_slot("amount-of-money")
    #         credit_card_slot = {"credit_card": value.title()}
    #         balance_types = profile_db.list_balance_types()
    #         if amount and amount.lower() in balance_types:
    #             updated_amount = self.amount_from_balance(
    #                 dispatcher, tracker, value.lower(), amount
    #             )
    #             if float(updated_amount.get("amount-of-money")) == 0:
    #                 dispatcher.utter_message(
    #                     response="utter_nothing_due", **updated_amount
    #                 )
    #                 return {
    #                     "amount-of-money": None,
    #                     "credit_card": None,
    #                     "payment_amount_type": None,
    #                 }
    #             account_balance = profile_db.get_account_balance(tracker.sender_id)
    #             if account_balance < float(updated_amount.get("amount-of-money")):
    #                 dispatcher.utter_message(
    #                     response="utter_insufficient_funds_specific", **updated_amount
    #                 )
    #                 return {"amount-of-money": None}
    #             return {**credit_card_slot, **updated_amount}
    #         return credit_card_slot
    #
    #     dispatcher.utter_message(response="utter_no_creditcard")
    #     return {"credit_card": None}

    # async def explain_credit_card(
    #     self,
    #     value: Text,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: Dict[Text, Any],
    # ) -> Dict[Text, Any]:
    #     """Explains 'credit_card' slot"""
    #     dispatcher.utter_message("You have the following credits cards:")
    #     for credit_card in profile_db.list_credit_cards(tracker.sender_id):
    #         current_balance = profile_db.get_credit_card_balance(
    #             tracker.sender_id, credit_card
    #         )
    #         dispatcher.utter_message(
    #             response="utter_credit_card_balance",
    #             **{
    #                 "credit_card": credit_card.title(),
    #                 "amount-of-money": f"{current_balance:.2f}",
    #             },
    #         )
    #     return {}
    #
    # async def validate_time(
    #     self,
    #     value: Text,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: Dict[Text, Any],
    # ) -> Dict[Text, Any]:
    #     """Validates value of 'time' slot"""
    #     timeentity = get_entity_details(tracker, "time")
    #     parsedtime = timeentity and parse_duckling_time(timeentity)
    #     if not parsedtime:
    #         dispatcher.utter_message(response="utter_no_transactdate")
    #         return {"time": None}
    #     return parsedtime

    # async def validate_zz_confirm_form(
    #     self,
    #     value: Text,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: Dict[Text, Any],
    # ) -> Dict[Text, Any]:
    #     """Validates value of 'zz_confirm_form' slot"""
    #     if value in ["yes", "no"]:
    #         return {"zz_confirm_form": value}
    #
    #     return {"zz_confirm_form": None}