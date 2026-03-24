# Required tool definitions
"""
tools.py
Defines the MCP tools for interacting with the World Bank Documents & Reports API.
Uses FastMCP for tool registration and Pydantic for schema-based input validation.
"""

from typing import Optional
from mcp.server.fastmcp import FastMCP
from wb_mcp.api.client import WorldBankClient


def register_tools(mcp: FastMCP, api_client: WorldBankClient) -> None:
    """
    Registers the required World Bank API tools to the FastMCP server instance.
    The docstrings below are explicitly designed to be read by an LLM to help
    it understand exactly when and how to use each tool.
    """

    @mcp.tool()
    async def search_documents( qterm: str, 
    lang_exact: Optional[str] = None, 
    rows: int = 5, 
    os: int = 0
    ) -> str:
        """
        Use this tool ONLY for broad, full-text keyword searches across World Bank publications.
        DO NOT use this tool if the user provides a specific date range, country, or topic; 
        use filter_documents instead.
        
        Args:
            qterm: The main search query (e.g., 'climate change').
            rows: Number of documents to return (pagination limit). Default is 10.
            offset: The starting index for pagination. Default is 0.
            lang_exact: Optional exact language filter (e.g., 'English', 'French').
            
        Returns:
            A JSON string containing the total count and the list of matching documents.
        """
        try:
            # We use the validated data from the Pydantic model
            result = await api_client.search(
                qterm=qterm, 
                rows=rows, 
                offset=os,
                lang_exact=lang_exact
            )
            return result.model_dump_json()
        except Exception as e:
            return f"Error executing search_documents: {str(e)}"

    @mcp.tool()
    async def filter_documents(count_exact: Optional[str] = None,
    docty_exact: Optional[str] = None,
    strdate: Optional[str] = None,
    enddate: Optional[str] = None,
    qterm: Optional[str] = None,
    rows: int = 10,
    os: int = 0
    ) -> str:
        """
        Use this tool to find documents using structured filters (dates, countries, topics).
        You can also provide a 'qterm' to search for keywords WITHIN these filters.
        
        Args:
            qterm: Optional keyword search within the filters.
            count_exact: Exact country name (e.g., 'Kenya').
            topic_exact: Exact topic name (e.g., 'Education').
            docty_exact: Exact document type (e.g., 'Working Paper').
            strdate: Start date (YYYY-MM-DD).
            enddate: End date (YYYY-MM-DD).
        """
        try:
            # Unpacking the model's data into the client
            filters = {
            "count_exact": count_exact,
            "docty_exact": docty_exact,
            "strdate": strdate,
            "enddate": enddate,
            "qterm": qterm
            }
            result = await api_client.search(rows=rows, offset=os, **filters)
            return result.model_dump_json()
        except Exception as e:
        
            return f"Error executing filter_documents: {str(e)}"

    @mcp.tool()
    async def get_document(id: str) -> str:
        """
        Use this tool to retrieve the complete metadata for a single specific document 
        using its unique ID. This provides 'all fields' available.
        
        Args:
            id: The unique identifier string for the World Bank document.
            
        Returns:
            A JSON string containing the full document details.
        """
        try:
            # We use the specialized get_document method from our client
            # which requests 'all fields' (fl="*") automatically.
            result = await api_client.get_document(doc_id=id)
            
            # Since result is a WBDocument object, we dump it to JSON for the LLM
            return result.model_dump_json()
            
        except ValueError as ve:
            # Catches "Document not found" from the client logic
            return f"Error executing get_document: {str(ve)}"
        except Exception as e:
            # Catches unexpected network/API errors
            return f"Error retrieving document: {str(e)}"


    @mcp.tool()
    async def get_facets(fct: str, qterm: Optional[str] = None) -> str:
        """
        Discovery tool to find distinct metadata values. Use this BEFORE filter_documents 
        if you are unsure of the exact spelling of a country, topic, or document type.
        
        Args:
            fct: The field to discover (e.g., 'count_exact', 'topic_exact', 'docty_exact').
            qterm: Optional keyword search to narrow down the facet scope.
            
        Returns:
            A JSON string listing the distinct values and their frequency counts.
        """
        try:
            # We pass the fct and optional qterm from the validated args
            result = await api_client.get_facets(
                facet_field=fct, 
                qterm=qterm
            )
            return result.model_dump_json()
        except Exception as e:
            return f"Error executing get_facets: {str(e)}"