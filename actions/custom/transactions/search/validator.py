from typing import Dict, Text, Any, List

from rasa_sdk.events import (
    SlotSet,
    EventType,
)
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.actions import profile_db
from actions.custom_forms import CustomFormValidationAction
from actions.parsing import get_entity_details, parse_duckling_time_as_interval


class ValidateTransactionSearchForm(CustomFormValidationAction):
    """Validates Slots of the transaction_search_form"""

    def name(self) -> Text:
        """Unique identifier of the form"""
        return "validate_transaction_search_form"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        """Custom validates the filled slots"""
        events = await super().run(dispatcher, tracker, domain)

        # For 'spend' type transactions we need to know the vendor
        search_type = tracker.get_slot("search_type")

        if search_type == "spend":
            vendor_name = tracker.get_slot("vendor")

            if not vendor_name:
                events.append(SlotSet("requested_slot", "vendor"))

        return events

    async def validate_search_type(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'search_type' slot"""
        if value in ["spend", "deposit"]:
            return {"search_type": value}

        return {"search_type": None}

    async def validate_vendor(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'vendor' slot"""

        available_vendors = [v.name for v in profile_db.get_vendors()]

        if value and value in available_vendors:
            return {"vendor": value}

        dispatcher.utter_message(response="utter_no_vendor")
        return {"vendor": None}

    async def validate_time(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'time' slot"""
        timeentity = get_entity_details(tracker, "time")
        parsedinterval = timeentity and parse_duckling_time_as_interval(timeentity)
        if not parsedinterval:
            dispatcher.utter_message(response="utter_no_transactdate")
            return {"time": None}

        return parsedinterval
