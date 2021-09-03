"""Custom actions"""
import os
from typing import Dict, Text, Any, List
import logging
from dateutil import parser
import sqlalchemy as sa

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

from actions.profile_db import create_database, ProfileDB

from actions.custom_forms import CustomFormValidationAction


logger = logging.getLogger(__name__)

# The profile database is created/connected to when the action server starts
# It is populated the first time `ActionSessionStart.run()` is called .

PROFILE_DB_NAME = os.environ.get("PROFILE_DB_NAME", "profile")
PROFILE_DB_URL = os.environ.get("PROFILE_DB_URL", f"sqlite:///{PROFILE_DB_NAME}.db")
ENGINE = sa.create_engine(PROFILE_DB_URL)
create_database(ENGINE, PROFILE_DB_NAME)

profile_db = ProfileDB(ENGINE)

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
            "AA_CONTINUE_FORM": None,
            "zz_confirm_form": None,
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

        if tracker.get_slot("zz_confirm_form") == "yes":
            credit_card = tracker.get_slot("credit_card")
            amount_of_money = float(tracker.get_slot("amount-of-money"))
            amount_transferred = float(tracker.get_slot("amount_transferred"))
            profile_db.pay_off_credit_card(
                tracker.sender_id, credit_card, amount_of_money
            )

            dispatcher.utter_message(response="utter_cc_pay_scheduled")

            slots["amount_transferred"] = amount_transferred + amount_of_money
        else:
            dispatcher.utter_message(response="utter_cc_pay_cancelled")

        return [SlotSet(slot, value) for slot, value in slots.items()]


