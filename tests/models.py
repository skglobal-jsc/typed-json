from typing import Any, Dict, List, Optional, Tuple, NamedTuple, Iterable, TypeVar
from datetime import datetime

from typing_extensions import TypedDict

from typed_json import register_converter

class CountingModel(NamedTuple):
    count: int
    childs: Optional[Dict[str, 'CountingModel']] = None

class CountingDict(TypedDict):
    count: int
    childs: Optional[Dict[str, 'CountingDict']]

Range = TypedDict('Range', {
    'from': int,
    'to': int
})

class DataModel(NamedTuple):
    string: str
    list_str: List[str]
    num: int
    list_num: List[float]
    data3d: List[List[int]]
    range_num: Optional[Range]
    counting: Dict[str, CountingModel]


class ISODateTime(datetime):
    def __new__(cls, dt:datetime):
        return super().__new__(cls, dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond, dt.tzinfo)

class MilliSecondsEpochDateTime(datetime):
    def __new__(cls, dt:datetime):
        return super().__new__(cls, dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond, dt.tzinfo)

class MicroSecondsEpochDateTime(datetime):
    def __new__(cls, dt:datetime):
        return super().__new__(cls, dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond, dt.tzinfo)

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
        return True, ISODateTime(datetime.fromisoformat(val))
    elif cls is MilliSecondsEpochDateTime and isinstance(val, int):
        return True, MilliSecondsEpochDateTime(datetime.fromtimestamp(val / 1000))
    elif cls is MicroSecondsEpochDateTime and isinstance(val, int):
        return True, MicroSecondsEpochDateTime(datetime.fromtimestamp(val / 1000000))
    else:
        return False, None

register_converter(_datetime_typed, _datetime_json)

T = TypeVar('T')
class GenericModel(NamedTuple):
    ite: Iterable[T]
