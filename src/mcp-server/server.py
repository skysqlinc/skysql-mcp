import os
import httpx
import json
import logging
from typing import Optional, List
from fastmcp import FastMCP
from pydantic import BaseModel
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize MCP server
mcp = FastMCP("SkySQL MCP Server")

# Models for request/response handling
class ServerlessDBResponse(BaseModel):
    service_id: str
    name: str
    status: str

class AgentInfo(BaseModel):
    id: str
    name: str
    description: Optional[str]
    type: str
    status: str
    datasource_id: Optional[str]

class LlamaResponse(BaseModel):
    content: Optional[str]
    sql_text: str
    error_text: str
    col_keys: List[str]

# Cache to store agent information
_agent_cache = {}

# SkySQL API client helper
async def get_skysql_client():
    api_key = os.getenv("SKYSQL_API_KEY")
    logger.info(f"API key is configured: {bool(api_key)}")
    
    if not api_key:
        raise ValueError("SKYSQL_API_KEY not configured")
    
    return httpx.AsyncClient(
        base_url="https://api.skysql.com",
        headers={"X-API-Key": api_key, "Content-Type": "application/json"},
        timeout=30.0  # Increase timeout to 30 seconds
    )

# Tool for listing available DB agents
@mcp.tool()
async def list_agents() -> str:
    """List all available SkySQL DB agents with their capabilities"""
    async with await get_skysql_client() as client:
        try:
            response = await client.get("/copilot/v1/agent/")
            response.raise_for_status()
            agents = response.json()
            
            # Cache agent information
            global _agent_cache
            _agent_cache = {agent['id']: agent for agent in agents}
            
            # Format the output to clearly show agent names and datasource IDs
            formatted_agents = []
            for agent in agents:
                agent_info = f"Name: {agent['name']}\n"
                agent_info += f"ID: {agent['id']}\n"
                agent_info += f"Type: {agent['type']}\n"
                if 'datasource_id' in agent:
                    agent_info += f"Datasource ID: {agent['datasource_id']}\n"
                else:
                    agent_info += "Datasource ID: None\n"
                if 'description' in agent:
                    agent_info += f"Description: {agent['description']}\n"
                agent_info += "---"
                formatted_agents.append(agent_info)
            
            return "\n\n".join(formatted_agents)
        except httpx.HTTPError as e:
            return f"Failed to list agents: {str(e)}"

# Tool for launching a serverless DB
@mcp.tool()
async def launch_serverless_db(name: str, region: str = "eastus", provider: str = "azure") -> str:
    """Launch a new Serverless DB instance in SkySQL"""
    # Convert name to lowercase
    name = name.lower()
    
    async with await get_skysql_client() as client:
        try:
            payload = {
                "topology": "serverless-standalone",
                "provider": provider,
                "region": region,
                "name": name
            }
            logger.debug(f"Launching serverless DB with payload: {json.dumps(payload, indent=2)}")
            
            response = await client.post(
                "/provisioning/v1/services",
                json=payload
            )
            logger.debug(f"Launch response status: {response.status_code}")
            logger.debug(f"Launch response body: {response.text}")
            
            response.raise_for_status()
            data = response.json()
            return f"Successfully launched serverless DB '{name}' with ID: {data['id']}"
        except httpx.HTTPError as e:
            logger.error(f"Failed to launch DB: {str(e)}")
            if isinstance(e, httpx.HTTPStatusError):
                logger.error(f"Error response body: {e.response.text}")
            return f"Failed to launch DB: {str(e)}"

# Tool for deleting a DB
@mcp.tool()
async def delete_db(service_id: str) -> str:
    """Delete a DB instance from SkySQL"""
    async with await get_skysql_client() as client:
        try:
            logger.debug(f"Attempting to delete DB with ID: {service_id}")
            response = await client.delete(f"/provisioning/v1/services/{service_id}")
            logger.debug(f"Delete response status: {response.status_code}")
            logger.debug(f"Delete response body: {response.text}")
            
            response.raise_for_status()
            return f"Successfully deleted DB with ID: {service_id}"
        except httpx.HTTPError as e:
            logger.error(f"Failed to delete DB: {str(e)}")
            if isinstance(e, httpx.HTTPStatusError):
                logger.error(f"Error response body: {e.response.text}")
            return f"Failed to delete DB: {str(e)}"

