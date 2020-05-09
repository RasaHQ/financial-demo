from typing import Dict, Text, Any, List, Union, Optional
import logging
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction, REQUESTED_SLOT
from rasa_sdk.events import SlotSet, EventType
from actions.parsing import (
    parse_duckling_time_as_interval,
    parse_duckling_time,
    get_entity_details,
    parse_duckling_currency,
)

logger = logging.getLogger(__name__)


def custom_request_next_slot(
    form,
    dispatcher: "CollectingDispatcher",
    tracker: "Tracker",
    domain: Dict[Text, Any],
) -> Optional[List[EventType]]:
    """Request the next slot and utter template if needed,
        else return None"""

    for slot in form.required_slots(tracker):
        if form._should_request_slot(tracker, slot):
            logger.debug(f"Request next slot '{slot}'")
            dispatcher.utter_message(
                template=f"utter_ask_{form.name()}_{slot}", **tracker.slots
            )
            return [SlotSet(REQUESTED_SLOT, slot)]

    return None


class PayCCForm(FormAction):
    """Pay credit card form..."""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "cc_payment_form"

    def request_next_slot(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> Optional[List[EventType]]:

        return custom_request_next_slot(self, dispatcher, tracker, domain)

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

    def validate_payment_amount(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate payment amount value."""

        try:
            entity = get_entity_details(
                tracker, "amount-of-money"
            ) or get_entity_details(tracker, "number")
            amount_currency = parse_duckling_currency(entity)
            return amount_currency
        except:
            pass
        if value and value.lower() in self.payment_amount_db():
            key = value.lower()
            amount = self.payment_amount_db().get(key)
            amount_type = f" (your {key})"
            return {
                "payment_amount": f"{amount:.2f}",
                "payment_amount_type": amount_type,
                "currency": "$",
            }

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

        timeentity = get_entity_details(tracker, "time")
        parsedtime = parse_duckling_time(timeentity)
        if not parsedtime:
            dispatcher.utter_message(template="utter_no_transactdate")
            return {"time": None}
        return parsedtime

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        if tracker.get_slot("confirm"):
            dispatcher.utter_message(template="utter_cc_pay_scheduled")
        else:
            dispatcher.utter_message(template="utter_cc_pay_cancelled")
        return [
            SlotSet("credit_card", None),
            SlotSet("payment_amount", None),
            SlotSet("confirm", None),
            SlotSet("time", None),
            SlotSet("grain", None)
        ]


class TransactSearchForm(FormAction):
    """Transaction search form"""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "transact_search_form"

    def request_next_slot(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> Optional[List[EventType]]:

        return custom_request_next_slot(self, dispatcher, tracker, domain)

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
                self.from_trigger_intent(
                    intent="search_transactions", value="spend"
                ),
                self.from_trigger_intent(
                    intent="check_earnings", value="deposit"
                ),
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
        timeentity = get_entity_details(tracker, "time")
        parsedinterval = parse_duckling_time_as_interval(timeentity)
        if not parsedinterval:
            dispatcher.utter_message(template="utter_no_transactdate")
            return {"time": None}
        return parsedinterval

    @staticmethod
    def transactions_db() -> Dict[Text, Any]:
        """Database of transactions"""

        return {
            "spend": {
                "starbucks": [{"amount": 5.50}, {"amount": 9.10}],
                "amazon": [
                    {"amount": 35.95},
                    {"amount": 9.35},
                    {"amount": 49.50},
                ],
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
        transactions_subset = self.transactions_db().get(search_type, {})
        vendor = tracker.get_slot("vendor_name")

        if vendor:
            transactions = transactions_subset.get(vendor.lower())
            vendor = f" with {vendor}"
        else:
            transactions = [
                v for k in list(transactions_subset.values()) for v in k
            ]
            vendor = ""

        numtransacts = len(transactions)
        total = sum([t.get("amount") for t in transactions])
        slotvars = {
            "total": f"{total:.2f}",
            "numtransacts": numtransacts,
            "start_time": tracker.get_slot("start_time"),
            "end_time": tracker.get_slot("end_time"),
            "grain": tracker.get_slot("grain"),
            "vendor_name": vendor,
        }

        dispatcher.utter_message(
            template=f"utter_searching_{search_type}_transactions", **slotvars
        )
        dispatcher.utter_message(
            template=f"utter_found_{search_type}_transactions", **slotvars
        )

        return [
            SlotSet("time", None),
            SlotSet("start_time", None),
            SlotSet("end_time", None),
            SlotSet("grain", None),
            SlotSet("search_type", None),
        ]


class TransferForm(FormAction):
    """Transfer money form..."""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "transfer_form"

    def request_next_slot(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> Optional[List[EventType]]:

        return custom_request_next_slot(self, dispatcher, tracker, domain)

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["PERSON", "amount_of_money", "confirm"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "PERSON": [self.from_entity(entity="PERSON")],
            "amount_of_money": [
                self.from_entity(entity="amount-of-money"),
                self.from_entity(entity="number"),
            ],
            "confirm": [
                self.from_intent(value=True, intent="affirm"),
                self.from_intent(value=False, intent="deny"),
            ],
        }

    def validate_amount_of_money(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        try:
            entity = get_entity_details(
                tracker, "amount-of-money"
            ) or get_entity_details(tracker, "number")
            amount_currency = parse_duckling_currency(entity)
            return amount_currency
        except:
            dispatcher.utter_message(template="utter_no_payment_amount")
            return {"amount_of_money": None}

    def submit(self, dispatcher, tracker, domain):
        if tracker.get_slot("confirm"):
            dispatcher.utter_message(template="utter_transfer_complete")
            return [
                SlotSet("PERSON", None),
                SlotSet("amount_of_money", None),
                SlotSet("confirm", None),
                SlotSet(
                    "amount_transferred", tracker.get_slot("amount_of_money")
                )
            ]
        else:
            dispatcher.utter_message(template="utter_transfer_cancelled")
            return [
                SlotSet("PERSON", None),
                SlotSet("amount_of_money", None),
                SlotSet("confirm", None)
            ]


class ActionAccountBalance(Action):
    def name(self):
        return "action_account_balance"

    def run(self, dispatcher, tracker, domain):
        init_account_balance = float(tracker.get_slot("account_balance"))
        amount = tracker.get_slot("amount_transferred")
        if amount:
            amount = float(tracker.get_slot("amount_transferred"))
            account_balance = init_account_balance - amount
            dispatcher.utter_message(
                template="utter_changed_account_balance",
                init_account_balance=f"{init_account_balance:.2f}",
                account_balance=f"{account_balance:.2f}",
            )
            return [
                SlotSet("payment_amount", None),
                SlotSet("account_balance", account_balance),
                SlotSet("amount_transferred", None),
            ]
        else:
            dispatcher.utter_message(
                template="utter_account_balance",
                init_account_balance=f"{init_account_balance:.2f}",
            )
            return [SlotSet("payment_amount", None)]
