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


MAX_VALIDATION_FAILURES = 1


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

        if not tracker.get_slot("continue"):
            events.append(SlotSet("continue", "yes"))

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
        """Updates the slot repeated_validation_failures, and throws
        ActionExecutionRejection when the threshold is reached.

        This allows other policies to predict another action, for example, based on
        a rule or a story.
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

            # Trigger question to continue with the form or not
            rvf_events.append(SlotSet("continue", None))

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
            "continue": None,
            "credit_card": None,
            "account_type": None,
            "amount-of-money": None,
            "confirm": None,
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

    async def validate_continue(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'continue' slot"""
        if value == "yes":
            return {"continue": value}

        if value == "no":
            # This will activate rule 'Submit cc_payment_form' to cancel payment
            return {"requested_slot": None, "confirm": "no", "continue": value}

        return {"continue": None}

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
        parsedtime = parse_duckling_time(timeentity)
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
        search_type = tracker.get_slot("search_type")
        transaction_history = tracker.get_slot("transaction_history")
        transactions_subset = transaction_history.get(search_type, {})
        vendor_name = tracker.get_slot("vendor_name")

        if vendor_name:
            transactions = transactions_subset.get(vendor_name.lower())
            vendor_name = f" with {vendor_name}"
        else:
            transactions = [v for k in list(transactions_subset.values()) for v in k]
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
            template=f"utter_searching_{search_type}_transactions", **slotvars
        )
        dispatcher.utter_message(
            template=f"utter_found_{search_type}_transactions", **slotvars
        )

        return [
            SlotSet("time", None),
            SlotSet("time_formatted", None),
            SlotSet("start_time", None),
            SlotSet("end_time", None),
            SlotSet("start_time_formatted", None),
            SlotSet("end_time_formatted", None),
            SlotSet("grain", None),
            SlotSet("search_type", None),
            SlotSet("vendor_name", None),
        ]


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
        parsedinterval = parse_duckling_time_as_interval(timeentity)
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
        events = [
            SlotSet("PERSON", None),
            SlotSet("amount-of-money", None),
            SlotSet("number", None),
            SlotSet("confirm", None),
        ]

        if tracker.get_slot("confirm") == "yes":
            amount_of_money = float(tracker.get_slot("amount-of-money"))
            account_balance = float(tracker.get_slot("account_balance"))

            updated_account_balance = account_balance - amount_of_money

            dispatcher.utter_message(template="utter_transfer_complete")

            amount_transferred = float(tracker.get_slot("amount_transferred"))
            events.extend(
                [
                    SlotSet(
                        "amount_transferred",
                        amount_transferred + amount_of_money,
                    ),
                    SlotSet("account_balance", f"{updated_account_balance:.2f}"),
                ]
            )
        else:
            dispatcher.utter_message(template="utter_transfer_cancelled")

        return events


class ValidateTransferMoneyForm(MyFormValidationAction):
    """Validates Slots of the transfer_money_form"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "validate_transfer_money_form"

    async def validate_PERSON(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'PERSON' slot"""
        name = value.title() if value else None
        known_recipients = tracker.get_slot("known_recipients")
        first_names = [name.split()[0] for name in known_recipients]
        if name in known_recipients:
            return {"PERSON": name}

        if name in first_names:
            index = first_names.index(name)
            fullname = known_recipients[index]
            return {"PERSON": fullname}

        dispatcher.utter_message(template="utter_unknown_recipient")
        return {"PERSON": None}

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

        # Seting slot 'continue' to None will trigger utter_ask_{form}_continue if
        # this action was predicted while a form is active.
        return [
            SlotSet("amount-of-money", None),
            SlotSet("account_type", None),
            SlotSet("continue", None),
        ]


class ActionRecipients(Action):
    """Lists the contents of then known_recipients slot"""

    def name(self):
        """Unique identifier of the action"""
        return "action_recipients"

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
        return []


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
