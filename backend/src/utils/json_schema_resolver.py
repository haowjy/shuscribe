"""
JSON Schema Reference Resolver

This utility resolves $ref references in JSON schemas and converts them to
fully resolved schemas without references. It also detects circular references
and raises errors when they are found.

Used by the LLM service to convert Pydantic model schemas to formats that
can be understood by models that don't support structured output.
"""
import json
from typing import Any, Dict, Set, List
from copy import deepcopy


class CircularReferenceError(Exception):
    """Raised when a circular reference is detected in a JSON schema."""
    pass


class JSONSchemaResolver:
    """
    Resolves JSON schema $ref references and converts them to fully expanded schemas.
    
    This class takes a JSON schema with $ref references and resolves them to create
    a complete schema without references. It detects circular references and raises
    an error if found.
    """
    
    def __init__(self, schema: Dict[str, Any]):
        """
        Initialize the resolver with a JSON schema.
        
        Args:
            schema: The JSON schema to resolve
        """
        self.original_schema = deepcopy(schema)
        self.definitions = schema.get("$defs", {}) or schema.get("definitions", {})
        self.resolution_stack: List[str] = []
    
    def resolve(self) -> Dict[str, Any]:
        """
        Resolve all $ref references in the schema.
        
        Returns:
            A fully resolved schema without $ref references
            
        Raises:
            CircularReferenceError: If circular references are detected
        """
        return self._resolve_node(self.original_schema)
    
    def _resolve_node(self, node: Any) -> Any:
        """
        Recursively resolve a node in the schema.
        
        Args:
            node: The node to resolve (can be dict, list, or primitive)
            
        Returns:
            The resolved node
        """
        if isinstance(node, dict):
            if "$ref" in node:
                return self._resolve_reference(node["$ref"])
            else:
                # Resolve all values in the dictionary
                resolved = {}
                for key, value in node.items():
                    resolved[key] = self._resolve_node(value)
                return resolved
        elif isinstance(node, list):
            # Resolve all items in the list
            return [self._resolve_node(item) for item in node]
        else:
            # Primitive value, return as-is
            return node
    
    def _resolve_reference(self, ref: str) -> Dict[str, Any]:
        """
        Resolve a $ref reference.
        
        Args:
            ref: The reference string (e.g., "#/$defs/MyModel")
            
        Returns:
            The resolved schema object
            
        Raises:
            CircularReferenceError: If circular reference is detected
            ValueError: If reference cannot be resolved
        """
        # Check for circular reference
        if ref in self.resolution_stack:
            cycle_path = " -> ".join(self.resolution_stack + [ref])
            raise CircularReferenceError(f"Circular reference detected: {cycle_path}")
        
        # Add to resolution stack
        self.resolution_stack.append(ref)
        
        try:
            # Parse the reference
            if not ref.startswith("#/"):
                raise ValueError(f"Only internal references are supported: {ref}")
            
            path_parts = ref[2:].split("/")  # Remove "#/" and split
            
            # Navigate to the referenced definition
            current = self.original_schema
            for part in path_parts:
                if part not in current:
                    raise ValueError(f"Reference path not found: {ref}")
                current = current[part]
            
            # Resolve the referenced definition
            resolved = self._resolve_node(current)
            
            return resolved
            
        finally:
            # Remove from resolution stack
            self.resolution_stack.pop()
    
    def to_json_string(self, indent: int = 2) -> str:
        """
        Convert the resolved schema to a JSON string.
        
        Args:
            indent: Number of spaces for indentation
            
        Returns:
            JSON string representation of the resolved schema
        """
        resolved = self.resolve()
        return json.dumps(resolved, indent=indent)


def resolve_json_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to resolve a JSON schema.
    
    Args:
        schema: The JSON schema to resolve
        
    Returns:
        Fully resolved schema without $ref references
        
    Raises:
        CircularReferenceError: If circular references are detected
    """
    resolver = JSONSchemaResolver(schema)
    return resolver.resolve()


def json_schema_to_prompt_instructions(
    schema: Dict[str, Any], 
    model_name: str = "MyModel"
) -> str:
    """
    Convert a JSON schema to natural language instructions for LLM prompts.
    
    This function takes a resolved JSON schema and converts it to clear instructions
    that can be appended to prompts for models that don't support structured output.
    
    Args:
        schema: The resolved JSON schema
        model_name: Name of the model/object being described
        
    Returns:
        Natural language instructions for the LLM
    """
    try:
        resolved_schema = resolve_json_schema(schema)
    except CircularReferenceError as e:
        raise ValueError(f"Cannot convert schema with circular references to prompt: {e}")
    
    instructions = [
        f"\nYou must respond with a valid JSON object that matches the following schema for {model_name}:",
        f"```json",
        json.dumps(resolved_schema, indent=2),
        f"```",
        "",
        "Requirements:",
        "- Your response must be valid JSON",
        "- Include all required fields",
        "- Follow the exact field names and types specified",
        "- Do not include any text outside the JSON object",
        "- Ensure the JSON object is complete and properly formatted"
    ]
    
    return "\n".join(instructions)