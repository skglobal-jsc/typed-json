from datetime import datetime
from typing import NamedTuple, Tuple, Any

from typed_json import register_converter, typed_from_json, typed_to_json

class ISODateTime(datetime):
    def __new__(cls, iso_str:str):
        dt = datetime.fromisoformat(iso_str)
        return super().__new__(cls, dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond, dt.tzinfo) # type: ignore
class MilliSecondsEpochDateTime(datetime):
    def __new__(cls, milisec:int):
        dt = datetime.fromtimestamp(milisec / 1000)
        return super().__new__(cls, dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond, dt.tzinfo) # type: ignore
class MicroSecondsEpochDateTime(datetime):
    def __new__(cls, microsec:int):
        dt = datetime.fromtimestamp(microsec / 1000000)
        return super().__new__(cls, dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond, dt.tzinfo) # type: ignore
class TimeData(NamedTuple):
    iso: ISODateTime
    mili: MilliSecondsEpochDateTime
    micro: MicroSecondsEpochDateTime

def _datetime_json(val: datetime) -> Tuple[bool, Any]:
    if isinstance(val, ISODateTime):
        return True, val.isoformat()
    elif isinstance(val, MilliSecondsEpochDateTime):
        return True, int(val.timestamp() * 1000)
    elif isinstance(val, MicroSecondsEpochDateTime):
        return True, int(val.timestamp() * 1000000)
    else:
        return False, None
def _datetime_typed(cls, val):
    if cls is ISODateTime and isinstance(val, str):
        return True, ISODateTime(val) # type: ignore
    elif cls is MilliSecondsEpochDateTime and isinstance(val, int):
        return True, MilliSecondsEpochDateTime(val) # type: ignore
    elif cls is MicroSecondsEpochDateTime and isinstance(val, int):
        return True, MicroSecondsEpochDateTime(val) # type: ignore
    else:
        return False, None

register_converter(_datetime_typed, _datetime_json)

def test_TimeData():
    now = datetime.now()
    json = {
        'iso': now.isoformat(),
        'mili' : int(now.timestamp()*1000),
        'micro' : int(now.timestamp()*1000000),
    }
    model = TimeData(
        iso=ISODateTime(now.isoformat()), # type: ignore
        mili=MilliSecondsEpochDateTime(int(now.timestamp()*1000)), # type: ignore
        micro=MicroSecondsEpochDateTime(int(now.timestamp()*1000000)), # type: ignore
    )

    v = typed_from_json(TimeData, json)
    assert v == model

    assert typed_to_json(v) == json
