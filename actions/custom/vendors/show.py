from typing import List, Dict, Text, Any

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions.actions import profile_db


class ActionShowVendors(Action):
    def name(self) -> Text:
        return "action_show_vendors"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            f"Here are available vendors: "
            f"{[vendor.account_holder_name for vendor in profile_db.get_vendors()]}",
        )

        return []
