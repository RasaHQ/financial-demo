from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet

from actions.rasaxapi import RasaXAPI

class ActionAccountBalance(Action):

    def name(self) -> Text:
        return "action_account_balance"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        account = tracker.get_slot("account_type")

        dispatcher.utter_message(text=f"Custom action getting the balance for your {account} account.")

        return []


class ActionMakePaymentFormValidation(FormValidationAction):
    def name(self) -> Text:
        return "validate_make_payment_form"

    def validate_credit_card(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate credit card provided by user."""
        user_cc = slot_value.lower()

        valid_cards = ["discover", "visa", "mastercard", "emblem", "preferred", "sapphire", "barclays",
                       "platinum", "citi", "amex"]

        if user_cc not in valid_cards:
            dispatcher.utter_message(f"{slot_value} is not a valid credit card.")
            return {"credit_card": None}

        return {"credit_card": slot_value}

    def validate_payment_amount(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate payment amount provided by user."""
        try:
            pay_amt = int(slot_value.replace("$", ""))
        except ValueError:
            dispatcher.utter_message("Must provide a number for the payment amount.")
            return {"payment_amount": None}

        # Check if positive number.
        if pay_amt <= 0:
            dispatcher.utter_message("Payment amount must be greater than 0.")
            return {"payment_amount": None}

        return {"payment_amount": pay_amt}


class ActionProcessMakePaymentForm(Action):

    def name(self) -> Text:
        return "action_process_make_payment_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Process make payment form."""
        slots = [
            "credit_card",
            "payment_amount"
        ]

        dispatcher.utter_message(template="utter_payment_thank_you")

        # Reset slots for the bot.
        return [SlotSet(s, None) for s in slots]

class ActionTagFeedback(Action):
    """Tag a conversation in Rasa X as positive or negative feedback """

    def name(self):
        return "action_tag_positive_feedback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:

        label = '[{"value":"postive_feedback","color":"76af3d"}]'

        rasax = RasaXAPI()
        rasax.tag_convo(tracker, label)

        return []
