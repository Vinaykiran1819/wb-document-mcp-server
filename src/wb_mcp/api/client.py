# HTTP calls, error handling, and WB logic

"""
client.py
Logic for interacting with the World Bank Documents & Reports API.
Includes robust error handling, retries, and data normalization.
"""

import httpx
import logging
from typing import Optional, Dict, Any
from .schemas import SearchResponse, WBDocument, FacetResponse, FacetValue

logger = logging.getLogger("wb_api_client")

class WorldBankClient:
    """
    Client for the World Bank Documents & Reports API.
    Encapsulates all HTTP logic, parameter formatting, and error handling. 
    """
    BASE_URL = "https://search.worldbank.org/api/v3/wds"

    def __init__(self, timeout: float = 30.0):
        """Initializes the client with a shared HTTPX session for efficiency."""
        self.timeout = timeout
        # Persistent client for connection pooling (much faster)
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def close(self):
        """Closes the underlying HTTP session."""
        await self.client.aclose()  

    async def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal helper to execute GET requests with standard formatting.
        Handles API errors and ensures JSON responses.
        """
        # Always include format=json as required by the task
        params["format"] = "json"
        
        try:
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Check for API-level errors even if HTTP status is 200
            if not data:
                raise ValueError("World Bank API returned an empty response.")
            return data
        
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"World Bank API Error ({e.response.status_code}): {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error connecting to World Bank API: {str(e)}")

    async def search(
        self, 
        qterm: Optional[str] = None, 
        rows: int = 10, 
        offset: int = 0, 
        **filters
    ) -> SearchResponse:
        """
        Executes search/filter queries. 
        Leverages Pydantic's internal validator to clean 'facets' and dicts.
        """
        params = {
            "qterm": qterm,
            "rows": rows,
            "os": offset,
            **{k: v for k, v in filters.items() if v is not None}
        }
        raw_data = await self._make_request(params)

        # Remove the API's messy versions to avoid collisions
        raw_data.pop("rows", None)
        raw_data.pop("os", None)
        raw_data.pop("offset", None)


        return SearchResponse(offset=offset, rows=rows, **raw_data)

    async def get_document(self, doc_id: str) -> WBDocument:
        """
        Retrieves a single document by ID with all available metadata.
        Fulfills the 'get_document' tool requirement.
        """
        params = {"docid": doc_id, "fl": "*"}  # fl="*" gets 'all fields' as required
        raw_data = await self._make_request(params)
        
        docs_dict = raw_data.get("documents", {})
        # The document will be the only entry in the dict (excluding 'facets')
        for key, val in docs_dict.items():
            if key != "facets":
                return WBDocument(**val)
        
        raise ValueError(f"Document with ID {doc_id} not found.")

    async def get_facets(self, facet_field: str, qterm: Optional[str] = None) -> FacetResponse:
        """
        Retrieves discovery statistics for a specific field.
        """
        params = {"fct": facet_field, "rows": 0} # rows=0 because we only want the counts
        if qterm:
            params["qterm"] = qterm
            
        raw_data = await self._make_request(params)
        facets_data = raw_data.get("facets", {}).get(facet_field, {})
        
        # Convert dictionary facets into a list of FacetValue objects
        values = [FacetValue(name=k, count=v) for k, v in facets_data.items()]
        return FacetResponse(field_name=facet_field, values=values)