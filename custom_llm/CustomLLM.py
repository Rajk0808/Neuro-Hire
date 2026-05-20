"""from crewai import BaseLLM
from typing import Any, Dict, List, Optional, Union
import requests

class CustomLLM(BaseLLM):
    def __init__(self, model: str, api_key: str, endpoint: str, temperature: Optional[float] = None):
        # IMPORTANT: Call super().__init__() with required parameters
        super().__init__(model=model, temperature=temperature)
        
        self.api_key = api_key
        self.endpoint = endpoint
        
    def call(
        self,
        messages: Union[str, List[Dict[str, str]]],
        tools: Optional[List[dict]] = None,
        callbacks: Optional[List[Any]] = None,
        available_functions: Optional[Dict[str, Any]] = None,
    ) -> Union[str, Any]:
        "Call the LLM with the given messages."
        # Convert string to message format if needed
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        # Prepare request
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }
        
        # Add tools if provided and supported
        if tools and self.supports_function_calling():
            payload["tools"] = tools
        
        # Make API call
        response = requests.post(
            self.endpoint,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
        
    def supports_function_calling(self) -> bool:
        "Override if your LLM supports function calling."
        return True  # Change to False if your LLM doesn't support tools
        
    def get_context_window_size(self) -> int:
        "Return the context window size of your LLM."
        return 256000  # Adjust based on your model's actual context window
    
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="<OPENROUTER_API_KEY>",
)

# First API call with reasoning
response = client.chat.completions.create(
  model="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
  messages=[
          {
            "role": "user",
            "content": "How many r's are in the word 'strawberry'?"
          }
        ],
  extra_body={"reasoning": {"enabled": True}}
)

# Extract the assistant message with reasoning_details
response = response.choices[0].message

# Preserve the assistant message with reasoning_details
messages = [
  {"role": "user", "content": "How many r's are in the word 'strawberry'?"},
  {
    "role": "assistant",
    "content": response.content,
    "reasoning_details": response.reasoning_details  # Pass back unmodified
  },
  {"role": "user", "content": "Are you sure? Think carefully."}
]

# Second API call - model continues reasoning from where it left off
response2 = client.chat.completions.create(
  model="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
  messages=messages,
  extra_body={"reasoning": {"enabled": True}}
)"""

