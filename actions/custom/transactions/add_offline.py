from typing import List, Dict, Text, Any

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions.actions import profile_db


class ActionAddOfflineTransaction(Action):
    def name(self) -> Text:
        return "action_add_offline_transaction"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[Dict[Text, Any]]:
        vendor = ...
        timestamp = ...
        amount = ...

        profile_db.add_offline_transaction(vendor, timestamp, amount)

        dispatcher.utter_message(f"Transaction was added!")

        return [
            SlotSet("vendor", None),
            SlotSet("timestamp", None),
            SlotSet("amount-of-money", None),
        ]
