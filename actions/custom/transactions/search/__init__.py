from typing import Dict, Text, Any, List
from dateutil import parser
import sqlalchemy as sa

from rasa_sdk.interfaces import Action
from rasa_sdk.events import (
    SlotSet,
)
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.actions import profile_db


class ActionTransactionSearch(Action):
    """Searches for a transaction"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "action_transaction_search"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Executes the action"""
        slots = {
            "AA_CONTINUE_FORM": None,
            "zz_confirm_form": None,
            "time": None,
            "time_formatted": None,
            "start_time": None,
            "end_time": None,
            "start_time_formatted": None,
            "end_time_formatted": None,
            "grain": None,
            "search_type": None,
            "vendor_name": None,
        }

        if tracker.get_slot("zz_confirm_form") == "yes":
            search_type = tracker.get_slot("search_type")
            deposit = search_type == "deposit"
            vendor = tracker.get_slot("vendor_name")
            vendor_name = f" at {vendor.title()}" if vendor else ""
            start_time = parser.isoparse(tracker.get_slot("start_time"))
            end_time = parser.isoparse(tracker.get_slot("end_time"))
            transactions = profile_db.search_transactions(
                tracker.sender_id,
                start_time=start_time,
                end_time=end_time,
                deposit=deposit,
                vendor=vendor,
            )

            aliased_transactions = transactions.subquery()
            total = profile_db.session.query(
                sa.func.sum(aliased_transactions.c.amount)
            )[0][0]
            if not total:
                total = 0
            numtransacts = transactions.count()
            slotvars = {
                "total": f"{total:.2f}",
                "numtransacts": numtransacts,
                "start_time_formatted": tracker.get_slot("start_time_formatted"),
                "end_time_formatted": tracker.get_slot("end_time_formatted"),
                "vendor_name": vendor_name,
            }

            dispatcher.utter_message(
                response=f"utter_searching_{search_type}_transactions",
                **slotvars,
            )
            dispatcher.utter_message(
                response=f"utter_found_{search_type}_transactions", **slotvars
            )
        else:
            dispatcher.utter_message(response="utter_transaction_search_cancelled")

        return [SlotSet(slot, value) for slot, value in slots.items()]
