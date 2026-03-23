# World Bank Documents MCP Server

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-2ea44f)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade implementation of the **Model Context Protocol (MCP)** server that exposes the [World Bank Documents & Reports API](https://search.worldbank.org/) as actionable tools for AI agents. This project utilizes **FastMCP** for tool registration , **Pydantic** for schema validation, and an **agentic CLI** to connect LLMs to live publication data.

---

## 1. Setup Instructions

### Prerequisites

- **Python 3.10 or higher**
- **uv** (Recommended for high-performance dependency management)
- **Ollama** installed and running locally for the default setup
- For the reference cloud setup: a **Groq API key** ([Groq Console](https://console.groq.com/))

### Installation

#### 1. Clone the repository

```bash
git clone https://github.com/Vinaykiran1819/wb-document-mcp-server.git
cd wb-document-mcp-server
```

#### 2. Set up the environment using `uv`
Using `uv` ensures that the project layout and local modules are correctly linked.

```bash
uv venv
uv sync
uv pip install -e .
```

### Configuration
Create a .env file in the root directory to configure your chosen provider:
Copy the example file and fill in secrets:

```bash
cp .env.example .env
```
---

## 2. Usage

### Starting the Server (Subprocess Mode)
The client script automatically starts the MCP server as a subprocess using the `stdio` transport.

```bash
uv run python src/wb_mcp/clients/cli_agent/client.py
```

Testing the Server Directly
To inspect the available tools independently of the agent loop, use the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector .venv\Scripts\python.exe -m wb_mcp.servers.docs_server.server
```

---

## 3.  LLM/SLM Choice & Justification

This project supports two high-performance models explicitly selected for their native tool-calling capabilities:.
- **Primary Choice**: **Ollama with** `qwen2.5:3b`
- **Justification:** This model was chosen as the default to provide a **fully offline, private, and zero-cost** environment. Despite its small size, `qwen2.5:3b` has excellent native tool-calling support, which is the primary driver for the MCP architecture.
- **Alternative**: **Groq (`llama-3.1-8b-instant`)** is supported for users requiring high-speed inference with zero local compute requirements.

---

## 4. Example Questions & Outputs
The following examples demonstrate the agent's ability to utilize different tools to fulfill user requests.

### Question 1: Climate Resilience in Kenya

**User:** What World Bank reports exist on climate resilience in Kenya?

**Assistant:** The World Bank has produced several reports on climate resilience in Kenya. Here are some of them:

1. **Kenya - Coastal Region Water Security and Climate Resilience Project: Resettlement Plan (Vol. 4 of 4) : Resettlement Action Plan for Mwache Multipurpose Dam Project**
2. **Kenya - Water Security and Climate Resilience Project: Audited Financial Statement – Year Ending June 30, 2014**
3. **Kenya - Coastal Region Water Security and Climate Resilience Project: Resettlement Plan (Vol. 3 of 4) : Resettlement Action Plan 1b for Mwache Multipurpose Dam Project**
4. **Disclosable Restructuring Paper - Kenya Water Security and Climate Resilience Project - P117635**      
5. **Kenya - Kenya Water Security and Climate Resilience Project: P117635 – Implementation Status Results Report (Sequence 04)**
6. **Kenya - AFRICA EAST- P117635 – Kenya Water Security and Climate Resilience Project – Procurement Plan**
7. **Kenya - AFRICA – P117635 – Kenya Water Security and Climate Resilience Project – Procurement Plan**    
8. **Kenya - AFRICA EAST- P117635 – Kenya Water Security and Climate Resilience Project – Procurement Plan**

These reports cover various aspects including the implementation, funding status, procurement plans, and resettlement actions for water security projects in Kenya.

### Question 2: Education Financing in Africa (2019-2022)

**User:** Find documents about education financing in Sub-Saharan Africa published between 2019 and 2022.

**Assistant:** There are no documents found about education financing in Sub-Saharan Africa published between 2019 and 2022.


**User:** Find documents in Kenya for the topic Education between 2019 and 2022.

**Assistant:** The provided search for documents related to education in Kenya between 2019 and 2022 resulted in the following documents:

1. **Title:** Disclosable Version of the ISR - KENYA GPE COVID 19 LEARNING CONTINUITY IN BASIC EDUCATION PROJECT - P174059 - Sequence No : 03
   - Type: Implementation Status and Results Report
2. **Title:** Kenya - GPE COVID-19 Learning Continuity in Basic Education Project
   - Type: Project Appraisal Document
3. **Title:** Disclosable Restructuring Paper - Kenya Secondary Education Quality Improvement Project - P160083
   - Type: Project Paper
4. **Title:** Disclosable Version of the ISR - KENYA GPE COVID 19 LEARNING CONTINUITY IN BASIC EDUCATION PROJECT - P174059 - Sequence No : 01
   - Type: Implementation Status and Results Report
5. **Title:** Disclosable Version of the ISR - KENYA GPE COVID 19 LEARNING CONTINUITY IN BASIC EDUCATION PROJECT - P174059 - Sequence No : 02
   - Type: Implementation Status and Results Report, Project Paper
6. **Title:** Project Information Document - KENYA GPE COVID 19 LEARNING CONTINUITY IN BASIC EDUCATION PROJECT - P174059
   - Type: Project Information Document
7. **Title:** Disclosable Restructuring Paper - Kenya GPE Primary Education Development Project - P146797   
   - Type: Project Paper, Implementation Status and Results Report
8. **Title:** Disclosable Version of the ISR - Kenya GPE Primary Education Development Project - P146797 - Sequence No : 10
   - Type: Implementation Status and Results Report
9. **Title:** Disclosable Version of the ISR - Kenya GPE Primary Education Development Project - P146797 - Sequence No : 13
   - Type: Implementation Status and Results Report
10. **Title:** Disclosable Version of the ISR - Kenya Secondary Education Quality Improvement Project - P160083 - Sequence No : 08
    - Type: Implementation Status and Results Report

These documents suggest a focus on various aspects of education projects, including learning continuity, structure reform, primary education development, and quality improvement.


### Question 4: Language Discovery

**User:** List all languages the World Bank publishes documents in.

**Assistant:** The listed languages published by the World Bank do not include any explicit values. This suggests that all documents are available in multiple languages, or there may be no specific language data currently included for these publications.

---


## 5. Project structure

```
wb-document-mcp-server/
├── src/
│   └── wb_mcp/
│       ├── agent/                          # Agentic loop and LLM provider logic
│       │   ├── orchestrator.py             # Manages multi-turn history and tool calls
│       │   ├── providers.py                # Adapters for LLMs (Ollama, Groq, etc.)
│       │   └── prompts.py
│       ├── api/                            # Core World Bank API integration
│       │   ├── client.py                   # HTTP client and raw API logic
│       │   └── schemas.py                  # Pydantic models for data validation
│       ├── clients/                        # End-user applications
│       │   └── cli_agent/                  # CLI tool for interactive natural language queries
│       │       └── client.py
│       └── servers/                        # MCP Server implementation
│           └── docs_server/                # World Bank document discovery tools
│               ├── server.py
│               └── tools.py
├── .env.example                            # Template for environment variables
├── requirements.txt                        # Project dependencies
└── README.md                               # Project documentation
```

---

## 6. MCP tools

These tools are registered in [`src/wb_mcp/servers/docs_server/tools.py`](src/wb_mcp/servers/docs_server/tools.py) on the FastMCP instance created in [`src/wb_mcp/servers/docs_server/server.py`](src/wb_mcp/servers/docs_server/server.py).

| Tool | When the agent should use it |
|------|------------------------------|
| **`search_documents`** | The user asks a **keyword or conceptual question** (“climate adaptation Kenya”, “PPI in transport”) and needs ranked matches across titles, abstracts, and metadata. Supports pagination (`rows`, `offset`), optional `lang_exact`, and field projection via comma-separated `fl`. |
| **`filter_documents`** | The user wants results constrained by **known dimensions**: country (`count_exact`), topic (`topic_exact`), document type (`docty_exact`), or **date range** (`strdate` / `enddate`). Use when filters are explicit rather than free-text. |
| **`get_document`** | The user names a **specific document ID** or the workflow already has an `id` from a prior search; fetch one record’s metadata (optionally trimmed with `fl`). |
| **`get_facets`** | The user is unsure of **valid filter values** (e.g., exact country strings, languages, types) or wants a **distribution** of values. Call before `filter_documents` to discover spelling and cardinality; optional `qterm` scopes facet counts. |

All four tools return **JSON strings** (or an error string) suitable for direct insertion into the model’s tool result channel.

---

## License

This project is released under the [MIT License](LICENSE).

---


