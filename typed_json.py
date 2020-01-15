from typing import Callable, Any, Dict, List, Tuple, get_type_hints, TypeVar, Type

try:
    from typing import _TypedDictMeta # type: ignore
except ImportError:
    from typing_extensions import _TypedDictMeta # type: ignore

__all__ = [
    'register_converter',
    'typed_to_json', 'typed_from_json',
    'is_typed_class', 'is_namedtuple'
]

T = TypeVar('T')
TypedConverter = Callable[[Any, Any], Tuple[bool, Any]]
JsonConverter = Callable[[Any], Tuple[bool, Dict[str, Any]]]
TYPED_CONVERTERS: List[TypedConverter] = []
JSON_CONVERTERS: List[JsonConverter] = []

def register_converter(typed_conv: TypedConverter, json_conv: JsonConverter):
    TYPED_CONVERTERS.append(typed_conv)
    JSON_CONVERTERS.append(json_conv)

# checker
def is_typed_class(cls):
    return cls.__class__ is _TypedDictMeta or is_namedtuple(cls) or is_dataclass(cls)
def is_namedtuple(cls):
    return hasattr(cls, '_asdict') and hasattr(cls, '_fields') and hasattr(cls, '__annotations__')
def is_dataclass(cls):
    return hasattr(cls, '__dataclass_fields__') and hasattr(cls, '__dataclass_params__')

def typed_to_json(value) -> Dict[str, Any]:
    t = type(value)
    if not (isinstance(value, dict) or is_namedtuple(t) or is_dataclass(value)):
        raise ValueError(f'This function only support <dict>, <NamedTuple>, <TypedDict>, <dataclass> but got: {t}')

    return _json_handler(value)

def _json_handler(value) -> Any:
    if value is None or any(isinstance(value, t) for t in (int, float, str, bool)):
        return value
    elif is_namedtuple(value):
        return {
            k: _json_handler(v)
            for k, v in value._asdict().items()
        }
    elif is_dataclass(value):
        return {
            k: _json_handler(v)
            for k, v in vars(value).items()
        }
    elif isinstance(value, list):
        return [
            _json_handler(v)
            for v in value
        ]
    elif isinstance(value, dict):
        return {
            k: _json_handler(v)
            for k, v in value.items()
        }

    for handler in JSON_CONVERTERS:
        success, val = handler(value)
        if success:
            return val

    raise TypeError(f'Unable to handler type: {type(value)}')

def typed_from_json(typed_class: Type[T], dict_val: dict) -> T:
    if not is_typed_class(typed_class):
        raise ValueError(f'This function only support <NamedTuple>, <TypedDict>, <dataclass> but got: {typed_class}')
    elif not isinstance(dict_val, dict):
        raise TypeError(f'Second argument need Dict type, but got: {type(dict_val)}')

    new_kwargs = {}
    for key, annotation in get_type_hints(typed_class).items():
        val = dict_val.get(key, None)
        # print(f'{key} {val} {annotation}')

        new_kwargs[key] = _annotation_handler(annotation, val, key, typed_class)

    return typed_class(**new_kwargs)

def _annotation_handler(cls, value, key, root_class):
    if value is None:
        if 'typing.Union' in str(cls) and any(i is type(None) for i in cls.__args__):
            if is_namedtuple(root_class):
                return root_class._field_defaults[key]
            elif is_dataclass(root_class):
                return root_class.__dataclass_fields__[key].default
            else:
                return None
        else:
            raise ValueError(f'{root_class.__name__} missing required attribute: {key}')

    elif 'typing.Union' in str(cls):
        for annotation in cls.__args__:
            if 'NoneType' not in str(annotation):
                return _annotation_handler(annotation, value, key, root_class)

    elif 'typing.List' in str(cls):
        if isinstance(value, list):
            return [
                _annotation_handler(cls.__args__[0], v, key, root_class)
                for v in value
            ]

    elif 'typing.Dict' in str(cls):
        if isinstance(value, dict):
            return {
                k: _annotation_handler(cls.__args__[1], v, key, root_class)
                for k, v in value.items()
            }

    elif type(cls) is type and isinstance(value, cls):
        return value
    elif is_typed_class(cls):
        return typed_from_json(cls, value)

    for handler in TYPED_CONVERTERS:
        success, v = handler(cls, value)
        if success:
            return v

    raise TypeError(f'Key "{key}" of {root_class.__name__} need {cls} but got {type(value)}')
