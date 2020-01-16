from typing import NamedTuple, Dict, Optional, Union, TypeVar, Iterable

import pytest
from typed_json import typed_from_json, typed_to_json, register_converter

class Model(NamedTuple):
    count: int

T = TypeVar('T')
class GenericModel(NamedTuple):
    ite: Iterable[T]

class OptionalInside(NamedTuple):
    not_accept: Optional[Union[Dict[str, int], int]] = 0
    accept: Optional[Union[Dict[str, Optional[int]], int]] = 0

def test_common_fail():
    with pytest.raises(TypeError, match=r'Key "count" of Model need *'):
        typed_from_json(Model, {'count': 'af'})

    with pytest.raises(ValueError, match=r'This function only support *'):
        typed_from_json(int, {})

    with pytest.raises(TypeError, match=r"Second argument need Dict type, but got: *"):
        typed_from_json(Model, 3) # type: ignore
    
    with pytest.raises(ValueError, match=r'Model missing required attribute *'):
        typed_from_json(Model, {})

    with pytest.raises(TypeError, match=r'Key "ite" of GenericModel need typing.Iterable\[~T\] *'):
        typed_from_json(GenericModel, { 'ite': [] })

    with pytest.raises(ValueError, match=r'This function only support *'):
        typed_to_json(3)

    with pytest.raises(TypeError, match=r'Unable to handler type: *'):
        typed_to_json({ 'e': set() })

def test_optional_inside():
    v = typed_from_json(OptionalInside, { 'accept': { 'asd': None } })
    assert v == OptionalInside(accept={ 'asd': None })
    assert typed_to_json(v) == { 'accept': { 'asd': None }, 'not_accept': 0 }

    with pytest.raises(ValueError, match=r'None is not accepted inside attribute *'):
        typed_from_json(OptionalInside, { 'not_accept': { 'asd': 3, 'qwe': None } })