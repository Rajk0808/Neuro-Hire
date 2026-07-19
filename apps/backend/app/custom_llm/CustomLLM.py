from crewai import BaseLLM
from typing import Any, Dict, List, Optional, Union
import os
import re
import json
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
        
        # Enforce list structure for message context
        if isinstance(messages, str):
            messages = [
                {
                    "role": "system",
                    "content": "You are a specialist Job Description Architect for a recruiting platform. Your goal is to produce a complete, market-benchmarked, DEI-clean, legally compliant job description from a hiring manager's rough input. Always reason before acting. Use the available tools to gather grounded data before writing any content. Never fabricate salary ranges, skill requirements, or market data."
                },
                {
                    "role": "user",
                    "content": messages
                }
            ]
            
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )

        tools = self.tools

        # Build available_functions mapping from tools
        if not available_functions:
            available_functions = {}
            if tools:
                for tool in tools:
                    tool_name = tool.name if hasattr(tool, 'name') else str(tool)
                    available_functions[tool_name] = tool._run if hasattr(tool, '_run') else tool

        # Convert tools to OpenRouter format if supported
        tools_for_api = []
        if tools and self.supports_function_calling():
            for tool in tools:
                tool_name = tool.name if hasattr(tool, 'name') else str(tool)
                tool_description = tool.description if hasattr(tool, 'description') else "Tool"
                
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
            
            payload = {
               "model": self.model,
               "messages": messages,
               "extra_body": {"reasoning": {"enabled": True}}  # Required by gpt-oss-20b:free
            }
            
            if tools_for_api and self.supports_function_calling():
                payload["tools"] = tools_for_api
                payload["tool_choice"] = "auto"

            response = client.chat.completions.create(**payload)
            response_message = response.choices[0].message
            
            # Extract content cleanly or default to an empty string
            content_text = response_message.content or ""
            
            # Construct a clean dictionary message history layer for the model chain
            assistant_msg = {
                "role": "assistant",
                "content": content_text
            }
            
            # Process tool requests safely if provided
            has_tool_calls = hasattr(response_message, 'tool_calls') and response_message.tool_calls
            if has_tool_calls:
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
            
            # If no tool execution is required, handle text checking
            if not has_tool_calls:
                if content_text.strip():
                    return content_text  # Return plain text string back to CrewAI
                else:
                    # Model is thinking/reasoning but hasn't generated structural output text yet. Loop again.
                    print(f"[Iteration {iteration}] Model is processing reasoning phase... extending context.")
                    continue
            
            # Execute tool paths sequential loop
            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = tool_call.function.arguments
                
                clean_tool_name = re.sub(r'<\|channel\|>.*$', '', tool_name).strip()
                
                if isinstance(tool_args, str):
                    try:
                        tool_args_clean = tool_args.strip()
                        if tool_args_clean.startswith('{\n{'):
                            tool_args_clean = '{' + tool_args_clean[3:]
                        tool_args = json.loads(tool_args_clean)
                    except json.JSONDecodeError as e:
                        print(f"[JSON ERROR] Failed parsing args for '{tool_name}': {str(e)}")
                        tool_result = f"Failed to parse tool arguments for {tool_name}: {str(e)}"
                        messages.append({
                            "role": "tool",
                            "content": tool_result,
                            "tool_call_id": tool_call.id
                        })
                        continue
                
                actual_tool_name = None
                if clean_tool_name in available_functions:
                    actual_tool_name = clean_tool_name
                else:
                    for available_tool in available_functions.keys():
                        if clean_tool_name.lower() in available_tool.lower() or available_tool.lower() in clean_tool_name.lower():
                            actual_tool_name = available_tool
                            break
                
                if actual_tool_name:
                    try:
                        print(f"[INFO] Executing tool: {tool_name} -> {actual_tool_name}")
                        tool_result = available_functions[actual_tool_name](**tool_args)
                        print(f"[OK] Tool execution complete.")
                    except Exception as e:
                        tool_result = f"Tool execution error: {str(e)}"
                        print(f"[ERROR] Tool failed: {str(e)}")
                else:
                    tool_result = f"Tool {tool_name} not found in available functions."
                    print(f"[ERROR] Tool missing: {tool_name}")
                
                messages.append({
                    "role": "tool",
                    "content": str(tool_result),
                    "tool_call_id": tool_call.id
                })
        
        return messages[-1].get("content", "")

    def supports_function_calling(self) -> bool:
        return True
        
    def get_context_window_size(self) -> int:
        return 256000