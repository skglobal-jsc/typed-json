# Typed Json

Convert json to typed python model

```python
>>> from typing import Optional, Dict, NamedTuple
>>> from typed_json import typed_from_json
>>> class CountingModel(NamedTuple):
...     count: int
...     childs: Optional[Dict[str, 'CountingModel']] = None
... 
>>> json = {
...     'count': 5,
...     'childs': {
...         'abc': {
...             'count': 2,
...         },
...         'qwe': {
...             'count': 6,
...             'childs': { 'ert': { 'count': 5 } }
...         }
...     }
... }
>>> typed_from_json(CountingModel, json)
CountingModel(count=5, childs={'abc': CountingModel(count=2, childs=None), 'qwe': CountingModel(count=6, childs={'ert': CountingModel(count=5, childs=None)})})
```

## Supported types

`typed_json` support most of standard types in python:

 * Basic python types (int, str, bool, float, NoneType)
 * NamedTuple
 * Enum
 * Optional[T]
 * List[T]
 * Dict[T1, T2]
 * Union[T1, T2, ...]
 * dataclass (requires Python 3.7)
 * TypedDict (requires Python 3.8)
 <!-- * Literal (requires Python 3.8) -->

## Add custom converter

Example for datetime:

- Create converter

```python
from typing import Any, Tuple, NamedTuple
from datetime import datetime
from typed_json import register_converter

class ISODateTime(datetime):
    def __new__(cls, iso_str:str):
        dt = datetime.fromisoformat(iso_str)
        return super().__new__(cls, dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond, dt.tzinfo)
class MilliSecondsEpochDateTime(datetime):
    def __new__(cls, milisec:int):
        dt = datetime.fromtimestamp(milisec / 1000)
        return super().__new__(cls, dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond, dt.tzinfo)
class MicroSecondsEpochDateTime(datetime):
    def __new__(cls, microsec:int):
        dt = datetime.fromtimestamp(microsec / 1000000)
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
        return True, ISODateTime(val)
    elif cls is MilliSecondsEpochDateTime and isinstance(val, int):
        return True, MilliSecondsEpochDateTime(val)
    elif cls is MicroSecondsEpochDateTime and isinstance(val, int):
        return True, MicroSecondsEpochDateTime(val)
    else:
        return False, None

register_converter(_datetime_typed, _datetime_json)

```

- Test

```python
>>> json = {
...    'iso': '2020-01-15T17:57:35.171859'),
...    'mili' : 1579085855171,
...    'micro' : 1579085855171859,
... }
>>> data = typed_from_json(TimeData, json)
>>> data
TimeData(iso=ISODateTime(2020, 1, 15, 17, 57, 35, 171859), mili=MilliSecondsEpochDateTime(2020, 1, 15, 17, 57, 35, 171000), micro=MicroSecondsEpochDateTime(2020, 1, 15, 17, 57, 35, 171859))
>>> typed_to_json(data)
{'iso': '2020-01-15T17:57:35.171859', 'mili': 1579085855171, 'micro': 1579085855171859}
```

## Copyright Notice

Copyright (C) Spring Knowledge Global,.JSC. All rights reserved.

Licensed under the [MIT](/LICENSE) license (see the LICENSE file).