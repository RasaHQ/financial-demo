import json
import pytest

from rasa_sdk.executor import CollectingDispatcher, Tracker
from rasa_sdk.events import SlotSet, ActionExecuted, SessionStarted

from tests.conftest import EMPTY_TRACKER
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
