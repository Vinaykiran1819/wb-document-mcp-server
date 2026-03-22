# Pydantic models for WB API responses
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class WBDocument(BaseModel):
    """
    Represents a single World Bank publication record.
    Matches the fields returned by the 'fl' parameter in the API.
    """
    id: str = Field(..., description="Unique identifier for the document")
    display_title: Optional[str] = Field(None, description="The human-readable title of the document")
    docdt: Optional[str] = Field(None, description="The publication date")
    pdfurl: Optional[str] = Field(None, description="URL to the PDF version of the report")
    count_exact: Optional[str] = Field(None, description="Country associated with the document")
    lang_exact: Optional[str] = Field(None, description="Language of the document")
    docty: Optional[str] = Field(None, description="The type/category of the document")

class SearchResponse(BaseModel):
    """
    The structured response from a search or filter query.
    Note: The 'facets' key should be handled separately from 'documents'.
    """
    total: int = Field(default=0, description="Total number of documents matching the query")
    documents: List[WBDocument] = Field(default_factory=list, description="List of matching document records")

class FacetValue(BaseModel):
    """Represents a single entry in a facet list (e.g., 'Kenya': 45 reports)."""
    name: str
    count: int

class FacetResponse(BaseModel):
    """Container for discovery tools showing distinct values for a specific field."""
    field_name: str
    values: List[FacetValue]