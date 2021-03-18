import json
import pytest

from rasa_sdk.executor import CollectingDispatcher, Tracker
from rasa_sdk.events import SlotSet, ActionExecuted, SessionStarted

from tests.conftest import EMPTY_TRACKER, PAY_CC_CONFIRMED, PAY_CC_NOT_CONFIRMED
from actions import actions


@pytest.mark.asyncio
async def test_run_action_session_start(dispatcher, domain):
    tracker = EMPTY_TRACKER
    action = actions.ActionSessionStart()
    events = await action.run(dispatcher, tracker, domain)
    expected_events = [
        SessionStarted(),
        SlotSet("currency", "$"),
        ActionExecuted("action_listen"),
    ]
    assert events == expected_events


async def test_action_pay_cc_not_confirmed(dispatcher, domain):
    tracker = PAY_CC_NOT_CONFIRMED
    action = actions.ActionPayCC()
    events = await action.run(dispatcher, tracker, domain)
    expected_events = [
        SlotSet("AA_CONTINUE_FORM", None),
        SlotSet("zz_confirm_form", None),
        SlotSet("credit_card", None),
        SlotSet("account_type", None),
        SlotSet("amount-of-money", None),
        SlotSet("time", None),
        SlotSet("time_formatted", None),
        SlotSet("start_time", None),
        SlotSet("end_time", None),
        SlotSet("start_time_formatted", None),
        SlotSet("end_time_formatted", None),
        SlotSet("grain", None),
        SlotSet("number", None),
    ]
    expected_response = "utter_cc_pay_cancelled"
    assert events == expected_events
    assert dispatcher.messages[0]["response"] == expected_response


async def test_action_pay_cc_confirmed(dispatcher, domain):
    tracker = EMPTY_TRACKER
    action = actions.ActionSessionStart()
    await action.run(dispatcher, tracker, domain)
    tracker = PAY_CC_CONFIRMED
    action = actions.ActionPayCC()
    events = await action.run(dispatcher, tracker, domain)
    expected_events = [
        SlotSet("AA_CONTINUE_FORM", None),
        SlotSet("zz_confirm_form", None),
        SlotSet("credit_card", None),
        SlotSet("account_type", None),
        SlotSet("amount-of-money", None),
        SlotSet("time", None),
        SlotSet("time_formatted", None),
        SlotSet("start_time", None),
        SlotSet("end_time", None),
        SlotSet("start_time_formatted", None),
        SlotSet("end_time_formatted", None),
        SlotSet("grain", None),
        SlotSet("number", None),
        SlotSet("amount_transferred", value=602.65),
    ]
    expected_response = "utter_cc_pay_scheduled"
    assert events == expected_events
    assert dispatcher.messages[0]["response"] == expected_response