from crewai import BaseLLM
from typing import Any, Dict, List, Optional, Union
import requests
import os
from openai import OpenAI
class CustomLLM(BaseLLM):
    def __init__(self, model: str, temperature: Optional[float] = None, tools: Optional[List[dict]] = None):
        super().__init__(model=model, temperature=temperature)
        self.tools = tools

    def call(
        self,
        messages: Union[str, List[Dict[str, str]]],
        tools: Optional[List[dict]] = None,
        callbacks: Optional[List[Any]] = None,
        available_functions: Optional[Dict[str, Any]] = None,
        from_task = None,
        from_agent = None,
        response_model=None
    ) -> Union[str, Any]:
        if isinstance(messages, str):
            messages = [
                {
                    "role" : "system",
                    "content" : "You are a specialist Job Description Architect for a recruiting platform. Your goal is to produce a complete, market-benchmarked, DEI-clean, legally compliant job description from a hiring manager's rough input. Always reason before acting. Use the available tools to gather grounded data before writing any content. Never fabricate salary ranges, skill requirements, or market data."
                },
                {
                    "role" : "user",
                    "content" : messages
                }
            ]
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key = os.getenv("OPENROUTER_API_KEY")
        )

        tools = self.tools

        # Build available_functions mapping from tools
        if not available_functions:
            available_functions = {}
            if tools:
                for tool in tools:
                    # For BaseTool objects, the name is in the 'name' attribute
                    tool_name = tool.name if hasattr(tool, 'name') else str(tool)
                    # The callable is the _run method
                    available_functions[tool_name] = tool._run if hasattr(tool, '_run') else tool

        # Convert tools to OpenRouter format if they're BaseTool objects
        tools_for_api = []
        if tools and self.supports_function_calling():
            for tool in tools:
                tool_name = tool.name if hasattr(tool, 'name') else str(tool)
                tool_description = tool.description if hasattr(tool, 'description') else "Tool"
                
                # Get the schema from args_schema if available
                schema = {}
                if hasattr(tool, 'args_schema') and tool.args_schema:
                    try:
                        schema = tool.args_schema.model_json_schema()
                    except:
                        schema = {}
                
                tools_for_api.append({
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "description": tool_description,
                        "parameters": schema if schema else {"type": "object", "properties": {}}
                    }
                })

        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Build request payload
            payload = {
               "model": self.model,
               "messages": messages,
               "extra_body": {"reasoning": {"enabled": True}}
            }
            
            # Include tools if provided and supported
            if tools_for_api and self.supports_function_calling():
                payload["tools"] = tools_for_api
                payload["tool_choice"] = "auto"

            response = client.chat.completions.create(**payload)
            response_message = response.choices[0].message
            
            # Add assistant response to messages in CrewAI-compatible format
            assistant_msg = {
                "role": "assistant",
                "content": response_message.content or ""
            }
            
            # Only add tool_calls if they exist and convert to dict format
            if hasattr(response_message, 'tool_calls') and response_message.tool_calls:
                # Convert tool_calls to dictionary format that CrewAI expects
                tool_calls_list = []
                for tc in response_message.tool_calls:
                    tool_calls_list.append({
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    })
                assistant_msg["tool_calls"] = tool_calls_list
            
            messages.append(assistant_msg)
            
            # Check if there are tool calls
            if not hasattr(response_message, 'tool_calls') or not response_message.tool_calls:
                # No more tool calls, return the final response
                return response_message
            
            # Execute tool calls
            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = tool_call.function.arguments
                
                # Clean tool name: remove channel suffixes like <|channel|>json, <|channel|>commentary
                import re
                clean_tool_name = re.sub(r'<\|channel\|>.*$', '', tool_name).strip()
                
                # Parse arguments if it's a string
                if isinstance(tool_args, str):
                    import json
                    try:
                        # Clean up malformed JSON (remove duplicate opening braces, etc.)
                        tool_args_clean = tool_args.strip()
                        if tool_args_clean.startswith('{\n{'):
                            tool_args_clean = '{' + tool_args_clean[3:]
                        tool_args = json.loads(tool_args_clean)
                    except json.JSONDecodeError as e:
                        print(f"[JSON ERROR] JSON Parse Error for tool '{tool_name}':")
                        print(f"   Raw arguments: {repr(tool_args)}")
                        print(f"   Error: {str(e)}")
                        tool_result = f"Failed to parse tool arguments for {tool_name}: {str(e)}"
                        messages.append({
                            "role": "tool",
                            "content": tool_result,
                            "tool_call_id": tool_call.id
                        })
                        continue
                
                # Try to find the tool (exact match first, then fuzzy match)
                actual_tool_name = None
                if clean_tool_name in available_functions:
                    actual_tool_name = clean_tool_name
                else:
                    # Fuzzy matching: try to find a tool with similar name
                    for available_tool in available_functions.keys():
                        if clean_tool_name.lower() in available_tool.lower() or available_tool.lower() in clean_tool_name.lower():
                            actual_tool_name = available_tool
                            break
                
                # Execute the tool
                if actual_tool_name:
                    try:
                        print(f"[INFO] Executing tool: {tool_name} -> {actual_tool_name}")
                        tool_result = available_functions[actual_tool_name](**tool_args)
                        print(f"[OK] Tool executed: {tool_name} -> {actual_tool_name}")
                    except Exception as e:
                        tool_result = f"Tool execution error: {str(e)}"
                        print(f"[ERROR] Tool error: {tool_name} - {str(e)}")
                else:
                    tool_result = f"Tool {tool_name} not found in available functions. Available: {list(available_functions.keys())}"
                    print(f"[ERROR] Tool not found: {tool_name}")
                
                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "content": str(tool_result),
                    "tool_call_id": tool_call.id
                })
        
        # If we exit the loop, return the last response
        return response_message
        
    def supports_function_calling(self) -> bool:
        # Return True if your LLM supports function calling, otherwise False
        return True
        
    def get_context_window_size(self) -> int:
        # Return the context window size of your LLM
        return 256000 