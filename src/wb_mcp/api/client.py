# HTTP calls, error handling, and WB logic
import httpx
from typing import Optional, Dict, Any
from .schemas import SearchResponse, WBDocument, FacetResponse, FacetValue

class WorldBankClient:
    """
    A professional SDK-style client for the World Bank Documents & Reports API.
    Encapsulates all HTTP logic, parameter formatting, and error handling.
    """
    BASE_URL = "https://search.worldbank.org/api/v3/wds"

    def __init__(self, timeout: float = 30.0):
        """Initializes the client with a shared HTTPX session for efficiency."""
        self.timeout = timeout

    async def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal helper to execute GET requests with standard formatting.
        Handles API errors and ensures JSON responses.
        """
        # Always include format=json as required by the task
        params["format"] = "json"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(self.BASE_URL, params=params)
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
        Executes a full-text search with optional structured filtering.
        Maps directly to 'search_documents' and 'filter_documents' tools.
        """
        params = {
            "qterm": qterm,
            "rows": rows,
            "os": offset
        }
        # Merge additional filters like count_exact or docty_exact
        params.update(filters)
        
        raw_data = await self._make_request(params)
        
        # The API returns documents as a dict where keys are IDs. 
        # We must extract them and ignore the 'facets' key.
        documents_dict = raw_data.get("documents", {})
        docs_list = []
        
        for key, value in documents_dict.items():
            if key != "facets":
                docs_list.append(WBDocument(**value))
                
        return SearchResponse(
            total=int(raw_data.get("total", 0)),
            documents=docs_list
        )

    async def get_facets(self, facet_field: str, qterm: Optional[str] = None) -> FacetResponse:
        """
        Retrieves distinct values for a field to help with 'discovery'.
        Example: Listing all 'count_exact' values to see which countries have data.
        """
        params = {"fct": facet_field}
        if qterm:
            params["qterm"] = qterm
            
        raw_data = await self._make_request(params)
        facets_data = raw_data.get("facets", {}).get(facet_field, {})
        
        # Convert dictionary facets into a list of FacetValue objects
        values = [FacetValue(name=k, count=v) for k, v in facets_data.items()]
        return FacetResponse(field_name=facet_field, values=values)