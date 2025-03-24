from typing import Generator, List, Optional

from pydantic import BaseModel, Field

from shuscribe.schemas.base import DescriptiveEnum, BaseOutputSchema

class EntitySigLvl(DescriptiveEnum):
    CENTRAL = "Central", "absolutely central to the story"
    MAJOR = "Major", "necessary for the story to function"
    RELEVANT = "Relevant", "relevant to the story"
    MINOR = "Minor", "Having a slight or indirect connection to the story; not essential"
    INCIDENTAL = "Incidental", "mentioned only briefly; unimportant; background"
    
    @property
    def int_val(self) -> int:
        return {
            self.CENTRAL: 5,
            self.MAJOR: 4,
            self.RELEVANT: 3,
            self.MINOR: 2,
            self.INCIDENTAL: 1
        }[self]
    
    def __gt__(self, other: "EntitySigLvl") -> bool:
        return self.int_val > other.int_val
    
    def __ge__(self, other: "EntitySigLvl") -> bool:
        return self.int_val >= other.int_val
    
    def __lt__(self, other: "EntitySigLvl") -> bool:
        return self.int_val < other.int_val
    
    def __le__(self, other: "EntitySigLvl") -> bool:
        return self.int_val <= other.int_val
    
    @staticmethod
    def to_prompt_reference(tab_prefix: str = "  ") -> str:
        entity_sig_lvls_prompt = ""
        for entity_sig_lvl in EntitySigLvl:
            entity_sig_lvls_prompt += (
                f"{tab_prefix}{entity_sig_lvl.int_val}. {entity_sig_lvl.value}: {entity_sig_lvl.description}\n"
            )
        return entity_sig_lvls_prompt
    

class EntityType(DescriptiveEnum):
    # Primary Narrative Elements (Essential)
    CHARACTER = "Character", "People, beings, or sentient entities (including unnamed)"
    LOCATION = "Location", "Places, settings, or spatial environments"
    EVENT = "Event", "Significant occurrences, happenings, or incidents"
    ITEM = "Item", "Physical objects or artifacts with narrative significance"
    CONCEPT = "Concept", "Abstract systems, powers, theories, or ideas important to the world"
    
    # Grouping & Context Elements (Important)
    GROUP = "Group", "Collections of characters (including organizations, factions, etc.)"
    TIME_PERIOD = "Time Period", "Significant temporal ranges or eras"
    CULTURE = "Culture", "Societal patterns, practices, and beliefs"
    
    # Literary Elements (Secondary for MVP)
    THEME = "Theme", "Recurring ideas, motifs, or messages"
    SYMBOLISM = "Symbolism", "Symbolic elements and their meanings"
    ALLUSION = "Allusion", "References to other stories, media, popular culture, real life, etc."
    
    OTHER = "Other", "Key entities that don't fit other categories"
    
    @staticmethod
    def to_prompt_reference(tab_prefix: str = "  ") -> str:
        entity_types_prompt = ""
        for i, entity in enumerate(EntityType):
            entity_types_prompt += (
                f"{tab_prefix}{i+1}. {entity.value}s: {entity.description}\n"
            )
        return entity_types_prompt
    

# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
#                                        Extract Entities
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------

class ExtractedEntity(BaseModel):
    description: str = Field(
        description="The description of the entity (what the entity is, what it does, etc)")
    
    narrative_role: str = Field(
        description="The narrative role of the entity in the context of this chapter and the story as a whole")
    
    # key_facts: List[str] = Field(
    #     description="List of key facts about the entity introduced in this chapter")
    
    significance_level: EntitySigLvl = Field(
        description="The significance level of the entity to the chapter's plot and the story as a whole")
    
    entity_type: EntityType = Field(
        description="The type of entity")
    
    identifier: str = Field(
        description="The main identifier of the entity that will be used to reference the entity. Ensure that this identifier is unique across the story by adding clarifications (parentheses, prefix titles, titles, etc). This identifier should be something that you would actually call the entity in conversation")

    aliases: List[str] = Field(
        description="All names and other identifiers for the entity")
    
    related_entities: List[str] = Field(
        description="List of entity identifiers that are related to the entity")
    
    def to_upsert_str(self, sig_entities: List['ExtractedEntity'] | None = None) -> str:
        if sig_entities:
            related_entities = [e.identifier for e in sig_entities if e.identifier in self.related_entities]
            
        return (
            f'name: {self.identifier}\n' +
            (f'other_names: {self.aliases}\n' if self.aliases else '') +
            f'entity_type: {self.entity_type.value}\n' +
            f'significance_level: {self.significance_level.value}\n' +
            f'narrative_role: {self.narrative_role}\n' +
            f'description: {self.description}\n' +
            # (f'key_facts: |\n{"\n".join([f"  {k}" for k in self.key_facts])}\n' if len(self.key_facts) > 0 else '') +
            (f'related_entities: {related_entities}\n' if related_entities else '')
            )
            