# Tool for asking questions to DB agents
@mcp.tool()
async def ask_agent(agent_id: str, question: str) -> str:
    """Ask a question to a specific DB agent"""
    async with await get_skysql_client() as client:
        try:
            # Get agent info from cache
            if agent_id not in _agent_cache:
                # If agent not in cache, refresh the cache
                await list_agents()
                if agent_id not in _agent_cache:
                    return f"Agent {agent_id} not found. Please check the agent ID and try again."
            
            agent_info = _agent_cache[agent_id]
            
            # Prepare request payload
            request_payload = {
                "prompt": question,
                "agent_id": agent_id,
                "config": {}
            }
            
            # Only add datasource_id for DBA agents, not for IMDB or other agents
            if agent_info.get('type') == 'dba' and 'datasource_id' in agent_info:
                request_payload["datasource_id"] = agent_info["datasource_id"]
            
            logger.debug(f"Sending chat request with payload: {json.dumps(request_payload, indent=2)}")
            
            # Send the chat request directly
            try:
                chat_response = await client.post(
                    "/copilot/v1/chat/",
                    json=request_payload
                )
                
                # Log response details for debugging
                logger.debug(f"Response status: {chat_response.status_code}")
                logger.debug(f"Response headers: {dict(chat_response.headers)}")
                logger.debug(f"Response body: {chat_response.text}")
                
                chat_response.raise_for_status()
                chat_data = chat_response.json()
                
                # Format response with both explanation and SQL
                response_parts = []
                if chat_data["response"]["content"]:
                    response_parts.append(f"Analysis: {chat_data['response']['content']}")
                if chat_data["response"]["sql_text"]:
                    response_parts.append(f"Generated SQL:\n```sql\n{chat_data['response']['sql_text']}\n```")
                if chat_data["response"]["error_text"]:
                    response_parts.append(f"Errors: {chat_data['response']['error_text']}")
                
                return "\n\n".join(response_parts)
            except httpx.TimeoutException as e:
                logger.error(f"Request timed out after {client.timeout} seconds")
                return f"Request timed out. The API is taking longer than expected to respond. You may want to try again or check if the API is experiencing delays."
            
        except httpx.HTTPError as e:
            logger.error(f"Exception details: {str(e)}")
            if isinstance(e, httpx.HTTPStatusError):
                logger.error(f"Error response body: {e.response.text}")
            return f"Failed to get response from agent: {str(e)}"

# Prompts for common operations
@mcp.prompt()
def launch_db_prompt() -> str:
    """Create a prompt for launching a new serverless DB"""
    return """Please help me launch a new serverless database with the following specifications:
1. Name for the database (must be lowercase)
2. Region (optional, defaults to eastus)
3. Cloud provider (optional, one of: azure, aws, gcp. Defaults to azure)
"""

@mcp.prompt()
def delete_db_prompt() -> str:
    """Create a prompt for deleting a DB"""
    return """Please help me delete a database by providing:
1. The service ID of the database to delete.
2. Always confirm the deletion with me.
"""

@mcp.prompt()
def ask_agent_prompt() -> str:
    """Create a prompt for asking questions to DB agents"""
    return """I'd like to ask a question to a DB agent. Please provide:
1. The agent ID (use list_agents to see available agents)
2. Your question about database management
"""

