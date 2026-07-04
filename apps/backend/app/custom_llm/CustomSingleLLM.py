from crewai import BaseLLM
from typing import Any, Dict, List, Optional, Union
from openai import OpenAI
import os 
import httpx

class CustomLLM(BaseLLM):
    def __init__(self, model: str, api_key: str, endpoint: str, temperature: Optional[float] = None, tools: Optional[List[dict]] = None, human_feedback: Optional[str] = None):
        # IMPORTANT: Call super().__init__() with required parameters
        super().__init__(model=model, temperature=temperature)
        
        self.api_key = api_key
        self.endpoint = endpoint
        self.tools = tools
        self.human_feedback = human_feedback
    async def call(
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
                    "content" : "You are a specialist Job Description Architect for a recruiting platform. Your goal is to produce a complete, market-benchmarked, DEI-clean, legally compliant job description from a hiring manager's rough input. Always reason before acting. Use the available tools to gather grounded data before writing any content. Never fabricate salary ranges, skill requirements, or market data. Expected output is a JSON object with the following keys: 'jd_draft', 'dei_audit', 'salary_benchmark', 'competitor_analysis', 'legal_compliance' all as key-value pairs. If you need to call a tool, use the tool's name as the key and the tool's output as the value. If you need to ask for human feedback, use 'human_feedback' as the key and the feedback request as the value."
                },
                {
                    "role" : "user",
                    "content" : messages
                }
            ]
    
        client = OpenAI(
          base_url=self.endpoint,
          api_key=self.api_key,
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
                    available_functions[tool_name] = tool._arun if hasattr(tool, '_arun') else tool
        # First API call with reasoning
        response = await client.chat.completions.create(
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



