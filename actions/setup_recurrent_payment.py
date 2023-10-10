from datetime import datetime
from typing import List, Optional

from rasa.shared.nlu.training_data.message import Message
from rasa_sdk import Action, Tracker
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from rasa.nlu.extractors.duckling_entity_extractor import DucklingEntityExtractor
from typing import List, Optional

duckling_config = {**DucklingEntityExtractor.get_default_config(),
                   "url": "https://rasa:xCTBjGqjTqDqE6X72FXLiBWVXYaQDZ@duckling.rasa-dev.io",
                   "dimensions": ["time"]}
duckling = DucklingEntityExtractor(duckling_config)


def parse_datetime(text: str) -> Optional[datetime]:
    msg = Message.build(text)
    duckling.process([msg])
    if len(msg.data["entities"]) == 0:
        return None

    parsed_value = msg.data["entities"][0]["value"]
    if isinstance(parsed_value, dict):
        parsed_value = parsed_value["from"]

    return datetime.fromisoformat(parsed_value)


class ValidatePaymentStartDate(Action):
    def name(self) -> str:
        return "validate_recurrent_payment_start_date"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> List[EventType]:
        current_value = tracker.get_slot("recurrent_payment_start_date")
        if current_value is None:
            return []

        start_date = parse_datetime(current_value)
        start_date_timezone = start_date.tzinfo if start_date else None
        if start_date is None or (start_date and start_date < datetime.now(tz=start_date_timezone)):
            dispatcher.utter_message(response="utter_invalid_date")
            return [SlotSet("recurrent_payment_start_date", None)]

        return [SlotSet("recurrent_payment_start_date", start_date.isoformat())]


class ValidatePaymentEndDate(Action):
    def name(self) -> str:
        return "validate_recurrent_payment_end_date"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> List[EventType]:
        current_value = tracker.get_slot("recurrent_payment_end_date")
        if current_value is None:
            return []

        end_date = parse_datetime(current_value)
        if end_date is None:
            dispatcher.utter_message(response="utter_invalid_date")
            return [SlotSet("recurrent_payment_end_date", None)]

        start_date = tracker.get_slot("recurrent_payment_start_date")
        if start_date is not None and end_date < datetime.fromisoformat(start_date):
            dispatcher.utter_message(response="utter_invalid_date")
            return [SlotSet("recurrent_payment_end_date", None)]

        return [SlotSet("recurrent_payment_end_date", end_date.isoformat())]


class ExecutePayment(Action):
    def name(self) -> str:
        return "action_execute_recurrent_payment"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> List[EventType]:
        # set-up payment logic here
        return [SlotSet("setup_recurrent_payment_successful", True)]
