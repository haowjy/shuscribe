from typing import List, Dict, Optional
from enum import Enum

from pydantic import BaseModel, Field

from shuscribe.schemas.base import DescriptiveEnum

class EntitySigLvl(str, Enum):
    CENTRAL = "central"
    MAJOR = "major"
    SUPPORTING = "supporting"
    MINOR = "minor"
    BACKGROUND = "background"
    
    @property
    def int_val(self) -> int:
        return {
            self.CENTRAL: 5,
            self.MAJOR: 4,
            self.SUPPORTING: 3,
            self.MINOR: 2,
            self.BACKGROUND: 1
        }[self]
    
    def __gt__(self, other: "EntitySigLvl") -> bool:
        return self.int_val > other.int_val
    
    def __ge__(self, other: "EntitySigLvl") -> bool:
        return self.int_val >= other.int_val
    
    def __lt__(self, other: "EntitySigLvl") -> bool:
        return self.int_val < other.int_val
    
    def __le__(self, other: "EntitySigLvl") -> bool:
        return self.int_val <= other.int_val
    

class EntityType(DescriptiveEnum):
    # Primary Narrative Elements (Essential)
    CHARACTER = "character", "People, beings, or sentient entities (including unnamed)"
    LOCATION = "location", "Places, settings, or spatial environments"
    EVENT = "event", "Significant occurrences, happenings, or incidents"
    ITEM = "item", "Physical objects or artifacts with narrative significance"
    CONCEPT = "concept", "Abstract systems, powers, theories, or ideas important to the world"
    
    # Grouping & Context Elements (Important)
    GROUP = "group", "Collections of characters (including organizations, factions, etc.)"
    TIME_PERIOD = "time_period", "Significant temporal ranges or eras"
    CULTURE = "culture", "Societal patterns, practices, and beliefs"
    
    # Literary Elements (Secondary for MVP)
    THEME = "theme", "Recurring ideas, motifs, or messages"
    SYMBOLISM = "symbolism", "Symbolic elements and their meanings"
    ALLUSION = "allusion", "References to other works, events, or cultural touchpoints"
    
    OTHER = "other", "Elements not fitting other categories"
    
    
class ExtractedEntity(BaseModel):
    description: str = Field(
        description="The description of the entity (what the entity is, what it does, etc)")
    
    narrative_significance: str = Field(
        description="The narrative significance of the entity in the context of this chapter and the story as a whole")
    
    significance_level: EntitySigLvl = Field(
        description="The significance level of the entity to the chapter's plot and the story as a whole")
    
    entity_type: EntityType = Field(
        description="The type of entity")
    
    identifier: str = Field(
        description="The main identifier of the entity that will be used to reference the entity and you believe is unique")

    aliases: List[str] = Field(
        description="All names and other identifiers for the entity")
    
    related_entities: List[str] = Field(
        description="List of entity identifiers that are related to the entity")
    
    def to_upsert_str(self, sig_entities: List['ExtractedEntity'] | None = None) -> str:
        if sig_entities:
            related_entities = [e.identifier for e in sig_entities if e.identifier in self.related_entities]
            if len(related_entities) > 0:
                return f"""{self.entity_type.value}: {self.identifier} - {self.significance_level.value} (related: {', '.join(related_entities)})"""
            
        return f"""{self.entity_type.value}: {self.identifier} - {self.significance_level.value}"""

class ExtractEntitiesOutSchema(BaseModel):
    entities: List[ExtractedEntity] = Field(
        description="important entities found in the chapter that carry narrative significance")

    def filter_entities(self, sig_level: EntitySigLvl) -> List[ExtractedEntity]:
        return [entity for entity in self.entities if entity.significance_level >= sig_level]
