"""Custom actions"""
from typing import Dict, Text, Any, List
import logging
from abc import abstractmethod
from dateutil import parser
from rasa_sdk import utils
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.interfaces import Action
from rasa_sdk.events import (
    SlotSet,
    EventType,
    ActionExecuted,
    SessionStarted,
    Restarted,
    FollowupAction,
    UserUtteranceReverted,
)
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.parsing import (
    parse_duckling_time_as_interval,
    parse_duckling_time,
    get_entity_details,
    parse_duckling_currency,
)
from actions.profile import create_mock_profile


logger = logging.getLogger(__name__)


MAX_VALIDATION_FAILURES = 2

NEXT_FORM_NAME = {
    "pay_cc": "cc_payment_form",
    "transfer_money": "transfer_money_form",
    "search_transactions": "transaction_search_form",
    "check_earnings": "transaction_search_form",
}

FORM_DESCRIPTION = {
    "cc_payment_form": "credit card payment",
    "transfer_money_form": "money transfer",
    "transaction_search_form": "transaction search",
}


async def shared_validate_continue_form(value: Text) -> Dict[Text, Any]:
    """Validates value of 'continue_form' slot, which is identical for all the forms"""
    if value == "yes":
        return {"continue_form": value}

    if value == "no":
        # This will activate rule 'Submit ---_form' to cancel the operation
        return {
            "requested_slot": None,
            "confirm": "no",
            "continue_form": value,
        }

    # The user's answer was not valid. Just re-set it to None.
    return {"continue_form": None}


