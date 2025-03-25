# # shuscribe/services/llm/pipeline/wikigen_pipeline.py

# import os
# from pathlib import Path
# from typing import List, Dict, Any, Optional, AsyncGenerator, Type
# import logging
# import json

# import faiss
# import numpy as np

# from shuscribe.services.llm.pipeline.base_pipeline import Pipeline, LLMPipelineStep, PipelineStep
# from shuscribe.schemas.streaming import StreamChunk
# from shuscribe.schemas.llm import Message, GenerationConfig
# from shuscribe.schemas.wikigen.summary import ChapterSummary
# from shuscribe.schemas.wikigen.entity import ExtractEntitiesOutSchema, UpsertEntitiesOutSchema, EntitySigLvl
# from shuscribe.schemas.wikigen.wiki import WikiPage
# from shuscribe.schemas.pipeline import Chapter, StoryMetadata
# from shuscribe.services.llm.prompts import templates

# logger = logging.getLogger(__name__)

# class ChapterSummaryStep(LLMPipelineStep[Dict[str, Any], StreamChunk]):
#     """Pipeline step that summarizes a chapter."""
    
#     def __init__(self, provider_name: str, model: str):
#         super().__init__("chapter_summary", provider_name, model)
    
#     async def process(self, input_data: Dict[str, Any], stream: bool = False) -> StreamChunk:
#         """Generate a chapter summary."""
#         # Reload the template to get the latest version
#         templates.chapter.summary.reload()
        
#         # Format the messages using the template
#         messages = templates.chapter.summary.format(
#             current_chapter=input_data.get("current_chapter"),
#             story_metadata=input_data.get("story_metadata"),
#             summary_so_far=input_data.get("comprehensive_wiki", None),
#             recent_summaries=input_data.get("recent_summaries", []),
#         )
        
#         if stream:
#             # Return the first complete chunk
#             async for chunk in self.generate_with_llm(messages, templates.chapter.summary.default_config, stream=True):
#                 if chunk.status == StreamStatus.COMPLETE:
#                     return chunk
#             # If no complete chunk, return the last chunk
#             return chunk
#         else:
#             # Generate and return the complete response
#             response = await self.generate_with_llm(messages, templates.chapter.summary.default_config, stream=False)
            
#             # Create a StreamChunk from the response
#             return StreamChunk(
#                 text="",
#                 accumulated_text=response.text,
#                 status=StreamStatus.COMPLETE,
#                 usage=response.usage
#             )
    
#     async def process_stream(self, input_data: Dict[str, Any]) -> AsyncGenerator[StreamChunk, None]:
#         """Generate a chapter summary with streaming."""
#         # Reload the template to get the latest version
#         templates.chapter.summary.reload()
        
#         # Format the messages using the template
#         messages = templates.chapter.summary.format(
#             current_chapter=input_data.get("current_chapter"),
#             story_metadata=input_data.get("story_metadata"),
#             summary_so_far=input_data.get("comprehensive_wiki", None),
#             recent_summaries=input_data.get("recent_summaries", []),
#         )
        
#         # Stream the generation
#         async for chunk in self.generate_with_llm(messages, templates.chapter.summary.default_config, stream=True):
#             yield chunk


# class EntityExtractionStep(LLMPipelineStep[Dict[str, Any], StreamChunk]):
#     """Pipeline step that extracts entities from a chapter."""
    
#     def __init__(self, provider_name: str, model: str):
#         super().__init__("entity_extraction", provider_name, model)
    
#     async def process(self, input_data: Dict[str, Any], stream: bool = False) -> StreamChunk:
#         """Extract entities from the chapter."""
#         # Reload the template to get the latest version
#         templates.entity.extract.reload()
        
#         # Get the chapter summary from the previous step
#         chapter_summary = ChapterSummary.from_chapter_summary(
#             input_data.get("chapter_index", 0), 
#             input_data.get("chapter_summary").accumulated_text
#         )
        
#         # Format the messages using the template
#         messages = templates.entity.extract.format(
#             current_chapter=input_data.get("current_chapter"),
#             story_metadata=input_data.get("story_metadata"),
#             chapter_summary=chapter_summary,
#             summary_so_far=input_data.get("comprehensive_wiki", None),
#             recent_summaries=input_data.get("recent_summaries", []),
#         )
        
