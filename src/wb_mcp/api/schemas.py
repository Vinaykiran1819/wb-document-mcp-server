# Pydantic models for WB API responses

"""
schemas.py

This module defines the Pydantic v2 data models used for validating and 
structuring data exchanged between the World Bank Documents & Reports API 
and the MCP Server.

These models ensure type safety, provide clear metadata for the LLM's 
tool-calling logic, and handle the dynamic nature of the WB API responses.
"""

from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import List, Optional, Dict, Any

class WBDocument(BaseModel):
    """
    Represents a single World Bank publication record.
    This model captures the core metadata fields required for searching, 
    filtering, and detailed document retrieval.
    """
    # Essential for the get_document tool
    id: str = Field(..., description="Unique identifier for the document")

    # Core fields from the example
    display_title: Optional[str] = Field(None, description="The human-readable title of the document")
    docdt: Optional[str] = Field(None, description="The publication date")
    pdfurl: Optional[str] = Field(None, description="URL to the PDF version of the report")

    # Fields for full-text search (qterm) and grounding
    abstracts: Optional[str] = Field(None, description="A summary or abstract of the document's content")
    projn: Optional[str] = Field(None, description="The name of the associated World Bank project")

    # Fields for filter_documents and get_facets tools
    count_exact: Optional[str] = Field(None, description="The exact country name associated with the document")
    lang_exact: Optional[str] = Field(None, description="Language of the document is published in")
    docty: Optional[str] = Field(None, description="The type/category of the document")
    topic: Optional[str] = Field(None, description="The primary topic or subject matter")

    # Additional high-value metadata from the World Bank API
    txturl: Optional[str] = Field(None, description="URL to the plain-text version (ideal for LLM reading)")
    authr: Optional[str] = Field(None, description="The authors or department responsible for the report")
    geo_reg: Optional[str] = Field(None, description="The broader geographic region (e.g., Sub-Saharan Africa)")

    # Configuration for API compatibility and the 'all fields' requirement 
    model_config = ConfigDict(
        extra="ignore",  # Discards technical noise to save LLM context space
        populate_by_name=True
    )
    @model_validator(mode='before')
    @classmethod
    def unwrap_cdata(cls, data: Any) -> Any:
        """
        World Bank API often wraps text in {"cdata!": "text"}.
        This helper unwraps them automatically for all fields.
        """
        if isinstance(data, dict):
            for field, value in data.items():
                if isinstance(value, dict) and 'cdata!' in value:
                    data[field] = value['cdata!']
        return data


class SearchResponse(BaseModel):
    """
    The structured response from a search or filter query.
    Handles the WB API quirk of returning documents in a dict with a 'facets' key.
    """
    model_config = ConfigDict(extra="ignore")
    
    total: int = Field(default=0, description="Total number of documents matching the query")
    offset: int = Field(default=0, description="The starting point (os) of this result set")
    rows: int = Field(default=0, description="Number of results returned in this batch")
    documents: List[WBDocument] = Field(default_factory=list, description="List of matching document records")

    @model_validator(mode='before')
    @classmethod
    def handle_wb_api_structure(cls, data: Any) -> Any:
        """
        Cleans the API response by converting the 'documents' dict to a list
        and removing the 'facets' key as required by the task.
        """
        if isinstance(data, dict) and 'documents' in data:
            docs_data = data['documents']
            
            # If the API returned a dictionary (standard for WB API)
            if isinstance(docs_data, dict):
                # Filter out the 'facets' key and convert values to a list
                clean_list = [
                    val for key, val in docs_data.items() 
                    if key != 'facets'
                ]
                data['documents'] = clean_list
                
        return data


class FacetValue(BaseModel):
    """
    Represents a single entry in a facet list.
    Example: name='Kenya', count=45.
    """
    name: str = Field(..., description="The distinct value of the field (e.g., 'Kenya' or 'English')")
    count: int = Field(..., description="The number of documents that match this specific value")


class FacetResponse(BaseModel):
    """
    Container for discovery tools showing all distinct values for a field.
    Used by the get_facets tool to help the LLM understand available filters.
    """
    model_config = ConfigDict(extra="ignore")

    field_name: str = Field(..., description="The name of the field being faceted (e.g., 'count_exact')")
    values: List[FacetValue] = Field(default_factory=list, description="The list of names and counts found for this field")
