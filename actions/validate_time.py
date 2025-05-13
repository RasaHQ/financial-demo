from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import re
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from actions.parsing import (
    parse_duckling_time_as_interval,
    parse_duckling_time,
    get_entity_details,
    parse_duckling_currency,
)

class ValidateTime(Action):
    def name(self) -> Text:
        return "validate_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Validates value of 'time' slot"""
        started_collect = tracker.get_slot("started_collect")
        timeentity = get_entity_details(tracker, "time")
        if started_collect != "collect_time" or timeentity is None:
            return []

        parsedtime = timeentity and parse_duckling_time(timeentity)
        parsedtime_interval = timeentity and parse_duckling_time_as_interval(timeentity)


        if not parsedtime:
            dispatcher.utter_message(response="utter_no_transactdate")
            return [SlotSet("time", None)]
        try:
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
            time_formatted = parsedtime["time_formatted"]
            start_time = parsedtime_interval["start_time"]
            end_time = parsedtime_interval["end_time"]
            start_time_formatted = parsedtime_interval["start_time_formatted"]
            end_time_formatted = parsedtime_interval["end_time_formatted"]
            grain = parsedtime_interval["grain"]

            print(f"time_formatted: {time_formatted}")
            print(f"start_time: {start_time}")
            print(f"end_time: {end_time}")
            print(f"start_time_formatted: {start_time_formatted}")
            print(f"end_time_formatted: {end_time_formatted}")
            print(f"grain: {grain}")

            return [SlotSet("time_formatted", time_formatted)]
        except KeyError:
            dispatcher.utter_message(response="utter_no_transactdate")
            return [SlotSet("time", None)]