#         if stream:
#             # Return the first complete chunk
#             async for chunk in self.generate_with_llm(messages, templates.entity.extract.default_config, stream=True):
#                 if chunk.status == StreamStatus.COMPLETE:
#                     return chunk
#             # If no complete chunk, return the last chunk
#             return chunk
#         else:
#             # Generate and return the complete response
#             response = await self.generate_with_llm(messages, templates.entity.extract.default_config, stream=False)
            
#             # Create a StreamChunk from the response
#             return StreamChunk(
#                 text="",
#                 accumulated_text=response.text,
#                 status=StreamStatus.COMPLETE,
#                 usage=response.usage
#             )
    
#     async def process_stream(self, input_data: Dict[str, Any]) -> AsyncGenerator[StreamChunk, None]:
#         """Extract entities with streaming."""
#         # Reload the template to get the latest version
#         templates.entity.extract.reload()
        
#         # Get the chapter summary from the previous step
#         chapter_summary = ChapterSummary.from_chapter_summary(
#             input_data.get("chapter_index", 0), 
#             input_data.get("chapter_summary").accumulated_text
#         )
        
#         # Format the messages using the template
#         messages = templates.entity.extract.format(
#             current_chapter=input_data.get("current_chapter"),
#             story_metadata=input_data.get("story_metadata"),
#             chapter_summary=chapter_summary,
#             summary_so_far=input_data.get("comprehensive_wiki", None),
#             recent_summaries=input_data.get("recent_summaries", []),
#         )
        
#         # Stream the generation
#         async for chunk in self.generate_with_llm(messages, templates.entity.extract.default_config, stream=True):
#             yield chunk


# class EntityUpsertStep(LLMPipelineStep[Dict[str, Any], UpsertEntitiesOutSchema]):
#     """Pipeline step that upserts entities."""
    
#     def __init__(self, provider_name: str, model: str, embedding_model: str = "all-MiniLM-L6-v2"):
#         super().__init__("entity_upsert", provider_name, model)
#         self.embedding_model = SentenceTransformer(embedding_model)
#         self.index = None
#         self.entity_ids = []
#         self.entity_embeddings = []
        
#     def _setup_index(self, existing_entities: List[Dict[str, Any]]):
#         """Set up the FAISS index for entity searching."""
#         if not existing_entities:
#             # Create an empty index
#             dimension = self.embedding_model.get_sentence_embedding_dimension()
#             self.index = faiss.IndexFlatL2(dimension)
#             return
        
#         # Extract entity identifiers and generate embeddings
#         self.entity_ids = [entity.get("identifier", "") for entity in existing_entities]
#         entity_texts = [entity.get("identifier", "") + " " + entity.get("detailed_description", "") for entity in existing_entities]
        
#         # Generate embeddings
#         self.entity_embeddings = self.embedding_model.encode(entity_texts)
        
#         # Create and populate the index
#         dimension = self.entity_embeddings.shape[1]
#         self.index = faiss.IndexFlatL2(dimension)
#         self.index.add(np.array(self.entity_embeddings).astype('float32'))
    
#     def _find_similar_entities(self, entity, top_k=3, threshold=0.8):
#         """Find similar existing entities using embedding similarity."""
#         if not self.index or self.index.ntotal == 0:
#             return []
        
#         # Generate embedding for the query entity
#         query_text = entity.identifier + " " + entity.description
#         query_embedding = self.embedding_model.encode([query_text])[0]
        
#         # Search for similar entities
#         D, I = self.index.search(np.array([query_embedding]).astype('float32'), min(top_k, self.index.ntotal))
        
#         # Filter by similarity threshold
#         results = []
#         for i, (dist, idx) in enumerate(zip(D[0], I[0])):
#             similarity = 1.0 - dist  # Convert distance to similarity
#             if similarity > threshold:
#                 results.append({
#                     "entity_id": self.entity_ids[idx],
#                     "similarity": similarity
#                 })
        
#         return results
    
#     async def process(self, input_data: Dict[str, Any], stream: bool = False) -> UpsertEntitiesOutSchema:
#         """Upsert entities from the extraction step."""
#         # Reload the template to get the latest version
#         templates.entity.upsert.reload()
        
