from dateutil import relativedelta, parser
from typing import Dict, Text, Any, List, Union, Optional, Iterable
from rasa_sdk import Tracker

def close_interval_duckling_time(timeinfo: Dict[Text, Any]) -> Iterable:
    grain = timeinfo.get("to", timeinfo.get("from",{})).get("grain")
    start = timeinfo.get("to",{}).get("value")
    end = timeinfo.get("from", {}).get("value")
    if start and end:
        parsedstart = parser.isoparse(start)
        parsedend = parser.isoparse(end)

    elif start or end:    
        deltaargs = {f"{grain}s": 1}
        delta = relativedelta.relativedelta(**deltaargs)
        if start:
            parsedstart = parser.isoparse(start)
            parsedend = parsedstart + delta
        elif end:
            parsedend = parser.isoparse(end)
            parsedstart = parsedend - delta
        
    else:
        parsedstart = None
        parsedend = None

    return parsedstart, parsedend, grain


def make_interval_from_value_duckling_time(timeinfo: Dict[Text, Any]) -> Iterable:
    grain = timeinfo.get("grain")
    start = timeinfo.get("value")
    parsedstart = parser.isoparse(start)
    deltaargs = {f"{grain}s": 1}
    delta = relativedelta.relativedelta(**deltaargs)
    parsedend = parsedstart + delta
    return parsedstart, parsedend, grain

def parse_duckling_time_as_interval(timeentity: Dict[Text, Any]) -> Optional[Iterable]:
    timeinfo = timeentity.get("additional_info",{})
    if timeinfo.get("type") == "interval":
        return close_interval_duckling_time(timeinfo)
    elif timeinfo.get("type") == "value":
        return make_interval_from_value_duckling_time(timeinfo)

def format_time_by_grain(time, grain):
    grain_format = {
        "second": "%I:%M:%S%p, %A %b %d, %Y",
        "day": "%A %b %d, %Y",
        "week": "%A %b %d, %Y",
        "month": "%b %Y",
        "year": "%Y"
    }
    timeformat = grain_format.get(grain,"%I:%M%p, %A %b %d, %Y")
    return time.strftime(timeformat)

def parse_duckling_time(timeentity: Dict[Text, Any]) -> Optional[Iterable]:
    timeinfo = timeentity.get("additional_info",{})
    if timeinfo.get("type") == "value":
        value = timeinfo.get("value")
        grain = timeinfo.get("grain")
        return parser.isoparse(value), grain

def get_entity_details(tracker: Tracker, entity_type: Text) -> Optional[Dict[Text, Any]]:
        all_entities = tracker.latest_message.get("entities", [])
        entities = [e for e in all_entities if e.get("entity") == entity_type]
        if entities:
            return entities[0]