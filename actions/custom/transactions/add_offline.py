from typing import List, Dict, Text, Any
import logging

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions.actions import profile_db
from actions.parsing import parse_duckling_time

logger = logging.getLogger(__name__)


class ActionAddOfflineTransaction(Action):
    def name(self) -> Text:
        return "action_add_offline_transaction"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[Dict[Text, Any]]:
        # logger.info(f'{tracker.__dict__["latest_message"]["entities"]}')
        # logger.info(f'Money: {tracker.get_slot("amount-of-money")}')
        # logger.info(f'Time: {tracker.get_slot("time")}')
        # logger.info(f'Vendor: {tracker.get_slot("vendor")}')
        ant = None

        for entity in tracker.latest_message.get("entities"):
            if entity.get("entity") == "time":
                ant = entity

        profile_db.add_offline_transaction(
            rasa_session_id=tracker.sender_id,
            amount=tracker.get_slot("amount-of-money"),
            time=ant.get("time_formatted"),
            to_account_name=tracker.get_slot("vendor"),
        )

        dispatcher.utter_message(f"Transaction was added!")
        #  Add a new transaction to Nike for 321$ that happened yesterday at 7am
        return [
            SlotSet("vendor", None),
            SlotSet("time", None),
            SlotSet("amount-of-money", None),
        ]