#         # Parse the extracted entities
#         extracted_entities = ExtractEntitiesOutSchema.model_validate_json(
#             input_data.get("entity_extraction").accumulated_text
#         )
        
#         # Get existing entities
#         existing_entities = input_data.get("existing_entities", [])
#         self._setup_index(existing_entities)
        
#         # Get the chapter summary
#         chapter_summary = ChapterSummary.from_chapter_summary(
#             input_data.get("chapter_index", 0), 
#             input_data.get("chapter_summary").accumulated_text
#         )
        
#         # Initialize the result
#         upsert_entities = UpsertEntitiesOutSchema(entities=[])
        
#         # Process entities in batches
#         for batch in extracted_entities.batch_for_upsert(EntitySigLvl.RELEVANT, chunk_size=5):
#             # For each entity in the batch, find similar existing entities
#             for entity in batch:
#                 similar_entities = self._find_similar_entities(entity)
#                 # Attach the similar entities to include in the prompt
#                 entity.similar_entities = similar_entities
            
#             # Format the messages using the template
#             messages = templates.entity.upsert.format(
#                 current_chapter=input_data.get("current_chapter"),
#                 entity_batch=batch,
#                 story_metadata=input_data.get("story_metadata"),
#                 chapter_summary=chapter_summary,
#                 existing_entities=existing_entities,
#                 summary_so_far=input_data.get("comprehensive_wiki", None),
#                 recent_summaries=input_data.get("recent_summaries", []),
#             )
            
#             # Generate the response
#             response = await self.generate_with_llm(messages, templates.entity.upsert.default_config, stream=False)
            
#             # Parse the response and append to results
#             batch_result = UpsertEntitiesOutSchema.model_validate_json(response.text)
#             upsert_entities.entities.extend(batch_result.entities)
        
#         return upsert_entities
    
#     async def process_stream(self, input_data: Dict[str, Any]) -> AsyncGenerator[StreamChunk, None]:
#         """Upsert entities with streaming (this will show progress through batches)."""
#         # Since this process involves multiple LLM calls in batches,
#         # we'll create our own streaming mechanism
        
#         # Reload the template to get the latest version
#         templates.entity.upsert.reload()
        
#         # Parse the extracted entities
#         extracted_entities = ExtractEntitiesOutSchema.model_validate_json(
#             input_data.get("entity_extraction").accumulated_text
#         )
        
#         # Get existing entities
#         existing_entities = input_data.get("existing_entities", [])
#         self._setup_index(existing_entities)
        
#         # Get the chapter summary
#         chapter_summary = ChapterSummary.from_chapter_summary(
#             input_data.get("chapter_index", 0), 
#             input_data.get("chapter_summary").accumulated_text
#         )
        
#         # Initialize the result
#         upsert_entities = UpsertEntitiesOutSchema(entities=[])
#         accumulated_text = ""
        
#         # Process entities in batches
#         total_batches = len(list(extracted_entities.batch_for_upsert(EntitySigLvl.RELEVANT, chunk_size=5)))
#         current_batch = 0
        
#         for batch in extracted_entities.batch_for_upsert(EntitySigLvl.RELEVANT, chunk_size=5):
#             current_batch += 1
            
#             # Emit a progress update
#             progress_text = f"Processing batch {current_batch}/{total_batches} - "
#             for entity in batch:
#                 progress_text += f"{entity.identifier}, "
#             yield StreamChunk(
#                 text=progress_text,
#                 accumulated_text=accumulated_text + progress_text,
#                 status=StreamStatus.IN_PROGRESS
#             )
#             accumulated_text += progress_text + "\n"
            
#             # For each entity in the batch, find similar existing entities
#             for entity in batch:
#                 similar_entities = self._find_similar_entities(entity)
#                 # Attach the similar entities to include in the prompt
#                 entity.similar_entities = similar_entities
            
#             # Format the messages using the template
#             messages = templates.entity.upsert.format(
#                 current_chapter=input_data.get("current_chapter"),
#                 entity_batch=batch,
#                 story_metadata=input_data.get("story_metadata"),
#                 chapter_summary=chapter_summary,
#                 existing_entities=existing_entities,
#                 summary_so_far=input_data.get("comprehensive_wiki", None),
#                 recent_summaries=input_data.get("recent_summaries", []),
#             )
            
