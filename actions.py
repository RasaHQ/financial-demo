from typing import Dict, Text, Any, List, Union, Optional
import datetime
from dateutil import relativedelta
import logging
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction, REQUESTED_SLOT
from rasa_sdk.events import Form, AllSlotsReset, SlotSet, Restarted, EventType

logger = logging.getLogger(__name__)


class CustomFormAction(FormAction):
    def name(self):
        return ""

    def request_next_slot(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> Optional[List[EventType]]:
        """Request the next slot and utter template if needed,
            else return None"""

        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):
                logger.debug(f"Request next slot '{slot}'")
                dispatcher.utter_message(
                    template=f"utter_ask_{self.name()}_{slot}", **tracker.slots
                )
                return [SlotSet(REQUESTED_SLOT, slot)]

        return []


class PayCCForm(CustomFormAction):
    """Pay credit card form..."""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "cc_payment_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["credit_card", "payment_amount", "time", "confirm"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "credit_card": self.from_entity(entity="credit_card"),
            "payment_amount": [
                self.from_entity(entity="payment_amount"),
                self.from_entity(entity="amount-of-money"),
                self.from_entity(entity="number"),
            ],
            "time": [self.from_entity(entity="time")],
            "confirm": [
                self.from_intent(value=True, intent="affirm"),
                self.from_intent(value=False, intent="deny"),
            ],
        }

    @staticmethod
    def payment_amount_db() -> Dict[Text, Any]:
        """Database of supported payment amounts"""

        return {
            "minimum balance": 85,
            "current balance": 550,
        }

    @staticmethod
    def credit_card_db() -> List[Text]:
        """Database of supported credit cards"""

        return [
            "iron bank",
            "credit all",
            "gringots",
            "justice bank",
        ]

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer"""

        try:
            int(string)
            return True
        except ValueError:
            return False

    def validate_payment_amount(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate payment amount value."""

        if isinstance(value, int):
            return {"payment_amount": value, "payment_amount_type": ""}

        if value and value.lower() in self.payment_amount_db():
            key = value.lower()
            amount = self.payment_amount_db().get(key)
            return {"payment_amount": amount, "payment_amount_type": f" (your {key})"}
        else:
            dispatcher.utter_message(template="utter_no_payment_amount")
            return {"payment_amount": None}

    def validate_credit_card(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate credit_card value."""

        if value and value.lower() in self.credit_card_db():
            return {"credit_card": value}
        else:
            dispatcher.utter_message(template="utter_no_creditcard")
            return {"credit_card": None}

    def validate_time(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate time value."""

        try:
            time = datetime.datetime.fromisoformat(value).strftime(
                "%I:%M%p, %A %b %d, %Y"
            )
            return {"time": time}
        except TypeError:
            dispatcher.utter_message(template="utter_no_paymentdate")
            return {"time": None}

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        # utter submit template
        if tracker.get_slot("confirm"):
            dispatcher.utter_message(template="utter_cc_pay_scheduled")
        else:
            dispatcher.utter_message(template="utter_cc_pay_cancelled")
        return [AllSlotsReset()]


class TransactSearchForm(CustomFormAction):
    """Transaction search form"""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "transact_search_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["search_type", "time"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "vendor_name": self.from_entity(entity="vendor_name"),
            "time": [self.from_entity(entity="time")],
            "search_type": [
                self.from_trigger_intent(intent="search_transactions", value="spend"),
                self.from_trigger_intent(intent="check_earnings", value="deposit"),
            ],
        }

    @staticmethod
    def vendor_name_db() -> List[Text]:
        """Database of supported vendors customers might buy from"""

        return [
            "amazon",
            "target",
            "starbucks",
        ]

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer"""

        try:
            int(string)
            return True
        except ValueError:
            return False

    def validate_vendor_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate vendor_name value."""

        if value and value.lower() in self.vendor_name_db():
            return {"vendor_name": value}
        else:
            dispatcher.utter_message(template="utter_no_vendor_name")
            return {"vendor_name": None}

    def validate_time(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate time value."""

        def get_duration(entity):
            value = entity.get("value")
            try:
                start = value.get("from")
                end = value.get("to")
                grain = entity.get("additional_info").get("from").get("grain")
                reportgrain = "timeframe"
            except AttributeError:
                start = entity.get("from")
                end = entity.get("to")
                grain = entity.get("additional_info").get("grain")
                reportgrain = grain
                
            if not start:
                start = value

            parsedstart = datetime.datetime.fromisoformat(start)

            if end:
                parsedend = datetime.datetime.fromisoformat(end)

            else:
                deltaargs = {f"{grain}s": 1}
                delta = relativedelta.relativedelta(**deltaargs)
                parsedend = parsedstart + delta
                reportgrain = grain

            if any(grain == t for t in ["day","week","month","year"]):
                dateformat = "%A %b %d, %Y"
            else:
                dateformat = "%H:%M %A %b %d, %Y"

            formatted_start_time = parsedstart.strftime(dateformat)
            formatted_end_time = parsedend.strftime(dateformat)

            return {
                "time": value,
                "start_time": formatted_start_time,
                "end_time": formatted_end_time,
                "transact_grain": reportgrain,
            }

        tracker_state = tracker.current_state()
        entities = [
            e
            for e in tracker_state["latest_message"]["entities"]
            if e["entity"] == "time"
        ]
        values = None
        for entity in entities:
            values = get_duration(entity)
        if values:
            return values
        else:
            dispatcher.utter_message(template="utter_no_transactdate")
            return {"time": None}

    @staticmethod
    def transactions_db() -> List[Text]:
        """Database of transactions"""

        return {
            "spend": {
                "starbucks": [{"amount": 5.50,}, {"amount": 9.10,}],
                "amazon": [{"amount": 35.95}, {"amount": 9.35}, {"amount": 49.50}],
                "target": [{"amount": 124.95}],
            },
            "deposit": {
                "employer": [{"amount": 1250.00}],
                "interest": [{"amount": 50.50}],
            },
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        search_type = tracker.get_slot("search_type")
        transactions_subset = self.transactions_db().get(search_type)
        vendor = tracker.get_slot("vendor_name")

        if vendor:
            transactions = transactions_subset.get(vendor.lower())
            vendor = f" with {vendor}"
        else:
            transactions = [v for k in list(transactions_subset.values()) for v in k]
            vendor = ""

        numtransacts = len(transactions)
        total = sum([t.get("amount") for t in transactions])
        slotvars = {
            "total": total,
            "numtransacts": numtransacts,
            "start_time": tracker.get_slot("start_time"),
            "end_time": tracker.get_slot("end_time"),
            "transact_grain": tracker.get_slot("transact_grain"),
            "vendor_name": vendor,
        }

        dispatcher.utter_message(
            template=f"utter_searching_{search_type}_transactions", **slotvars
        )
        dispatcher.utter_message(
            template=f"utter_found_{search_type}_transactions", **slotvars
        )

        return [AllSlotsReset()]


class TransferForm(CustomFormAction):
    """Transfer money form..."""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "transfer_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["PERSON", "amount-of-money", "confirm"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "PERSON": [
                self.from_entity(entity="PERSON"),
                self.from_text(intent=["inform", None, "transfer_money"]),
            ],
            "amount-of-money": [
                self.from_entity(entity="amount-of-money"),
                self.from_entity(entity="number"),
            ],
            "confirm": [
                self.from_intent(value=True, intent="affirm"),
                self.from_intent(value=False, intent="deny"),
            ],
        }

    def submit(self, dispatcher, tracker, domain):
        if tracker.get_slot("confirm"):
            dispatcher.utter_message(template="utter_transfer_complete")
            return [
                AllSlotsReset(),
                SlotSet("amount_transferred", tracker.get_slot("amount-of-money")),
            ]
        else:
            dispatcher.utter_message(template="utter_transfer_cancelled")
            return [AllSlotsReset()]


class ActionAccountBalance(Action):
    def name(self):
        return "action_account_balance"

    def run(self, dispatcher, tracker, domain):
        init_account_balance = int(tracker.get_slot("account_balance"))
        amount = tracker.get_slot("amount_transferred")
        if amount:
            amount = int(tracker.get_slot("amount_transferred"))
            account_balance = init_account_balance - amount
            dispatcher.utter_message(
                template="utter_changed_account_balance",
                init_account_balance=init_account_balance,
                account_balance=account_balance,
            )
            return [
                SlotSet("account_balance", account_balance),
                SlotSet("amount_transferred", None),
            ]
        else:
            dispatcher.utter_message(
                template="utter_account_balance",
                init_account_balance=init_account_balance,
            )
            return []
