# shuscribe/schemas/wikigen/entity.py

from typing import Dict, Generator, List, Optional, Tuple

from pydantic import BaseModel, Field

from shuscribe.schemas.base import DescriptiveEnum, BaseOutputSchema, Promptable

import logging
logger = logging.getLogger(__name__)

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
        description="The main identifier of the entity that will be used to reference the entity. Ensure that this identifier is unique to the entity by adding clarifications (parentheses, prefixes, suffixes, character titles, clarifying adjectives, etc). This identifier should be something that you would actually call the entity in conversation and describes them completely")

    aliases: List[str] = Field(
        description="All names and other identifiers for the entity")
    
    related_entities: List[str] = Field(
        description="List of entity identifiers that are related to the entity")
    
    def to_upsert_dict(self, sig_entities: List['ExtractedEntity'] | None = None) -> dict:
        if sig_entities:
            related_entities = [e.identifier for e in sig_entities if e.identifier in self.related_entities]
            
        return {
            "identifier": self.identifier,
            "aliases": self.aliases,
            "entity_type": self.entity_type.value,
            "significance_level": self.significance_level.value,
            "narrative_role": self.narrative_role,
            "description": self.description,
            # (f'key_facts: |\n{"\n".join([f"  {k}" for k in self.key_facts])}\n' if len(self.key_facts) > 0 else '') +
            "related_entities": related_entities
        }
            

class ExtractEntitiesOutSchema(BaseOutputSchema):
    entities: List[ExtractedEntity] = Field(
        description="important entities found in the chapter that carry narrative significance")

    def filter_entities(self, min_sig_level: EntitySigLvl = EntitySigLvl.RELEVANT) -> List[ExtractedEntity]:
        return [entity for entity in self.entities if entity.significance_level >= min_sig_level]
    
    def batch_for_upsert(self, sig_level: EntitySigLvl = EntitySigLvl.RELEVANT, chunk_size: int = 5) -> Generator[dict, None, None]:
        filtered_entities = self.filter_entities(sig_level)
        for i in range(0, len(filtered_entities), chunk_size):
            yield {"entities": [entity.to_upsert_dict(filtered_entities) for entity in filtered_entities[i:i+chunk_size]]}
            
            
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
    
    identifier: str = Field(
        description="main identifier of the entity. This identifier should be something that you would actually call the entity in conversation. Add clarifications (parentheses, prefix titles, titles, etc) to the identifier if needed to make it different from another entity. Change the identifier if you think it would no longer be unique")
    
    old_identifier: Optional[str] = Field(
        description="old identifier of the entity if you are updating an existing entity")
    
    detailed_description: str = Field(
        description="detailed markdown bullet point description of the entity's attributes (what the entity is, what it does, etc), not a chronology of what happens to the entity")
    
    narrative_role: str = Field(
        description="narrative role this entity plays in the context of the story")
    
    facts: List[EntityFact] = Field(
        description="list of **NEW** facts about the entity that are not events but rather attributes of the entity")
    
    removed_facts: List[str] = Field(
        description="list of facts about the entity that are no longer true or no longer relevant")
    
    entity_types: List[EntityType] = Field(
        description="types of entities that the entity can be classified into")
    
    significance_level: EntitySigLvl = Field(
        description="The significance level of the entity to the chapter's plot and the story as a whole. You may change the significance as the story evolves")
    
    aliases: List[str] = Field(
        description="All names and other identifiers for the entity")
    
    related_entities: List[Relationship] = Field(
        description="relationships between the entity and other entities")
    
    def to_embed_content(self, prefix: str = "") -> str:
        return (
            prefix +
            "```json\n" +
            self.model_dump_json(indent=2, include={"identifier", "detailed_description", "narrative_role", "facts", "entity_types", "significance_level" , "aliases", "related_entities"}) +
            "```"
        )

class UpsertEntitiesOutSchema(BaseOutputSchema):
    entities: List[UpsertEntity] = Field(
        description="entities to upsert")










import torch
device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

class TempEntityRecord(Promptable):
    # TODO: move to an actual database model, this is a placeholder
    identifier: str
    embedding: List[float] = Field(default_factory=list)  # Changed to ensure proper JSON serialization
    entity_types: List[EntityType]
    aliases: List[str]
    detailed_description: str
    narrative_role: str
    facts: List[EntityFact]
    related_entities: Dict[str, Relationship]
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            np.ndarray: lambda x: x.tolist(),  # Handle numpy arrays
            np.float32: float,  # Handle numpy float32
            np.float64: float,  # Handle numpy float64
        }
    
    def to_prompt(self) -> str:
        return self.model_dump_json(indent=2, exclude={"embedding"})
    
    def to_embed_content(self, prefix: str = "") -> str:
        return (
            prefix +
            "```json\n" +
            self.model_dump_json(indent=2, exclude={"embedding"}) +
            "```"
        )
    
    def to_dict(self) -> dict:
        return self.model_dump(exclude={"embedding"})
    
    def __repr__(self) -> str:
        return f"TempEntityRecord(identifier={self.identifier})"
    
    def __str__(self) -> str:
        return f"TempEntityRecord(identifier={self.identifier})"
    
    def __hash__(self) -> int:
        return hash(self.identifier)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TempEntityRecord):
            return False
        return self.identifier == other.identifier