@mcp.tool()
async def get_db_credentials(service_id: str) -> str:
    """Get the credentials for a SkySQL database instance"""
    async with await get_skysql_client() as client:
        try:
            # First get the service details to get hostname and port
            logger.debug(f"Fetching service details for ID: {service_id}")
            services_response = await client.get("/provisioning/v1/services")
            services_response.raise_for_status()
            services = services_response.json()
            
            # Find the matching service
            service = next((s for s in services if s['id'] == service_id), None)
            if not service:
                return f"Service with ID {service_id} not found"
            
            # Extract hostname and port from service details
            hostname = service.get('fqdn', 'N/A')
            endpoint = service['endpoints'][0] if service.get('endpoints') else {}
            port = endpoint.get('ports', [{}])[0].get('port', 'N/A') if endpoint.get('ports') else 'N/A'
            
            # Now get the credentials
            logger.debug(f"Fetching credentials for DB with ID: {service_id}")
            creds_response = await client.get(f"/provisioning/v1/services/{service_id}/security/credentials")
            logger.debug(f"Credentials response status: {creds_response.status_code}")
            
            creds_response.raise_for_status()
            creds_data = creds_response.json()
            
            return f"""Database Credentials:
Host: {hostname}
Port: {port}
Username: {creds_data.get('username', 'N/A')}
Password: {creds_data.get('password', 'N/A')}"""
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch credentials: {str(e)}")
            if isinstance(e, httpx.HTTPStatusError):
                logger.error(f"Error response body: {e.response.text}")
            return f"Failed to fetch credentials: {str(e)}"

@mcp.tool()
async def update_ip_allowlist(service_id: str) -> str:
    """Update the IP allowlist for a SkySQL database instance with the current IP"""
    async with await get_skysql_client() as client:
        try:
            # First get the current IP
            ip_response = await client.get("https://checkip.amazonaws.com")
            ip_response.raise_for_status()
            current_ip = ip_response.text.strip()
            
            logger.debug(f"Current IP address: {current_ip}")
            
            # Update the allowlist
            payload = {
                "ip_address": f"{current_ip}/32"
            }
            
            response = await client.post(
                f"/provisioning/v1/services/{service_id}/security/allowlist",
                json=payload
            )
            logger.debug(f"Allowlist update response status: {response.status_code}")
            
            response.raise_for_status()
            return f"Successfully added IP {current_ip} to the allowlist for service {service_id}"
        except httpx.HTTPError as e:
            logger.error(f"Failed to update IP allowlist: {str(e)}")
            if isinstance(e, httpx.HTTPStatusError):
                logger.error(f"Error response body: {e.response.text}")
            return f"Failed to update IP allowlist: {str(e)}"

@mcp.tool()
async def list_services() -> str:
    """List all available SkySQL database services"""
    async with await get_skysql_client() as client:
        try:
            logger.debug("Fetching all database services")
            response = await client.get("/provisioning/v1/services")
            response.raise_for_status()
            services = response.json()
            
            if not services:
                return "No database services found"
            
            # Format each service's information
            formatted_services = []
            for service in services:
                # Get endpoint details
                endpoint = service['endpoints'][0] if service.get('endpoints') else {}
                port = endpoint.get('ports', [{}])[0].get('port', 'N/A') if endpoint.get('ports') else 'N/A'
                
                service_info = [
                    f"Service: {service['name']}",
                    f"ID: {service['id']}",
                    f"Status: {service['status']}",
                    f"Type: {service['service_type']}",
                    f"Provider: {service['provider']}",
                    f"Region: {service['region']}",
                    f"Version: {service.get('version', 'N/A')}",
                    f"FQDN: {service.get('fqdn', 'N/A')}",
                    f"Port: {port}",
                    f"Created: {service.get('created_on', 'N/A')}",
                    "---"
                ]
                formatted_services.append("\n".join(service_info))
            
            return "\n\n".join(formatted_services)
        except httpx.HTTPError as e:
            logger.error(f"Failed to list services: {str(e)}")
            if isinstance(e, httpx.HTTPStatusError):
                logger.error(f"Error response body: {e.response.text}")
            return f"Failed to list services: {str(e)}"

if __name__ == "__main__":
    logger.info("Starting SkySQL MCP Server...")
    mcp.run() 
    