#             # Stream the batch processing
#             async for chunk in self.generate_with_llm(messages, templates.entity.upsert.default_config, stream=True):
#                 yield StreamChunk(
#                     text=chunk.text,
#                     accumulated_text=accumulated_text + chunk.text,
#                     status=StreamStatus.IN_PROGRESS
#                 )
#                 accumulated_text += chunk.text
            
#             # Parse the response and append to results
#             batch_result = UpsertEntitiesOutSchema.model_validate_json(chunk.accumulated_text)
#             upsert_entities.entities.extend(batch_result.entities)
        
#         # Send the final complete result
#         yield StreamChunk(
#             text="",
#             accumulated_text=upsert_entities.model_dump_json(indent=2),
#             status=StreamStatus.COMPLETE
#         )


# class WikiGenerationStep(LLMPipelineStep[Dict[str, Any], StreamChunk]):
#     """Pipeline step that generates the comprehensive wiki."""
    
#     def __init__(self, provider_name: str, model: str):
#         super().__init__("wiki_generation", provider_name, model)
    
#     async def process(self, input_data: Dict[str, Any], stream: bool = False) -> StreamChunk:
#         """Generate the comprehensive wiki."""
#         # Reload the template to get the latest version
#         templates.story.comprehensive_wiki.reload()
        
#         # Get the chapter summary
#         chapter_summary = ChapterSummary.from_chapter_summary(
#             input_data.get("chapter_index", 0), 
#             input_data.get("chapter_summary").accumulated_text
#         )
        
#         # Get the upserted entities
#         upsert_entities = input_data.get("entity_upsert")
        
#         # Format the messages using the template
#         messages = templates.story.comprehensive_wiki.format(
#             current_chapter=input_data.get("current_chapter"),
#             chapter_summary=chapter_summary,
#             key_entities=upsert_entities,
#             story_metadata=input_data.get("story_metadata"),
#         )
        
#         if stream:
#             # Return the first complete chunk
#             async for chunk in self.generate_with_llm(messages, templates.story.comprehensive_wiki.default_config, stream=True):
#                 if chunk.status == StreamStatus.COMPLETE:
#                     return chunk
#             # If no complete chunk, return the last chunk
#             return chunk
#         else:
#             # Generate and return the complete response
#             response = await self.generate_with_llm(messages, templates.story.comprehensive_wiki.default_config, stream=False)
            
#             # Create a StreamChunk from the response
#             return StreamChunk(
#                 text="",
#                 accumulated_text=response.text,
#                 status=StreamStatus.COMPLETE,
#                 usage=response.usage
#             )
    
#     async def process_stream(self, input_data: Dict[str, Any]) -> AsyncGenerator[StreamChunk, None]:
#         """Generate the comprehensive wiki with streaming."""
#         # Reload the template to get the latest version
#         templates.story.comprehensive_wiki.reload()
        
#         # Get the chapter summary
#         chapter_summary = ChapterSummary.from_chapter_summary(
#             input_data.get("chapter_index", 0), 
#             input_data.get("chapter_summary").accumulated_text
#         )
        
#         # Get the upserted entities
#         upsert_entities = input_data.get("entity_upsert")
        
#         # Format the messages using the template
#         messages = templates.story.comprehensive_wiki.format(
#             current_chapter=input_data.get("current_chapter"),
#             chapter_summary=chapter_summary,
#             key_entities=upsert_entities,
#             story_metadata=input_data.get("story_metadata"),
#         )
        
#         # Stream the generation
#         async for chunk in self.generate_with_llm(messages, templates.story.comprehensive_wiki.default_config, stream=True):
#             yield chunk


# class WikiGenPipeline(Pipeline):
#     """Pipeline for generating a narrative wiki from chapters."""
    
#     def __init__(
#         self, 
#         provider_name: str, 
#         model: str,
#         story_metadata: StoryMetadata,
#         output_dir: Optional[Path] = None
#     ):
#         super().__init__("wikigen", output_dir)
#         self.provider_name = provider_name
#         self.model = model
#         self.story_metadata = story_metadata
        
