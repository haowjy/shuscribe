# shuscribe/schemas/base.py

from abc import abstractmethod
from enum import Enum
from typing import Any

from pydantic import BaseModel
    
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
    """Base class for all promptable objects"""
    @abstractmethod
    def to_prompt(self) -> str:
        pass