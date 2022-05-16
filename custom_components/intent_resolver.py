from typing import Dict, Text, Any, List

from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.core.trackers import DialogueStateTracker
from rasa.shared.core.events import (
    UserUttered,
    ActionExecuted,
)
import logging

logger = logging.getLogger(__name__)

# TODO: Correctly register your component with its type
@DefaultV1Recipe.register(
    [DefaultV1Recipe.ComponentType.INTENT_CLASSIFIER], is_trainable=False
)
class IntentResolver(GraphComponent):
    def __init__(
        self,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> None:

        self.component_config = config
        self._model_storage = model_storage
        self._resource = resource
        self._execution_context = execution_context

        self.active_skill = None

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> GraphComponent:
        return cls(config, model_storage, resource, execution_context)

    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        """The component's default config (see parent class for full docstring)."""
        # please make sure to update the docs when changing a default parameter
        return {
            "global_router_name": "",
            "skills": {},
        }

    def process(
        self, messages: List[Message], tracker: DialogueStateTracker
    ) -> List[Message]:
        logger.debug(f"Current active skill - {self.active_skill}")

        if self.active_skill:
            # Check if a skill just got terminated in the last turn of the conversation
            for event in reversed(tracker.applied_events()):
                if isinstance(event, UserUttered):
                    break
                if isinstance(event, ActionExecuted):
                    if (
                        self.component_config["skills"]
                        .get(self.active_skill, {})
                        .get("end_action")
                        == event.action_name
                    ):
                        logger.debug(
                            f"End action {event.action_name} detected. Resetting active skill to None"
                        )
                        self.active_skill = None

        final_label, final_ranking = None, None
        for message in messages:

            query_skill = (
                self.active_skill
                if self.active_skill
                else self.component_config["global_router_name"]
            )

            # check inside the active skill's model
            final_label = message.get(query_skill, {}).get("intent")
            final_ranking = message.get(query_skill, {}).get("intent_ranking")

            message.set("intent", final_label, add_to_output=True)
            message.set("intent_ranking", final_ranking, add_to_output=True)

        logger.debug(f"Resolved label - {final_label}")

        # set an active skill if possible
        for skill, metadata in self.component_config["skills"].items():
            if final_label.get("name") == metadata.get("start_intent"):
                self.active_skill = skill
                break
        logger.debug(f"New active skill - {self.active_skill}")

        return messages
