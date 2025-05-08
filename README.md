# SkySQL MCP Server

[![smithery badge](https://smithery.ai/badge/@skysqlinc/skysql-mcp)](https://smithery.ai/server/@skysqlinc/skysql-mcp)

This package contains everything needed to set up the SkySQL MCP (Machine Control Protocol) server, which provides a powerful interface for managing SkySQL database instances and interacting with SkyAI Agents.

## Features

- Launch and manage serverless database instances
- Interact with AI-powered database agents
- Execute SQL queries directly on SkySQL instances
- Manage database credentials and IP allowlists
- List and monitor database services

## Installation

#### Prerequisites
- Python 3.10 or higher
- A SkySQL API key

### Option 1: Run locally

#### Installation steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/skysql-mcp.git
   cd skysql-mcp
   ```

2. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. Create a `.env` file in the root directory of the cloned git repository with your SkySQL API key. Obtain API key by signing up for free on [SkySQL](https://app.skysql.com).

   ```
   SKYSQL_API_KEY=<your_skysql_api_key_here>
   ```

4. Use [MCP CLI tool](https://github.com/wong2/mcp-cli) to test the server interactively.
   ```
   npx @wong2/mcp-cli uv run python src/mcp-server/server.py
   ```

5. Configure in `Cursor.sh` manually

   For Mac/Linux:
   ```bash
   chmod +x launch.sh
   ```
Update `mcp.json`:
- command `"<full-path-to>/skysql-mcp/launch.sh"` for Mac/Linux and `"<full-path-to>\\skysql-mcp\\launch.bat"` for Windows.
- `SKYSQL_API_KEY` with your SkySQL API key

Copy the `mcp.json` included in the repo to Cursor MCP Settings

### Option 2: Installing via `Smithery.ai`

You can use Smithery.ai to test the MCP server via their UI. Follow the installation instructions from [smithery.ai](https://smithery.ai/server/@skysqlinc/skysql-mcp) 

For example, use the following command to install it in Cursor.sh IDE: 
   ```bash
   npx -y @smithery/cli@latest install @skysqlinc/skysql-mcp --client cursor --profile <your-smithery-profile> --key <your-smithery-kay>
   ```
For Windsurf:

   ```bash
   npx -y @smithery/cli@latest install @skysqlinc/skysql-mcp --client windsurf --profile <your-smithery-profile> --key <your-smithery-key>
   ```
