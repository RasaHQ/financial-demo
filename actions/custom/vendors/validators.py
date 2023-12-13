from typing import Dict, Text, Any

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions.actions import profile_db


class ValidateVendorForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_add_vendor_form"

    async def validate_vendor(
        self,
        vendor_name: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        available_vendors = profile_db.get_vendors()
        print(available_vendors)

        if vendor_name in available_vendors:
            dispatcher.utter_message(f"Such vendor already exists: {vendor_name}")
            return {"vendor": None}

        return {"vendor": vendor_name}