#         # Add pipeline steps
#         self.add_step(ChapterSummaryStep(provider_name, model))
#         self.add_step(EntityExtractionStep(provider_name, model))
#         self.add_step(EntityUpsertStep(provider_name, model))
#         self.add_step(WikiGenerationStep(provider_name, model))
    
#     async def process_chapter(
#         self, 
#         chapter: Chapter, 
#         chapter_index: int,
#         comprehensive_wiki: Optional[WikiPage] = None,
#         recent_summaries: List = None,
#         existing_entities: List[Dict[str, Any]] = None,
#         stream: bool = False
#     ) -> Dict[str, Any]:
#         """Process a single chapter through the pipeline."""
#         # Prepare the input data
#         input_data = {
#             "current_chapter": chapter,
#             "chapter_index": chapter_index,
#             "story_metadata": self.story_metadata,
#             "comprehensive_wiki": comprehensive_wiki,
#             "recent_summaries": recent_summaries or [],
#             "existing_entities": existing_entities or []
#         }
        
#         # Execute the pipeline
#         results = await self.execute(input_data, stream=stream)
        
#         # Process the results
#         processed_results = {
#             "chapter_summary": ChapterSummary.from_chapter_summary(
#                 chapter_index, 
#                 results["chapter_summary"].accumulated_text
#             ),
#             "extracted_entities": ExtractEntitiesOutSchema.model_validate_json(
#                 results["entity_extraction"].accumulated_text
#             ),
#             "upserted_entities": results["entity_upsert"],
#             "comprehensive_wiki": WikiPage.from_wiki_content(
#                 "Comprehensive Wiki", 
#                 results["wiki_generation"].accumulated_text
#             )
#         }
        
#         return processed_results
    
#     async def process_all_chapters(
#         self, 
#         chapters: List[Chapter],
#         start_chapter: int = 0,
#         stream: bool = False
#     ) -> Dict[str, Any]:
#         """Process all chapters sequentially, passing results between chapters."""
#         comprehensive_wiki = None
#         recent_summaries = []
#         existing_entities = []
        
#         final_results = {}
        
#         for i, chapter in enumerate(chapters[start_chapter:], start=start_chapter):
#             logger.info(f"Processing chapter {i+1}/{len(chapters)}: {chapter.title}")
            
#             # Create a chapter-specific output directory
#             chapter_dir = self.output_dir / f"chapter_{i}"
#             os.makedirs(chapter_dir, exist_ok=True)
            
#             # Process the chapter
#             results = await self.process_chapter(
#                 chapter=chapter,
#                 chapter_index=i,
#                 comprehensive_wiki=comprehensive_wiki,
#                 recent_summaries=recent_summaries,
#                 existing_entities=existing_entities,
#                 stream=stream
#             )
            
#             # Save the chapter results
#             for key, value in results.items():
#                 if hasattr(value, "model_dump_json"):
#                     with open(chapter_dir / f"{key}.json", "w") as f:
#                         f.write(value.model_dump_json(indent=2))
#                 else:
#                     with open(chapter_dir / f"{key}.json", "w") as f:
#                         json.dump(value, f, indent=2)
            
#             # Update the state for the next chapter
#             comprehensive_wiki = results["comprehensive_wiki"]
            
#             # Keep the last 3 summaries for context
#             recent_summaries.append(results["chapter_summary"])
#             if len(recent_summaries) > 3:
#                 recent_summaries = recent_summaries[-3:]
            
#             # Accumulate entities
#             if existing_entities:
#                 # Update existing entities with new information
#                 updated_entities = {}
#                 for entity in existing_entities:
#                     entity_id = entity.get("identifier", "")
#                     updated_entities[entity_id] = entity
                
#                 # Add or update with new entities
#                 for entity in results["upserted_entities"].entities:
#                     entity_dict = entity.model_dump()
#                     updated_entities[entity.identifier] = entity_dict
                
#                 existing_entities = list(updated_entities.values())
#             else:
#                 existing_entities = [entity.model_dump() for entity in results["upserted_entities"].entities]
            
#             # Store in the final results
#             final_results[f"chapter_{i}"] = results
        
#         return final_results