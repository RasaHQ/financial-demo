"""Customization to deal nicely with repeated slot validation failures."""
import abc
from typing import Dict, Text, Any, List
import logging
import pathlib
import ruamel.yaml
from rasa_sdk import utils
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.events import (
    SlotSet,
    EventType,
    LoopInterrupted,
    ActionExecutionRejected,
)
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher


logger = logging.getLogger(__name__)

# these slots are used to store information needed to nicely deal with
# repeated slot validation failures
RVF_SLOT = "repeated_validation_failures"
CF_SLOT = "AA_CONTINUE_FORM"


here = pathlib.Path(__file__).parent.absolute()
custom_forms_config = (
    ruamel.yaml.safe_load(open(f"{here}/custom_forms_config.yml", "r")) or {}
).get("custom_forms", {})

MAX_VALIDATION_FAILURES = custom_forms_config.get("max_validation_failures", 2)


class CustomFormValidationAction(FormValidationAction, metaclass=abc.ABCMeta):
    """Validates if slot values are valid and handles repeated validation failures.

    To use, you add the following to your bot:

    (-) Include these two intents:
        - affirm
        - deny

    (-) In domain.yml define these slots:

        slots:
          repeated_validation_failures:
            type: any
          AA_CONTINUE_FORM:
            type: any

    (-) In domain.yml, for each form, declare 'AA_CONTINUE_FORM' as first required slot.

        For example:

        forms:
          cc_payment_form:
            AA_CONTINUE_FORM:
            - type: from_intent
              intent: affirm
              value: yes
            - type: from_intent
              intent: deny
              value: no
            - type: from_text
              intent:
              - inform
              - cc_payment_form

    (-) In domain.yml, for each form, define the 'utter_{form}_AA_CONTINUE_FORM' response,
        using /affirm & /deny buttons.

        For example:

        utter_ask_cc_payment_form_AA_CONTINUE_FORM:
        - buttons:
          - payload: /affirm
            title: Yes
          - payload: /deny
            title: No, cancel the transaction
          text: Would you like to continue scheduling the credit card payment?

    (-) In the custom action Class that validates slots, subclass from
        'CustomFormValidationAction' instead of from 'FormValidationAction'.
        Optionally, add an 'explain_{slot}' method for every slot that the bot
        should explain in some detail if the user is repeatedly provides answer that
        cannot be validated.

        For example:

        class ValidatePayCCForm(CustomFormValidationAction):
            async def explain_credit_card(
                self,
                value: Text,
                dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any],
            ) -> Dict[Text, Any]:

                # Bot utters a message that explains the slot
                dispatcher.utter_message(   )

                # optionally, you can set slots by returning a dict
                return {}
    """

    # Avoids registering this class as a custom action
    @abc.abstractmethod
    def name(self) -> Text:
        """Unique identifier of the CustomFormValidationAction"""

        raise NotImplementedError("A CustomFormValidationAction must implement a name")

    async def validate(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> List[EventType]:
        """Validates slots by calling a validation function for each slot.

        Calls an explain function for the requested slot when validation fails
        MAX_VALIDATION_FAILURES in a row, and sets 'AA_CONTINUE_FORM' slot to None, which
        triggers the bot to utter the 'utter_ask_{form}_AA_CONTINUE_FORM' template.

        Args:
            dispatcher: the dispatcher which is used to send messages back to the user.
            tracker: the conversation tracker for the current user.
            domain: the bot's domain.
        Returns:
            `SlotSet` events for every validated slot.
        """
        events = []

        if not tracker.get_slot(CF_SLOT):
            events.append(SlotSet(CF_SLOT, "yes"))

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
        `AA_CONTINUE_FORM` to None when the threshold is reached.

        This will trigger utter_ask_{form}_AA_CONTINUE_FORM, asking the user if they want
        to continue with this form or not.
        """
        rvf_events: List[EventType] = []
        requested_slot = tracker.get_slot("requested_slot")

        # Only do this while form is asking for a certain slot
        if not requested_slot:
            return rvf_events

        # if the requested slot was not extracted, interupt the form
        interrupt_form = False
        if not events:
            interrupt_form = True
        else:
            for event in events:
                if event["event"] == "slot" and event["name"] == "requested_slot":
                    interrupt_form = True

        if interrupt_form:
            # Sending LoopInterrupted will prevent rasa.core from asking for the slot
            rvf_events.append(LoopInterrupted(is_interrupted=True))

            # Sending ActionExecutionRejected will allow rasa.core to predict
            # something else before continuing with the form
            rvf_events.append(ActionExecutionRejected(action_name=self.form_name()))

            return rvf_events

        # Skip if validate_{slot} turned off the form by setting requested_slot to None
        for event in events:
            if (
                event["event"] == "slot"
                and event["name"] == "requested_slot"
                and not event["value"]
            ):
                rvf_events.append(SlotSet(RVF_SLOT, 0))
                return rvf_events

        rvf = tracker.get_slot(RVF_SLOT)
        if rvf:
            rvf = int(rvf)
        else:
            # initialize counter to 0
            rvf = 0

        # check if validation of the requested_slot failed
        validation_failed = True
        for event in events:
            if (
                event["event"] == "slot"
                and event["name"] == requested_slot
                and event["value"]
            ):
                validation_failed = False
                break

        # keep track of repeated validation failures
        if validation_failed:
            rvf += 1
        else:
            rvf = 0

        if rvf >= MAX_VALIDATION_FAILURES:
            rvf_events.extend(
                await self.explain_requested_slot(dispatcher, tracker, domain)
            )
            # reset counter
            rvf = 0

            # Triggers 'utter_ask_{form}_AA_CONTINUE_FORM'
            rvf_events.append(SlotSet(CF_SLOT, None))

        rvf_events.append(SlotSet(RVF_SLOT, rvf))
        return rvf_events

    async def explain_requested_slot(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
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

        method_name = f"explain_{slot_name.replace('-','_')}"
        explain_method = getattr(self, method_name, None)

        if not explain_method:
            logger.debug(
                f"Skipping explanation for `{slot_name}`: there is no explanation "
                "method specified."
            )
            return []

        slots = {}
        explanation_output = await utils.call_potential_coroutine(
            explain_method(slot_value, dispatcher, tracker, domain)
        )

        if explanation_output:
            slots.update(explanation_output)

        return [SlotSet(slot, value) for slot, value in slots.items()]

    async def validate_AA_CONTINUE_FORM(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'AA_CONTINUE_FORM' slot"""
        if value == "yes":
            return {CF_SLOT: value}

        if value == "no":
            # This will activate rule 'Submit ---_form' to cancel the operation
            return {
                "requested_slot": None,
                "zz_confirm_form": "no",
                CF_SLOT: value,
            }

        # The user's answer was not valid. Just re-set it to None.
        return {CF_SLOT: None}
