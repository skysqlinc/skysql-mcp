# SkySQL MCP Server

[![smithery badge](https://smithery.ai/badge/@skysqlinc/skysql-mcp)](https://smithery.ai/server/@skysqlinc/skysql-mcp)

This package contains everything needed to set up the SkySQL MCP (Machine Control Protocol) server, which provides a powerful interface for managing SkySQL database instances and interacting with SkyAI Agents.

## Features

- Launch and manage serverless database instances
- Interact with AI-powered database agents
- Execute SQL queries directly on SkySQL instances
- Manage database credentials and IP allowlists
- List and monitor database services

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