class ExtractEntitiesOutSchema(BaseOutputSchema):
    entities: List[ExtractedEntity] = Field(
        description="important entities found in the chapter that carry narrative significance")

    def filter_entities(self, min_sig_level: EntitySigLvl = EntitySigLvl.INCIDENTAL) -> List[ExtractedEntity]:
        return [entity for entity in self.entities if entity.significance_level >= min_sig_level]
    
    def batch_for_upsert(self, sig_level: EntitySigLvl = EntitySigLvl.INCIDENTAL, chunk_size: int = 5) -> Generator[List[str], None, None]:
        filtered_entities = self.filter_entities(sig_level)
        for i in range(0, len(filtered_entities), chunk_size):
            yield [entity.to_upsert_str(filtered_entities) for entity in filtered_entities[i:i+chunk_size]]
            
            
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
#                               Upsert Entities and Relationships
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------

class RelationshipType(DescriptiveEnum):
    # Broadly categorized but meaningful relationship types
    ASSOCIATION = "Association", "General connection between entities"
    PERSONAL = "Personal", "Character relationships (family, friends, rivals, etc.)"
    LOCATION = "Location", "Spatial relationships (located in, traveled to, etc.)"
    OWNERSHIP = "Ownership", "Possession or belonging relationships"
    CAUSAL = "Causal", "One entity affects or influences another"
    THEMATIC = "Thematic", "Connection to themes, symbols, or concepts"
    
    OTHER = "Other", "Other relationship types"
    
    @staticmethod
    def to_prompt_reference(tab_prefix: str = "  ") -> str:
        relationship_types_prompt = ""
        for i, relationship in enumerate(RelationshipType):
            relationship_types_prompt += (
                f"{tab_prefix}{i+1}. {relationship.value}s: {relationship.description}\n"
            )
        return relationship_types_prompt

class Relationship(BaseModel):
    target_entity_id: str = Field(
        description="identifier of the entity that is related to the entity")
    
    description: str = Field(
        description="description of the relationship")
    
    relationship_type: RelationshipType = Field(
        description="type of relationship between the source and target entities")
    
    is_bidirectional: bool = Field(
        description="Whether the relationship is bidirectional or just one from the entity to the target")
     

class EntityFactType(DescriptiveEnum):
    EXPLICIT = "Explicit", "Information directly stated in the text"
    IMPLIED = "Implicit", "Information reasonably inferred but not directly stated"
    SPECULATIVE = "Speculative", "Educated guesses based on narrative patterns"
    RETROACTIVE = "Retroactive", "New information that recontextualizes earlier events"
    

class EntityFact(BaseModel):
    fact: str = Field(
        description="fact about the entity")
    
    type: EntityFactType = Field(
        description="type of the fact")
    

class UpsertEntity(BaseModel):
    
    old_identifier: Optional[str] = Field(
        description="old identifier of the entity if you are updating an existing entity")
    
    identifier: str = Field(
        description="main identifier of the entity. This identifier should be something that you would actually call the entity in conversation. Add clarifications (parentheses, prefix titles, titles, etc) to the identifier to make it unique. Change the identifier if you think it would no longer be unique")
    
    detailed_description: str = Field(
        description="detailed markdown bullet point description of the entity")
    
    narrative_role: str = Field(
        description="narrative role this entity plays in the context of the story")
    
    facts: List[EntityFact] = Field(
        description="list of NEW facts about the entity")
    
    removed_facts: List[str] = Field(
        description="list of facts about the entity that are no longer true or no longer relevant")
    
    entity_types: List[EntityType] = Field(
        description="types of entities that the entity can be classified into")
    
    aliases: List[str] = Field(
        description="All names and other identifiers for the entity")
    
    related_entities: List[Relationship] = Field(
        description="relationships between the entity and other entities")

class UpsertEntitiesOutSchema(BaseOutputSchema):
    entities: List[UpsertEntity] = Field(
        description="entities to upsert")