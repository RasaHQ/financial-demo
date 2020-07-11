from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher

import ruamel.yaml
import pathlib
from typing import Dict, Text, Any, List, Union, Optional
from rasa_sdk.events import SlotSet, EventType

here = pathlib.Path(__file__).parent.absolute()
handoff_config = (
    ruamel.yaml.safe_load(open(f"{here}/handoff_config.yml", "r")) or {}
).get("handoff_hosts", {})


class ActionHandoffOptions(Action):
    def name(self) -> Text:
        return "action_handoff_options"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:

        if not any(
            [config.get("url") for bot, config in handoff_config.items()]
        ):
            dispatcher.utter_message(template="utter_no_handoff")
        else:
            buttons = [
                {
                    "title": config.get("title"),
                    "payload": f'/trigger_handoff{{"handoff_to":"{bot}"}}',
                }
                for bot, config in handoff_config.items()
            ]
            dispatcher.utter_message(
                text="I can't transfer you to a human, but I can transfer you to one of these bots",
                buttons=buttons,
            )
        return []


class ActionHandoff(Action):
    def name(self) -> Text:
        return "action_handoff"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:

        dispatcher.utter_message(template="utter_handoff")
        handoff_to = tracker.get_slot("handoff_to")

        handoff_bot = handoff_config.get(handoff_to, {})
        url = handoff_bot.get("url")

        if url:
            if tracker.get_latest_input_channel() == "rest":
                dispatcher.utter_message(
                    json_message={
                        "handoff_host": url,
                        "title": handoff_bot.get("title"),
                    }
                )
            else:
                dispatcher.utter_message(
                    template="utter_wouldve_handed_off", handoffhost=url
                )
        else:
            dispatcher.utter_message(template="utter_no_handoff")

        return []
