import json
import pytest

from rasa_sdk.executor import CollectingDispatcher, Tracker
from rasa_sdk.events import SlotSet, ActionExecuted, Restarted

from tests.conftest import EMPTY_TRACKER
from actions import actions


def test_run_action_session_start(dispatcher, domain, session):
    tracker = EMPTY_TRACKER
    action = actions.ActionSessionStart()
    events = action.run(dispatcher, tracker, domain)
    expected_events = [SlotSet("currency", currency), ActionExecuted("action_listen")]
    assert events == expected_events
