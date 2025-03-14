import asyncio
import sys
import json
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent  
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from dotenv import load_dotenv
import os

load_dotenv(override=True)

python_path = sys.executable

def load_mcp_config(config_file="mcp_config.json"):
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in configuration file '{config_file}'.")
        sys.exit(1)

def load_system_prompt(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Warning: System prompt file '{file_path}' not found. Using default prompt.")
        return None
    except Exception as e:
        print(f"Error reading system prompt file: {e}")
        return None

def get_model_from_config(config):
    settings = config.get("settings", {})
    model_name = settings.get("model", "gpt-4o")
    return ChatOpenAI(model=model_name, openai_api_key=os.getenv("OPENAI_API_KEY"))

async def main(user_input):
    mcp_config = load_mcp_config()
    
    model = get_model_from_config(mcp_config)
    
    system_prompt_path = mcp_config.get("settings", {}).get("system_prompt_path")
    if system_prompt_path:
        system_message = load_system_prompt(system_prompt_path)
    
    if not system_prompt_path or system_message is None:
        system_message = """You are an advanced AI assistant with access to various tools.
        Your goal is to provide accurate, helpful information by using the appropriate tools.
        Take your time to think step by step before providing your final answer."""
    
    async with MultiServerMCPClient() as client:
        server_statuses = {}
        for server_name, server_config in mcp_config.items():
            if server_name != "settings" and server_config.get("active", False):
                script_path = server_config["script"]
                try:
                    print(f"Starting server '{server_name}' with script '{script_path}'...")
                    
                    required_env_vars = server_config.get("required_env_vars", [])
                    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
                    if missing_vars:
                        print(f"Warning: Missing required environment variables for {server_name}: {', '.join(missing_vars)}")
                        continue
                    
                    await client.connect_to_server(
                        server_name,
                        command=python_path,
                        args=[script_path],
                        encoding_error_handler=server_config.get("encoding_error_handler", "ignore"),
                    )
                    server_statuses[server_name] = "Connected"
                    print(f"Server '{server_name}' started successfully.")
                except Exception as e:
                    server_statuses[server_name] = f"Failed: {str(e)}"
                    print(f"Error starting server '{server_name}': {e}")
        
        print("\nServer Status Summary:")
        for server, status in server_statuses.items():
            print(f"  - {server}: {status}")
        
        if not any(status == "Connected" for status in server_statuses.values()):
            print("No servers connected successfully. Exiting.")
            return
      
        agent = create_react_agent(
            model, 
            client.get_tools(), 
            state_modifier=system_message
        )

        review_requested = await agent.ainvoke(
            debug=True,
            input={
                "messages": [HumanMessage(content=user_input)],
            },
        )

        parsed_data = parse_ai_messages(review_requested)
        for ai_message in parsed_data:
            print(ai_message)

def parse_ai_messages(data):
    messages = dict(data).get('messages', [])
    formatted_ai_responses = []

    for message in messages:
        if isinstance(message, AIMessage):
            formatted_message = f"### AI Response:\n\n{message.content}\n\n"
            formatted_ai_responses.append(formatted_message)

    return formatted_ai_responses

if __name__ == "__main__":
    user_query = "use advanced web search and Get me the latest news about Gemma 3 AI model using web search"
    asyncio.run(main(user_query))