class ValidatePayCCForm(CustomFormValidationAction):
    """Validates Slots of the cc_payment_form"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "validate_cc_payment_form"

    def amount_from_balance(
        self, dispatcher, tracker, credit_card_name, balance_type
    ) -> Dict[Text, Any]:
        amount_balance = profile_db.get_credit_card_balance(
            tracker.sender_id, credit_card_name, balance_type
        )
        account_balance = profile_db.get_account_balance(tracker.sender_id)
        if account_balance < float(amount_balance):
            dispatcher.utter_message(response="utter_insufficient_funds")
            return {"amount-of-money": None}
        return {
            "amount-of-money": f"{amount_balance:.2f}",
            "payment_amount_type": f"(your {balance_type})",
        }

    async def validate_amount_of_money(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'amount-of-money' slot"""
        if not value:
            return {"amount-of-money": None}

        account_balance = profile_db.get_account_balance(tracker.sender_id)
        # check if user asked to pay the full or the minimum balance
        if type(value) is str:
            credit_card_name = tracker.get_slot("credit_card")
            if credit_card_name:
                credit_card = profile_db.get_credit_card(
                    tracker.sender_id, credit_card_name
                )
            else:
                credit_card = None
            balance_types = profile_db.list_balance_types()
            if value and value.lower() in balance_types:
                balance_type = value.lower()
                if not credit_card:
                    dispatcher.utter_message(
                        f"I see you'd like to pay the {balance_type}."
                    )
                    return {"amount-of-money": balance_type}
                slots_to_set = self.amount_from_balance(
                    dispatcher, tracker, credit_card_name, balance_type
                )
                if float(slots_to_set.get("amount-of-money")) == 0:
                    dispatcher.utter_message(
                        response="utter_nothing_due", **slots_to_set
                    )
                    return {
                        "amount-of-money": None,
                        "credit_card": None,
                        "payment_amount_type": None,
                    }
                return slots_to_set

        try:
            entity = get_entity_details(
                tracker, "amount-of-money"
            ) or get_entity_details(tracker, "number")
            amount_currency = parse_duckling_currency(entity)
            if not amount_currency:
                raise TypeError
            if account_balance < float(amount_currency.get("amount-of-money")):
                dispatcher.utter_message(response="utter_insufficient_funds")
                return {"amount-of-money": None}
            return amount_currency
        except (TypeError, AttributeError):
            pass

        dispatcher.utter_message(response="utter_no_payment_amount")
        return {"amount-of-money": None}

    async def validate_credit_card(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'credit_card' slot"""
        if value and value.lower() in profile_db.list_credit_cards(tracker.sender_id):
            amount = tracker.get_slot("amount-of-money")
            credit_card_slot = {"credit_card": value.title()}
            balance_types = profile_db.list_balance_types()
            if amount and amount.lower() in balance_types:
                updated_amount = self.amount_from_balance(
                    dispatcher, tracker, value.lower(), amount
                )
                if float(updated_amount.get("amount-of-money")) == 0:
                    dispatcher.utter_message(
                        response="utter_nothing_due", **updated_amount
                    )
                    return {
                        "amount-of-money": None,
                        "credit_card": None,
                        "payment_amount_type": None,
                    }
                account_balance = profile_db.get_account_balance(tracker.sender_id)
                if account_balance < float(updated_amount.get("amount-of-money")):
                    dispatcher.utter_message(
                        response="utter_insufficient_funds_specific", **updated_amount
                    )
                    return {"amount-of-money": None}
                return {**credit_card_slot, **updated_amount}
            return credit_card_slot

        dispatcher.utter_message(response="utter_no_creditcard")
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
        for credit_card in profile_db.list_credit_cards(tracker.sender_id):
            current_balance = profile_db.get_credit_card_balance(
                tracker.sender_id, credit_card
            )
            dispatcher.utter_message(
                response="utter_credit_card_balance",
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
            dispatcher.utter_message(response="utter_no_transactdate")
            return {"time": None}
        return parsedtime

    async def validate_zz_confirm_form(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'zz_confirm_form' slot"""
        if value in ["yes", "no"]:
            return {"zz_confirm_form": value}

        return {"zz_confirm_form": None}


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
            "AA_CONTINUE_FORM": None,
            "zz_confirm_form": None,
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

        if tracker.get_slot("zz_confirm_form") == "yes":
            search_type = tracker.get_slot("search_type")
            deposit = search_type == "deposit"
            vendor = tracker.get_slot("vendor_name")
            vendor_name = f" at {vendor.title()}" if vendor else ""
            start_time = parser.isoparse(tracker.get_slot("start_time"))
            end_time = parser.isoparse(tracker.get_slot("end_time"))
            transactions = profile_db.search_transactions(
                tracker.sender_id,
                start_time=start_time,
                end_time=end_time,
                deposit=deposit,
                vendor=vendor,
            )

            aliased_transactions = transactions.subquery()
            total = profile_db.session.query(
                sa.func.sum(aliased_transactions.c.amount)
            )[0][0]
            if not total:
                total = 0
            numtransacts = transactions.count()
            slotvars = {
                "total": f"{total:.2f}",
                "numtransacts": numtransacts,
                "start_time_formatted": tracker.get_slot("start_time_formatted"),
                "end_time_formatted": tracker.get_slot("end_time_formatted"),
                "vendor_name": vendor_name,
            }

            dispatcher.utter_message(
                response=f"utter_searching_{search_type}_transactions",
                **slotvars,
            )
            dispatcher.utter_message(
                response=f"utter_found_{search_type}_transactions", **slotvars
            )
        else:
            dispatcher.utter_message(response="utter_transaction_search_cancelled")

        return [SlotSet(slot, value) for slot, value in slots.items()]


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
        if value and value.lower() in profile_db.list_vendors():
            return {"vendor_name": value}

        dispatcher.utter_message(response="utter_no_vendor_name")
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
            dispatcher.utter_message(response="utter_no_transactdate")
            return {"time": None}

        return parsedinterval


class ActionTransferMoney(Action):
    """Transfers Money."""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "action_transfer_money"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        """Executes the action"""
        slots = {
            "AA_CONTINUE_FORM": None,
            "zz_confirm_form": None,
            "PERSON": None,
            "amount-of-money": None,
            "number": None,
        }

        if tracker.get_slot("zz_confirm_form") == "yes":
            amount_of_money = float(tracker.get_slot("amount-of-money"))
            from_account_number = profile_db.get_account_number(
                profile_db.get_account_from_session_id(tracker.sender_id)
            )
            to_account_number = profile_db.get_account_number(
                profile_db.get_recipient_from_name(
                    tracker.sender_id, tracker.get_slot("PERSON")
                )
            )
            profile_db.transact(
                from_account_number,
                to_account_number,
                amount_of_money,
            )

            dispatcher.utter_message(response="utter_transfer_complete")

            amount_transferred = float(tracker.get_slot("amount_transferred"))
            slots["amount_transferred"] = amount_transferred + amount_of_money
        else:
            dispatcher.utter_message(response="utter_transfer_cancelled")

        return [SlotSet(slot, value) for slot, value in slots.items()]


class ValidateTransferMoneyForm(CustomFormValidationAction):
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
        # It is possible that both Spacy & DIET extracted the PERSON
        # Just pick the first one
        if isinstance(value, list):
            value = value[0]

        name = value.lower() if value else None
        known_recipients = profile_db.list_known_recipients(tracker.sender_id)
        first_names = [name.split()[0] for name in known_recipients]
        if name is not None and name in known_recipients:
            return {"PERSON": name.title()}

        if name in first_names:
            index = first_names.index(name)
            fullname = known_recipients[index]
            return {"PERSON": fullname.title()}

        dispatcher.utter_message(response="utter_unknown_recipient", PERSON=value)
        return {"PERSON": None}

    async def explain_PERSON(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Explains 'PERSON' slot"""
        recipients = profile_db.list_known_recipients(tracker.sender_id)
        formatted_recipients = "\n" + "\n".join(
            [f"- {recipient.title()}" for recipient in recipients]
        )
        dispatcher.utter_message(
            response="utter_recipients",
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
        account_balance = profile_db.get_account_balance(tracker.sender_id)
        try:
            entity = get_entity_details(
                tracker, "amount-of-money"
            ) or get_entity_details(tracker, "number")
            amount_currency = parse_duckling_currency(entity)
            if not amount_currency:
                raise TypeError
            if account_balance < float(amount_currency.get("amount-of-money")):
                dispatcher.utter_message(response="utter_insufficient_funds")
                return {"amount-of-money": None}
            return amount_currency
        except (TypeError, AttributeError):
            dispatcher.utter_message(response="utter_no_payment_amount")
            return {"amount-of-money": None}

    async def validate_zz_confirm_form(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'zz_confirm_form' slot"""
        if value in ["yes", "no"]:
            return {"zz_confirm_form": value}

        return {"zz_confirm_form": None}


class ActionShowBalance(Action):
    """Shows the balance of bank or credit card accounts"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "action_show_balance"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        """Executes the custom action"""
        account_type = tracker.get_slot("account_type")

        if account_type == "credit":
            # show credit card balance
            credit_card = tracker.get_slot("credit_card")
            available_cards = profile_db.list_credit_cards(tracker.sender_id)

            if credit_card and credit_card.lower() in available_cards:
                current_balance = profile_db.get_credit_card_balance(
                    tracker.sender_id, credit_card
                )
                dispatcher.utter_message(
                    response="utter_credit_card_balance",
                    **{
                        "credit_card": credit_card.title(),
                        "credit_card_balance": f"{current_balance:.2f}",
                    },
                )
            else:
                for credit_card in profile_db.list_credit_cards(tracker.sender_id):
                    current_balance = profile_db.get_credit_card_balance(
                        tracker.sender_id, credit_card
                    )
                    dispatcher.utter_message(
                        response="utter_credit_card_balance",
                        **{
                            "credit_card": credit_card.title(),
                            "credit_card_balance": f"{current_balance:.2f}",
                        },
                    )
        else:
            # show bank account balance
            account_balance = profile_db.get_account_balance(tracker.sender_id)
            amount = tracker.get_slot("amount_transferred")
            if amount:
                amount = float(tracker.get_slot("amount_transferred"))
                init_account_balance = account_balance + amount
                dispatcher.utter_message(
                    response="utter_changed_account_balance",
                    init_account_balance=f"{init_account_balance:.2f}",
                    account_balance=f"{account_balance:.2f}",
                )
            else:
                dispatcher.utter_message(
                    response="utter_account_balance",
                    init_account_balance=f"{account_balance:.2f}",
                )

        events = []
        active_form_name = tracker.active_form.get("name")
        if active_form_name:
            # keep the tracker clean for the predictions with form switch stories
            events.append(UserUtteranceReverted())
            # trigger utter_ask_{form}_AA_CONTINUE_FORM, by making it the requested_slot
            events.append(SlotSet("AA_CONTINUE_FORM", None))
            # avoid that bot goes in listen mode after UserUtteranceReverted
            events.append(FollowupAction(active_form_name))

        return events


class ActionShowRecipients(Action):
    """Lists the contents of then known_recipients slot"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "action_show_recipients"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        """Executes the custom action"""
        recipients = profile_db.list_known_recipients(tracker.sender_id)
        formatted_recipients = "\n" + "\n".join(
            [f"- {recipient.title()}" for recipient in recipients]
        )
        dispatcher.utter_message(
            response="utter_recipients",
            formatted_recipients=formatted_recipients,
        )

        events = []
        active_form_name = tracker.active_form.get("name")
        if active_form_name:
            # keep the tracker clean for the predictions with form switch stories
            events.append(UserUtteranceReverted())
            # trigger utter_ask_{form}_AA_CONTINUE_FORM, by making it the requested_slot
            events.append(SlotSet("AA_CONTINUE_FORM", None))
            # # avoid that bot goes in listen mode after UserUtteranceReverted
            events.append(FollowupAction(active_form_name))

        return events


class ActionShowTransferCharge(Action):
    """Lists the transfer charges"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "action_show_transfer_charge"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        """Executes the custom action"""
        dispatcher.utter_message(response="utter_transfer_charge")

        events = []
        active_form_name = tracker.active_form.get("name")
        if active_form_name:
            # keep the tracker clean for the predictions with form switch stories
            events.append(UserUtteranceReverted())
            # trigger utter_ask_{form}_AA_CONTINUE_FORM, by making it the requested_slot
            events.append(SlotSet("AA_CONTINUE_FORM", None))
            # # avoid that bot goes in listen mode after UserUtteranceReverted
            events.append(FollowupAction(active_form_name))

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

        # when restarting most slots should be reset
        relevant_slots = ["currency"]

        return [
            SlotSet(
                key=event.get("name"),
                value=event.get("value"),
            )
            for event in tracker.events
            if event.get("event") == "slot" and event.get("name") in relevant_slots
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

        # create a mock profile by populating database with values specific to tracker.sender_id
        profile_db.populate_profile_db(tracker.sender_id)
        currency = profile_db.get_currency(tracker.sender_id)

        # initialize slots from mock profile
        events.append(SlotSet("currency", currency))

        # add `action_listen` at the end
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
    """Asks for the 'zz_confirm_form' slot of 'transaction_search_form'

    A custom action is used instead of an 'utter_ask' response because a different
    question is asked based on 'search_type' and 'vendor_name' slots.
    """

    def name(self) -> Text:
        return "action_ask_transaction_search_form_zz_confirm_form"

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
