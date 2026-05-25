from crewai import BaseLLM
from typing import Any, Dict, List, Optional, Union
from openai import OpenAI
import os 

class CustomLLM(BaseLLM):
    def __init__(self, model: str, api_key: str, endpoint: str, temperature: Optional[float] = None, tools: Optional[List[dict]] = None):
        # IMPORTANT: Call super().__init__() with required parameters
        super().__init__(model=model, temperature=temperature)
        
        self.api_key = api_key
        self.endpoint = endpoint
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
          api_key=os.getenv("OPENROUTER_API_KEY"),
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
        # First API call with reasoning
        response = client.chat.completions.create(
          model=self.model,
          messages=messages,
          extra_body={"reasoning": {"enabled": True}}
        )
        
        # Extract the assistant message with reasoning_details
        response = response.choices[0].message   
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
        
     
        return response
    
    def supports_function_calling(self) -> bool:
        "Override if your LLM supports function calling."
        return True  # Change to False if your LLM doesn't support tools
        
    def get_context_window_size(self) -> int:
        "Return the context window size of your LLM."
        return 256000  # Adjust based on your model's actual context window



