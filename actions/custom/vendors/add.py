from typing import List, Dict, Text, Any

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions.actions import profile_db


class ActionAddVendor(Action):
    def name(self) -> Text:
        return "action_add_vendor"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[Dict[Text, Any]]:
        profile_db.add_vendor(tracker.get_slot("vendor"))

        dispatcher.utter_message(f"{tracker.get_slot('vendor')} is added")
        return [SlotSet("vendor", None)]
