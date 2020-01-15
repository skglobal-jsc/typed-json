import pytest
from datetime import datetime

from typed_json import typed_from_json, typed_to_json
from .models import CountingModel, ISODateTime, MicroSecondsEpochDateTime, MilliSecondsEpochDateTime, Range, GenericModel, TimeData, DataModel, CountingDict

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

    json['childs']['abc']['childs'] = None
    json['childs']['qwe']['childs']['ert']['childs'] = None
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

def test_TimeData():
    now = datetime.now()
    json = {
        'iso': now.isoformat(),
        'mili' : int(now.timestamp()*1000),
        'micro' : int(now.timestamp()*1000000),
    }
    model = TimeData(
        iso=ISODateTime(now),
        mili=MilliSecondsEpochDateTime(datetime.fromtimestamp(int(now.timestamp()*1000) / 1000)),
        micro=MicroSecondsEpochDateTime(now),
    )

    v = typed_from_json(TimeData, json)
    assert v == model

    assert typed_to_json(v) == json

def test_DataModel():
    json = {
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
        }
    }

    model = DataModel(
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
            'abc': CountingModel(count=2),
            'qwe': CountingModel(count=6, childs={ 'ert': CountingModel(count=5) } )
        }
    )

    v = typed_from_json(DataModel, json)
    assert v == model

    assert typed_to_json(v) == json


def test_to_typed_fail():
    with pytest.raises(TypeError, match=r'Key "count" of CountingModel need *'):
        typed_from_json(CountingModel, {'count': 'af'})

    with pytest.raises(ValueError, match=r'This function only support <NamedTuple>, <TypedDict>'):
        typed_from_json(int, {})

    with pytest.raises(TypeError, match=r"Second argument need Dict type, but got: *"):
        typed_from_json(CountingModel, 3)
    
    with pytest.raises(ValueError, match=r'CountingModel missing required attribute *'):
        typed_from_json(CountingModel, {})

    with pytest.raises(TypeError, match=r'Key "ite" of GenericModel need typing.Iterable\[~T\] *'):
        typed_from_json(GenericModel, { 'ite': [] })

    with pytest.raises(ValueError, match=r'This function only support *'):
        typed_to_json(3)

    with pytest.raises(TypeError, match=r'Unable to handler type: *'):
        typed_to_json({ 'e': set() })
