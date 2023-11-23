from typing import List, Dict, Text, Any

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


class MyAction(Action):
    def name(self) -> Text:
        return "my_mom_action"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> List[Dict[Text, Any]]:
        print("called!")
        dispatcher.utter_message(response="utter_pog")

        return []