class TempEntityDBRepresentation(BaseModel):
    entities: Dict[str, TempEntityRecord] = Field(
        description="entity identifier -> entity record")




class TempEntityDB:
    # TODO: move to an actual database model, this is a placeholder
    
    def __init__(self):
        self.entities_db = TempEntityDBRepresentation(entities={})
        
        # Initialize the model
        self.model = SentenceTransformer("nomic-ai/nomic-embed-text-v1", trust_remote_code=True, device=device)
    
    def _update_entity(self, entity: UpsertEntity, old_entity: TempEntityRecord):
        old_entity.identifier = entity.identifier
        old_entity.entity_types = entity.entity_types
        old_entity.aliases = list(set(old_entity.aliases) | set(entity.aliases))
        old_entity.detailed_description = entity.detailed_description
        old_entity.narrative_role = entity.narrative_role
        
        for to_remove in entity.removed_facts:
            old_entity.facts = [fact for fact in old_entity.facts if fact.fact != to_remove]
        
        for fact in entity.facts:
            old_entity.facts.append(fact)
        
        for related_entity in entity.related_entities:
            if related_entity.target_entity_id not in old_entity.related_entities:
                old_entity.related_entities[related_entity.target_entity_id] = related_entity
            else:
                old_entity.related_entities[related_entity.target_entity_id].description = related_entity.description
                old_entity.related_entities[related_entity.target_entity_id].relationship_type = related_entity.relationship_type
                old_entity.related_entities[related_entity.target_entity_id].is_bidirectional = related_entity.is_bidirectional
        
    def upsert(self, upsert_entities: List[UpsertEntity]) -> List[TempEntityRecord]:
        # TODO: move to an actual database model, this is a placeholder
        entities_to_embed: List[TempEntityRecord] = []
        entities_updated: List[TempEntityRecord] = []
        entities_new: List[TempEntityRecord] = []
        
        for entity in upsert_entities:
            # update existing entity
            
            # changed identifier -> update old entity
            if entity.old_identifier and entity.old_identifier in self.entities_db.entities:
                old_entity = self.entities_db.entities[entity.old_identifier]
                self._update_entity(entity, old_entity)
                entities_to_embed.append(old_entity)
                entities_updated.append(old_entity)
                
            # no identifier change -> update old entity
            elif entity.identifier in self.entities_db.entities:
                old_entity = self.entities_db.entities[entity.identifier]
                self._update_entity(entity, old_entity)
                entities_to_embed.append(old_entity)
                entities_updated.append(old_entity)
            else: # new entity
                new_related_entities = {}
                for related_entity in entity.related_entities:
                    new_related_entities[related_entity.target_entity_id] = related_entity
                    
                self.entities_db.entities[entity.identifier] = TempEntityRecord(
                    identifier=entity.identifier,
                    embedding=[],
                    entity_types=entity.entity_types,
                    aliases=entity.aliases,
                    detailed_description=entity.detailed_description,
                    narrative_role=entity.narrative_role,
                    facts=entity.facts,
                    related_entities=new_related_entities,
                )
                entities_to_embed.append(self.entities_db.entities[entity.identifier])
                entities_new.append(self.entities_db.entities[entity.identifier])
        # Embed the entities
        embeddings = self.model.encode([entity.to_embed_content("search_document: ") for entity in entities_to_embed])
        
        # Update the embeddings
        for i, entity in enumerate(entities_to_embed):
            entity.embedding = embeddings[i].tolist()
        
        logger.info(f"Upserted {len(entities_updated)} entities, {len(entities_new)} new entities")
        logger.info(f"{entities_updated=}\n{entities_new=}")
        
        return entities_to_embed
    
    def size(self) -> int:
        return len(self.entities_db.entities)
        
    def search(self, query: str, k: int = 10, min_sim: float = 90) -> List[Tuple[TempEntityRecord, float]]:
        entity_list = list(self.entities_db.entities.values())
        if len(entity_list) == 0:
            return []
        
        # Build index
        index = faiss.IndexFlatL2(self.model.get_sentence_embedding_dimension())
        index.add(torch.stack([torch.tensor(entity.embedding) for entity in entity_list])) # type: ignore
                
        # Embed the query
        query_embedding = self.model.encode([f"search_query: {query}"])
        
        # Search for the k most similar entities
        distances, indices = index.search(query_embedding, k) # type: ignore
        
        # for each query, get the k most similar entities, along with the cosine similarity score
        
        results = []
        for i in range(k):
            dist = min(max(distances[0][i], 0), 4)
            sim = float(100 * (4 - dist) / 4)
            if sim > min_sim:
                results.append((entity_list[indices[0][i]], sim))
        
        return results

    def find_by_identifier(self, identifier: List[str]) -> List[TempEntityRecord]:
        return [self.entities_db.entities[id] for id in identifier if id in self.entities_db.entities]
    
    def find_by_alias(self, alias: List[str]) -> List[TempEntityRecord]:
        return [entity for entity in self.entities_db.entities.values() if any(alias in entity.aliases for alias in alias)]
    
    