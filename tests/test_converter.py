import sys
from typing import Dict, List, Optional, NamedTuple, Union
from enum import Enum

if sys.version_info >= (3, 7):
    from dataclasses import dataclass

import pytest
from typed_json import typed_from_json, typed_to_json

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

class CountingModel(NamedTuple):
    count: int
    childs: Optional[Dict[str, 'CountingModel']] = None
    total: Optional[int] = 0

class CountingDict(TypedDict):
    count: int
    childs: Optional[Dict[str, 'CountingDict']]

if sys.version_info >= (3, 7):
    @dataclass()
    class CountingDataClass:
        count: int
        childs: Optional[Dict[str, 'CountingDataClass']] = None
        total: Optional[int] = 0

Range = TypedDict('Range', {
    'from': int,
    'to': int
})

class State(Enum):
    ok = 'ok'
    error = 'error'

class DataModel(NamedTuple):
    state: State
    string: str
    list_str: List[str]
    num: int
    list_num: List[float]
    data3d: List[List[int]]
    range_num: Optional[Range]
    counting: Dict[str, CountingDict]
    union_data: List[Union[int, str, Range]]


def test_CountingModel():
    json = {
        'count': 5,
        'childs': {
            'abc': {
                'count': 2,
            },
            'qwe': {
                'count': 6,
                'childs': { 'ert': { 'count': 5 } }
            }
        }
    }
    model = CountingModel(
        count=5,
        childs={
            'abc': CountingModel(count=2),
            'qwe': CountingModel(count=6, childs={ 'ert': CountingModel(count=5) } )
        }
    )
    v = typed_from_json(CountingModel, json)
    assert v == model

    json['total'] = 0
    json['childs']['abc']['childs'] = None
    json['childs']['abc']['total'] = 0
    json['childs']['qwe']['total'] = 0
    json['childs']['qwe']['childs']['ert']['childs'] = None
    json['childs']['qwe']['childs']['ert']['total'] = 0
    assert typed_to_json(v) == json

def test_CountingDict():
    json = {
        'count': 5,
        'childs': {
            'abc': {
                'count': 2,
            },
            'qwe': {
                'count': 6,
                'childs': { 'ert': { 'count': 5 } }
            }
        }
    }
    model = CountingDict(
        count=5,
        childs={
            'abc': CountingDict(count=2, childs=None),
            'qwe': CountingDict(count=6, childs={ 'ert': CountingDict(count=5, childs=None) } )
        }
    )
    v = typed_from_json(CountingDict, json)
    assert v == model

    json['childs']['abc']['childs'] = None
    json['childs']['qwe']['childs']['ert']['childs'] = None
    assert typed_to_json(v) == json

if sys.version_info >= (3, 7):
    def test_CountingDataClass():
        json = {
            'count': 5,
            'childs': {
                'abc': {
                    'count': 2,
                },
                'qwe': {
                    'count': 6,
                    'childs': { 'ert': { 'count': 5 } }
                }
            }
        }
        model = CountingDataClass(
            count=5,
            childs={
                'abc': CountingDataClass(count=2),
                'qwe': CountingDataClass(count=6, childs={ 'ert': CountingDataClass(count=5) } )
            }
        )
        v = typed_from_json(CountingDataClass, json)
        assert v == model

        json['total'] = 0
        json['childs']['abc']['childs'] = None
        json['childs']['abc']['total'] = 0
        json['childs']['qwe']['total'] = 0
        json['childs']['qwe']['childs']['ert']['childs'] = None
        json['childs']['qwe']['childs']['ert']['total'] = 0
        assert typed_to_json(v) == json

def test_DataModel():
    json = {
        'state': 'ok',
        'string': 'a',
        'list_str': ['a', 'e', 'd'],
        'num': 2,
        'list_num': [0.3, 0.2, 0.4],
        'data3d': [[2, 2], [34, 4]],
        'range_num': {'from': 1, 'to': 10},
        'counting': {
            'abc': {'count': 2, 'childs': None},
            'qwe': {
                'count': 6,
                'childs': {'ert': {'count': 5, 'childs': None } }
            }
        },
        'union_data': [
            'aaaa',
            2323,
            {'from': 42, 'to': 100}
        ]
    }

    model = DataModel(
        state = State.ok,
        string='a',
        list_str=['a', 'e', 'd'],
        num=2,
        list_num=[.3,.2,.4],
        data3d=[
            [2, 2],
            [34, 4]
        ],
        range_num={ 'from': 1, 'to': 10 },
        counting={
            'abc': CountingDict(count=2, childs=None),
            'qwe': CountingDict(count=6, childs={ 'ert': CountingDict(count=5, childs=None) } )
        },
        union_data=[
            'aaaa',
            2323,
            {'from': 42, 'to': 100}
        ]
    )

    v = typed_from_json(DataModel, json)
    assert v == model

    assert typed_to_json(v) == json
