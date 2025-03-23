# shuscribe/schemas/base.py

from abc import abstractmethod
from enum import Enum
import re
from typing import Any, Self
import jsonref
import json

from pydantic import BaseModel, ValidationError

from shuscribe.utils import find_last_json_block
    
class DescriptiveEnum(Enum):
    """Enum with a description"""
    description: str
    
    def __new__(cls, value: Any, description: str = ""):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj
    
    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name} ({self.description})"
    
class Promptable(BaseModel):
    """Base class for objects that can be converted to parts of a prompt"""
    @abstractmethod
    def to_prompt(self) -> str:
        pass
    
    
class BaseOutputSchema(BaseModel):
    """Base class for objects that can be used as an output schema"""
    
    @classmethod
    def to_output_schema_str(cls) -> str:
        schema: dict = jsonref.replace_refs(cls.model_json_schema(by_alias=False), merge_props=True, lazy_load=False) # type: ignore
        if '$defs' in schema:
            del schema['$defs']
        return json.dumps(schema, indent=2, ensure_ascii=False)
    
    @classmethod
    def model_validate_json(cls, json_data: str, **kwargs: Any) -> Self:
        try:
            return super().model_validate_json(json_data, **kwargs)
        except ValidationError as e:
            # we should try to parse the json as the last markdown ```json``` block
            new_json_data = find_last_json_block(json_data)
            if new_json_data:
                return super().model_validate_json(new_json_data, **kwargs)
            raise e
