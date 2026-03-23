# Required tool definitions
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
    async def search_documents(
        qterm: str,
        rows: int = 10,
        offset: int = 0,
        lang_exact: Optional[str] = None
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
        filters = {}
        if lang_exact:
            filters["lang_exact"] = lang_exact
            
        try:
            result = await api_client.search(qterm=qterm, rows=rows, offset=offset, **filters)
            return result.model_dump_json()
        except Exception as e:
            return f"Error executing search_documents: {str(e)}"

    @mcp.tool()
    async def filter_documents(
        count_exact: Optional[str] = None,
        topic_exact: Optional[str] = None,
        docty_exact: Optional[str] = None,
        strdate: Optional[str] = None,
        enddate: Optional[str] = None,
        rows: int = 10,
        offset: int = 0
    ) -> str:
        """
        Use this tool to find documents using strict structured metadata filters. 
        This is the REQUIRED tool for any queries involving specific date ranges (strdate/enddate), 
        countries (count_exact), topics (topic_exact), or document types (docty_exact).
        
        Args:
            count_exact: Exact country name (e.g., 'Kenya', 'Brazil').
            topic_exact: Exact topic name (e.g., 'Macroeconomics and Economic Growth').
            docty_exact: Exact document type (e.g., 'Working Paper').
            strdate: Start date for publication range in YYYY-MM-DD format.
            enddate: End date for publication range in YYYY-MM-DD format.
            rows: Number of results to return. Default is 10.
            offset: Pagination offset. Default is 0.
            
        Returns:
            A JSON string containing the filtered documents.
        """
        filters = {}
        if count_exact: filters["count_exact"] = count_exact
        if topic_exact: filters["topic_exact"] = topic_exact
        if docty_exact: filters["docty_exact"] = docty_exact
        if strdate: filters["strdate"] = strdate
        if enddate: filters["enddate"] = enddate
        
        try:
            result = await api_client.search(rows=rows, offset=offset, **filters)
            return result.model_dump_json()
        except Exception as e:
            return f"Error executing filter_documents: {str(e)}"

    @mcp.tool()
    async def get_document(id: str) -> str:
        """
        Use this tool to retrieve the complete metadata for a single specific document 
        using its unique ID.
        
        Args:
            id: The unique identifier string for the World Bank document.
            
        Returns:
            A JSON string containing the full document details.
        """
        try:
            result = await api_client.search(id=id, rows=1)
            if result.documents:
                return result.documents[0].model_dump_json()
            return f"No document found with ID: {id}"
        except Exception as e:
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
            result = await api_client.get_facets(facet_field=fct, qterm=qterm)
            return result.model_dump_json()
        except Exception as e:
            return f"Error executing get_facets: {str(e)}"