class MyFormValidationAction(FormValidationAction):
    """Tracks repeated validation failures"""

    # making this an abstractmethod avoids registering a custom action
    @abstractmethod
    def name(self) -> Text:
        pass

    async def validate(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> List[EventType]:
        """In addition to regular slot validation,
        - tracks repeated validation failures
        - when MAX_VALIDATION_FAILURES reached:
          - explains the slot, if an explain_{slot} method is provided
          - asks user to continue or not
        """
        events = []

        if not tracker.get_slot("continue_form"):
            events.append(SlotSet("continue_form", "yes"))

        events.extend(await super().validate(dispatcher, tracker, domain))

        events.extend(
            await self.repeated_validation_failures(dispatcher, tracker, domain, events)
        )

        return events

    async def repeated_validation_failures(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
        events: List[EventType],
    ) -> List[EventType]:
        """Updates the slot repeated_validation_failures, and sets required form slot
        `continue_form` to None when the threshold is reached.

        This will trigger utter_ask_{form}_continue_form, asking the user if they want
        to continue with this form or not.
        """
        rvf_events = []
        requested_slot = tracker.get_slot("requested_slot")

        # Only do this while form is asking for a certain slot
        if not requested_slot:
            return rvf_events

        # Skip if validate_{slot} turned off the form by setting requested_slot to None
        for event in events:
            if (
                event["event"] == "slot"
                and event["name"] == "requested_slot"
                and not event["value"]
            ):
                rvf_events.append(SlotSet("repeated_validation_failures", 0))
                return rvf_events

        rvf = tracker.get_slot("repeated_validation_failures")
        if rvf:
            rvf = int(rvf)
        else:
            # initialize counter to 0
            rvf = 0

        # check if validation of the requested_slot failed
        validation_failed = False
        for event in events:
            if (
                event["event"] == "slot"
                and event["name"] == requested_slot
                and not event["value"]
            ):
                validation_failed = True
                break

        # keep track of repeated validation failures
        if validation_failed:
            rvf += 1
        else:
            rvf = 0

        if rvf >= MAX_VALIDATION_FAILURES:
            rvf_events.extend(
                await self.explain_requested_slot(dispatcher, tracker, events)
            )
            # reset counter
            rvf = 0

            # Triggers 'utter_ask_{form}_continue_form'
            rvf_events.append(SlotSet("continue_form", None))

        rvf_events.append(SlotSet("repeated_validation_failures", rvf))
        return rvf_events

    async def explain_requested_slot(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[EventType]:
        """Explains requested slot by calling an explain function for the slot.

        Args:
            dispatcher: the dispatcher which is used to
                send messages back to the user.
            tracker: the conversation tracker for the current user.
            domain: the bot's domain.
        Returns:
            `SlotSet` events for the explained slot (Optional).
        """
        slot_name = tracker.get_slot("requested_slot")
        if not slot_name:
            return []

        slot_value = tracker.get_slot(slot_name)

        function_name = f"explain_{slot_name.replace('-','_')}"
        explain_func = getattr(self, function_name, None)

        if not explain_func:
            logger.debug(
                f"Skipping explanation for `{slot_name}`: there is no explanation "
                "function specified."
            )
            return []

        slots = {}
        if utils.is_coroutine_action(explain_func):
            explanation_output = await explain_func(
                slot_value, dispatcher, tracker, domain
            )
        else:
            explanation_output = explain_func(slot_value, dispatcher, tracker, domain)

        if explanation_output:
            slots.update(explanation_output)

        return [SlotSet(slot, value) for slot, value in slots.items()]


class ActionPayCC(Action):
    """Pay credit card."""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "action_pay_cc"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Executes the action"""

        slots = {
            "continue_form": None,
            "confirm": None,
            "credit_card": None,
            "account_type": None,
            "amount-of-money": None,
            "time": None,
            "time_formatted": None,
            "start_time": None,
            "end_time": None,
            "start_time_formatted": None,
            "end_time_formatted": None,
            "grain": None,
            "number": None,
        }

        if tracker.get_slot("confirm") == "yes":
            account_balance = float(tracker.get_slot("account_balance"))
            credit_card = tracker.get_slot("credit_card")
            cc_balance = tracker.get_slot("credit_card_balance")
            amount_of_money = float(tracker.get_slot("amount-of-money"))
            amount_transferred = float(tracker.get_slot("amount_transferred"))

            cc_balance[credit_card.lower()]["current balance"] -= amount_of_money
            account_balance = account_balance - amount_of_money
            dispatcher.utter_message(template="utter_cc_pay_scheduled")

            slots["amount_transferred"] = amount_transferred + amount_of_money
            slots["account_balance"] = f"{account_balance:.2f}"
            slots["credit_card_balance"] = cc_balance
        else:
            dispatcher.utter_message(template="utter_cc_pay_cancelled")

        return [SlotSet(slot, value) for slot, value in slots.items()]


class ValidatePayCCForm(MyFormValidationAction):
    """Validates Slots of the cc_payment_form"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "validate_cc_payment_form"

    async def validate_continue_form(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'continue_form' slot"""
        return await shared_validate_continue_form(value)

    async def validate_amount_of_money(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'amount-of-money' slot"""
        credit_card = tracker.get_slot("credit_card")
        cc_balance = tracker.get_slot("credit_card_balance")
        account_balance = float(tracker.get_slot("account_balance"))
        try:
            entity = get_entity_details(
                tracker, "amount-of-money"
            ) or get_entity_details(tracker, "number")
            amount_currency = parse_duckling_currency(entity)
            if not amount_currency:
                raise TypeError
            if account_balance < float(amount_currency.get("amount-of-money")):
                dispatcher.utter_message(template="utter_insufficient_funds")
                return {"amount-of-money": None}
            return amount_currency
        except (TypeError, AttributeError):
            pass
        # check if user asked to pay the full or the minimum balance
        if value and value.lower() in cc_balance.get(credit_card.lower()):
            key = value.lower()
            amount = cc_balance.get(credit_card.lower()).get(key)
            amount_type = f" (your {key})"

            if account_balance < float(amount):
                dispatcher.utter_message(template="utter_insufficient_funds")
                return {"amount-of-money": None}
            return {
                "amount-of-money": f"{amount:.2f}",
                "payment_amount_type": amount_type,
                "currency": "$",
            }

        dispatcher.utter_message(template="utter_no_payment_amount")
        return {"amount-of-money": None}

    async def validate_credit_card(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'credit_card' slot"""
        cc_balance = tracker.get_slot("credit_card_balance")
        if value and value.lower() in list(cc_balance.keys()):
            return {"credit_card": value.title()}

        dispatcher.utter_message(template="utter_no_creditcard")
        return {"credit_card": None}

    async def explain_credit_card(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Explains 'credit_card' slot"""
        dispatcher.utter_message("You have the following credits cards:")
        credit_card_balance = tracker.get_slot("credit_card_balance")
        for credit_card in credit_card_balance.keys():
            current_balance = credit_card_balance[credit_card]["current balance"]
            dispatcher.utter_message(
                template="utter_credit_card_balance",
                **{
                    "credit_card": credit_card.title(),
                    "amount-of-money": f"{current_balance:.2f}",
                },
            )
        return {}

    async def validate_time(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'time' slot"""
        timeentity = get_entity_details(tracker, "time")
        parsedtime = timeentity and parse_duckling_time(timeentity)
        if not parsedtime:
            dispatcher.utter_message(template="utter_no_transactdate")
            return {"time": None}
        return parsedtime

    async def validate_confirm(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'confirm' slot"""
        if value in ["yes", "no"]:
            return {"confirm": value}

        return {"confirm": None}


class ActionTransactionSearch(Action):
    """Searches for a transaction"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "action_transaction_search"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Executes the action"""
        slots = {
            "continue_form": None,
            "confirm": None,
            "time": None,
            "time_formatted": None,
            "start_time": None,
            "end_time": None,
            "start_time_formatted": None,
            "end_time_formatted": None,
            "grain": None,
            "search_type": None,
            "vendor_name": None,
        }

        if tracker.get_slot("confirm") == "yes":
            search_type = tracker.get_slot("search_type")
            transaction_history = tracker.get_slot("transaction_history")
            transactions_subset = transaction_history.get(search_type, {})
            vendor_name = tracker.get_slot("vendor_name")

            if vendor_name:
                transactions = transactions_subset.get(vendor_name.lower())
                vendor_name = f" with {vendor_name}"
            else:
                transactions = [
                    v for k in list(transactions_subset.values()) for v in k
                ]
                vendor_name = ""

            start_time = parser.isoparse(tracker.get_slot("start_time"))
            end_time = parser.isoparse(tracker.get_slot("end_time"))

            for i in range(len(transactions) - 1, -1, -1):
                transaction = transactions[i]
                transaction_date = parser.isoparse(transaction.get("date"))

                if transaction_date < start_time or transaction_date > end_time:
                    transactions.pop(i)

            numtransacts = len(transactions)
            total = sum([t.get("amount") for t in transactions])
            slotvars = {
                "total": f"{total:.2f}",
                "numtransacts": numtransacts,
                "start_time_formatted": tracker.get_slot("start_time_formatted"),
                "end_time_formatted": tracker.get_slot("end_time_formatted"),
                "vendor_name": vendor_name,
            }

            dispatcher.utter_message(
                template=f"utter_searching_{search_type}_transactions",
                **slotvars,
            )
            dispatcher.utter_message(
                template=f"utter_found_{search_type}_transactions", **slotvars
            )
        else:
            dispatcher.utter_message(template="utter_transaction_search_cancelled")

        return [SlotSet(slot, value) for slot, value in slots.items()]


class ValidateTransactionSearchForm(MyFormValidationAction):
    """Validates Slots of the transaction_search_form"""

    def name(self) -> Text:
        """Unique identifier of the form"""
        return "validate_transaction_search_form"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        """Custom validates the filled slots"""
        events = await super().run(dispatcher, tracker, domain)

        # For 'spend' type transactions we need to know the vendor_name
        search_type = tracker.get_slot("search_type")
        if search_type == "spend":
            vendor_name = tracker.get_slot("vendor_name")
            if not vendor_name:
                events.append(SlotSet("requested_slot", "vendor_name"))

        return events

    async def validate_continue_form(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'continue_form' slot"""
        return await shared_validate_continue_form(value)

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

    async def validate_vendor_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'vendor_name' slot"""
        if value and value.lower() in tracker.get_slot("vendor_list"):
            return {"vendor_name": value}

        dispatcher.utter_message(template="utter_no_vendor_name")
        return {"vendor_name": None}

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
            dispatcher.utter_message(template="utter_no_transactdate")
            return {"time": None}

        return parsedinterval


class ActionTransferMoney(Action):
    """Transfers Money."""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "action_transfer_money"

    async def run(self, dispatcher, tracker, domain):
        """Executes the action"""
        slots = {
            "continue_form": None,
            "confirm": None,
            "PERSON": None,
            "amount-of-money": None,
            "number": None,
        }

        if tracker.get_slot("confirm") == "yes":
            amount_of_money = float(tracker.get_slot("amount-of-money"))
            account_balance = float(tracker.get_slot("account_balance"))

            updated_account_balance = account_balance - amount_of_money

            dispatcher.utter_message(template="utter_transfer_complete")

            amount_transferred = float(tracker.get_slot("amount_transferred"))
            slots["amount_transferred"] = amount_transferred + amount_of_money
            slots["account_balance"] = f"{updated_account_balance:.2f}"
        else:
            dispatcher.utter_message(template="utter_transfer_cancelled")

        return [SlotSet(slot, value) for slot, value in slots.items()]


class ValidateTransferMoneyForm(MyFormValidationAction):
    """Validates Slots of the transfer_money_form"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "validate_transfer_money_form"

    async def validate_continue_form(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'continue_form' slot"""
        return await shared_validate_continue_form(value)

    async def validate_PERSON(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'PERSON' slot"""
        # It is possible that both Spacy & DIET extracted the PERSON
        # Just pick the first one
        if isinstance(value, list):
            value = value[0]

        name = value.title() if value else None
        known_recipients = tracker.get_slot("known_recipients")
        first_names = [name.split()[0] for name in known_recipients]
        if name in known_recipients:
            return {"PERSON": name}

        if name in first_names:
            index = first_names.index(name)
            fullname = known_recipients[index]
            return {"PERSON": fullname}

        dispatcher.utter_message(template="utter_unknown_recipient", PERSON=value)
        return {"PERSON": None}

    async def explain_PERSON(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Explains 'PERSON' slot"""
        recipients = tracker.get_slot("known_recipients")
        formatted_recipients = "\n" + "\n".join(
            [f"- {recipient}" for recipient in recipients]
        )
        dispatcher.utter_message(
            template="utter_recipients",
            formatted_recipients=formatted_recipients,
        )
        return {}

    async def validate_amount_of_money(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'amount-of-money' slot"""
        account_balance = float(tracker.get_slot("account_balance"))
        try:
            entity = get_entity_details(
                tracker, "amount-of-money"
            ) or get_entity_details(tracker, "number")
            amount_currency = parse_duckling_currency(entity)
            if not amount_currency:
                raise TypeError
            if account_balance < float(amount_currency.get("amount-of-money")):
                dispatcher.utter_message(template="utter_insufficient_funds")
                return {"amount-of-money": None}
            return amount_currency
        except (TypeError, AttributeError):
            dispatcher.utter_message(template="utter_no_payment_amount")
            return {"amount-of-money": None}

    async def validate_confirm(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'confirm' slot"""
        if value in ["yes", "no"]:
            return {"confirm": value}

        return {"confirm": None}


class ActionShowBalance(Action):
    """Shows the balance of bank or credit card accounts"""

    def name(self):
        """Unique identifier of the action"""
        return "action_show_balance"

    async def run(self, dispatcher, tracker, domain):
        """Executes the custom action"""
        account_type = tracker.get_slot("account_type")

        if account_type == "credit":
            # show credit card balance
            credit_card_balance = tracker.get_slot("credit_card_balance")
            credit_card = tracker.get_slot("credit_card")

            if credit_card and credit_card.lower() in credit_card_balance:
                current_balance = credit_card_balance[credit_card.lower()][
                    "current balance"
                ]
                dispatcher.utter_message(
                    template="utter_credit_card_balance",
                    **{
                        "credit_card": credit_card.title(),
                        "amount-of-money": f"{current_balance:.2f}",
                    },
                )
            else:
                for credit_card in credit_card_balance.keys():
                    current_balance = credit_card_balance[credit_card][
                        "current balance"
                    ]
                    dispatcher.utter_message(
                        template="utter_credit_card_balance",
                        **{
                            "credit_card": credit_card.title(),
                            "amount-of-money": f"{current_balance:.2f}",
                        },
                    )
        else:
            # show bank account balance
            account_balance = float(tracker.get_slot("account_balance"))
            amount = tracker.get_slot("amount_transferred")
            if amount:
                amount = float(tracker.get_slot("amount_transferred"))
                init_account_balance = account_balance + amount
                dispatcher.utter_message(
                    template="utter_changed_account_balance",
                    init_account_balance=f"{init_account_balance:.2f}",
                    account_balance=f"{account_balance:.2f}",
                )
            else:
                dispatcher.utter_message(
                    template="utter_account_balance",
                    init_account_balance=f"{account_balance:.2f}",
                )

        events = []
        active_form_name = tracker.active_form.get("name")
        if active_form_name:
            # Trigger utter_ask_{form}_continue_form
            events.append(SlotSet("continue_form", None))

        return events


class ActionShowRecipients(Action):
    """Lists the contents of then known_recipients slot"""

    def name(self):
        """Unique identifier of the action"""
        return "action_show_recipients"

    async def run(self, dispatcher, tracker, domain):
        """Executes the custom action"""
        recipients = tracker.get_slot("known_recipients")
        formatted_recipients = "\n" + "\n".join(
            [f"- {recipient}" for recipient in recipients]
        )
        dispatcher.utter_message(
            template="utter_recipients",
            formatted_recipients=formatted_recipients,
        )

        events = []
        active_form_name = tracker.active_form.get("name")
        if active_form_name:
            # Trigger utter_ask_{form}_continue_form
            events.append(SlotSet("continue_form", None))

        return events


class ActionShowTransferCharge(Action):
    """Lists the transfer charges"""

    def name(self):
        """Unique identifier of the action"""
        return "action_show_transfer_charge"

    async def run(self, dispatcher, tracker, domain):
        """Executes the custom action"""
        dispatcher.utter_message(template="utter_transfer_charge")

        events = []
        active_form_name = tracker.active_form.get("name")
        if active_form_name:
            # Trigger utter_ask_{form}_continue_form
            events.append(SlotSet("continue_form", None))

        return events


class ActionSessionStart(Action):
    """Executes at start of session"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "action_session_start"

    @staticmethod
    def _slot_set_events_from_tracker(
        tracker: "Tracker",
    ) -> List["SlotSet"]:
        """Fetches SlotSet events from tracker and carries over keys and values"""
        return [
            SlotSet(
                key=event.get("name"),
                value=event.get("value"),
            )
            for event in tracker.events
            if event.get("event") == "slot"
        ]

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        """Executes the custom action"""
        # the session should begin with a `session_started` event
        events = [SessionStarted()]

        events.extend(self._slot_set_events_from_tracker(tracker))

        # create mock profile
        user_profile = create_mock_profile()

        # initialize slots from mock profile
        for key, value in user_profile.items():
            if value is not None:
                events.append(SlotSet(key=key, value=value))

        # an `action_listen` should be added at the end
        events.append(ActionExecuted("action_listen"))

        return events


class ActionRestart(Action):
    """Executes after restart of a session"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "action_restart"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        """Executes the custom action"""
        return [Restarted(), FollowupAction("action_session_start")]


class ActionAskTransactionSearchFormConfirm(Action):
    """Asks for the 'confirm' slot of 'transaction_search_form'

    A custom action is used instead of an 'utter_ask' response because a different
    question is asked based on 'search_type' and 'vendor_name' slots.
    """

    def name(self) -> Text:
        return "action_ask_transaction_search_form_confirm"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        """Executes the custom action"""
        search_type = tracker.get_slot("search_type")
        vendor_name = tracker.get_slot("vendor_name")
        start_time_formatted = tracker.get_slot("start_time_formatted")
        end_time_formatted = tracker.get_slot("end_time_formatted")

        if vendor_name:
            vendor_name = f" with {vendor_name}"
        else:
            vendor_name = ""

        if search_type == "spend":
            text = (
                f"Do you want to search for transactions{vendor_name} between "
                f"{start_time_formatted} and {end_time_formatted}?"
            )
        elif search_type == "deposit":
            text = (
                f"Do you want to search deposits made to your account between "
                f"{start_time_formatted} and {end_time_formatted}?"
            )

        buttons = [
            {"payload": "/affirm", "title": "Yes"},
            {"payload": "/deny", "title": "No"},
        ]

        dispatcher.utter_message(text=text, buttons=buttons)

        return []


class ActionSwitchFormsAsk(Action):
    """Asks to switch forms"""

    def name(self) -> Text:
        return "action_switch_forms_ask"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        """Executes the custom action"""
        active_form_name = tracker.active_form.get("name")
        intent_name = tracker.latest_message["intent"]["name"]
        next_form_name = NEXT_FORM_NAME.get(intent_name)

        if (
            active_form_name not in FORM_DESCRIPTION.keys()
            or next_form_name not in FORM_DESCRIPTION.keys()
        ):
            logger.debug(
                f"Cannot create text for `active_form_name={active_form_name}` & "
                f"`next_form_name={next_form_name}`"
            )
            next_form_name = None
        else:
            text = (
                f"We haven't completed the {FORM_DESCRIPTION[active_form_name]} yet. "
                f"Are you sure you want to switch to {FORM_DESCRIPTION[next_form_name]}?"
            )
            buttons = [
                {"payload": "/affirm", "title": "Yes"},
                {"payload": "/deny", "title": "No"},
            ]
            dispatcher.utter_message(text=text, buttons=buttons)

        return [SlotSet("next_form_name", next_form_name)]


class ActionSwitchFormsDeny(Action):
    """Does not switch forms"""

    def name(self) -> Text:
        return "action_switch_forms_deny"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        """Executes the custom action"""
        active_form_name = tracker.active_form.get("name")

        if active_form_name not in FORM_DESCRIPTION.keys():
            logger.debug(
                f"Cannot create text for `active_form_name={active_form_name}`."
            )
        else:
            text = f"Ok, let's continue with the {FORM_DESCRIPTION[active_form_name]}."
            dispatcher.utter_message(text=text)

        return [SlotSet("next_form_name", None)]


class ActionSwitchFormsAffirm(Action):
    """Switches forms"""

    def name(self) -> Text:
        return "action_switch_forms_affirm"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        """Executes the custom action"""
        active_form_name = tracker.active_form.get("name")
        next_form_name = tracker.get_slot("next_form_name")

        if (
            active_form_name not in FORM_DESCRIPTION.keys()
            or next_form_name not in FORM_DESCRIPTION.keys()
        ):
            logger.debug(
                f"Cannot create text for `active_form_name={active_form_name}` & "
                f"`next_form_name={next_form_name}`"
            )
        else:
            text = (
                f"Great. Let's switch from the {FORM_DESCRIPTION[active_form_name]} "
                f"to {FORM_DESCRIPTION[next_form_name]}. "
                f"Once completed, you will have the option to switch back."
            )
            dispatcher.utter_message(text=text)

        return [
            SlotSet("previous_form_name", active_form_name),
            SlotSet("next_form_name", None),
        ]


class ActionSwitchBackAsk(Action):
    """Asks to switch back to previous form"""

    def name(self) -> Text:
        return "action_switch_back_ask"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        """Executes the custom action"""
        previous_form_name = tracker.get_slot("previous_form_name")

        if previous_form_name not in FORM_DESCRIPTION.keys():
            logger.debug(
                f"Cannot create text for `previous_form_name={previous_form_name}`"
            )
            previous_form_name = None
        else:
            text = (
                f"Would you like to go back to the "
                f"{FORM_DESCRIPTION[previous_form_name]} now?."
            )
            buttons = [
                {"payload": "/affirm", "title": "Yes"},
                {"payload": "/deny", "title": "No"},
            ]
            dispatcher.utter_message(text=text, buttons=buttons)

        return [SlotSet("previous_form_name", None)]
