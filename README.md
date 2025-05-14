[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/skysqlinc-skysql-mcp-badge.png)](https://mseep.ai/app/skysqlinc-skysql-mcp)

# SkySQL MCP Server

This package contains everything needed to setup the SkySQL MCP (Machine Control Protocol) server.

## Prerequisites

- Python 3.8 or higher
- `uv` package manager (recommended) or pip
- A SkySQL API key

## Setup Instructions

1. Clone this repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   # OR using pip:
   # pip install -r requirements.txt
   ```
4. Create a `.env` file in the root directory with your SkySQL API key:
   ```
   SKYSQL_API_KEY=your_skysql_api_key_here
   ```

## Running the Tests

Use [MCP CLI tool](https://github.com/wong2/mcp-cli) to test the server.
   ```
   npx @wong2/mcp-cli python src/mcp-server/server.py
   ```
