import json
import sys
from openai import AsyncOpenAI
from config import config
from services.backend import backend_client

class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=config.llm_api_key,
            base_url=config.llm_api_base_url,
        )
        self.model = config.llm_api_model
        
        # Define the tools
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_items",
                    "description": "Get a list of all available labs and tasks",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_learners",
                    "description": "Get a list of enrolled students and their groups",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_scores",
                    "description": "Get score distribution across 4 buckets (0-25, 26-50, etc) for a lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_pass_rates",
                    "description": "Get per-task average scores and attempt counts for a lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_timeline",
                    "description": "Get submissions per day for a given lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_groups",
                    "description": "Get per-group average scores and student counts for a lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_top_learners",
                    "description": "Get top N learners by score for a lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"},
                            "limit": {"type": "integer", "description": "Number of top learners to return (default 5)"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_completion_rate",
                    "description": "Get the completion rate percentage for a lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "trigger_sync",
                    "description": "Trigger ETL sync to refresh data from the autochecker",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
        ]
        
        self.available_functions = {
            "get_items": backend_client.get_items,
            "get_learners": backend_client.get_learners,
            "get_scores": backend_client.get_scores_distribution,
            "get_pass_rates": backend_client.get_pass_rates,
            "get_timeline": backend_client.get_timeline,
            "get_groups": backend_client.get_groups,
            "get_top_learners": backend_client.get_top_learners,
            "get_completion_rate": backend_client.get_completion_rate,
            "trigger_sync": backend_client.trigger_sync,
        }

    async def chat(self, user_message: str) -> str:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful teaching assistant bot. You MUST use tools to fetch data to answer the user's questions about labs, scores, and students! Whenever a user asks for data such as pass rate, scores, sync or learners, ALWAYS call the corresponding backend tool."
            },
            {"role": "user", "content": user_message}
        ]

        try:
            # Step 1: Send message and tools to LLM
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
            )
            
            response_message = response.choices[0].message
            
            # If no tool calls, just return the response
            if not response_message.tool_calls:
                return response_message.content or "I couldn't process that."
                
            # Keep looping until LLM stops calling tools (max 10 iterations to prevent infinite loops)
            iterations = 0
            while response_message.tool_calls and iterations < 10:
                iterations += 1
                
                # Manually cleanly convert assistant msg since provider is very picky
                assistant_msg = {
                    "role": "assistant",
                    "content": response_message.content or "",
                }
                if response_message.tool_calls:
                    assistant_msg["tool_calls"] = []
                    for tc in response_message.tool_calls:
                        assistant_msg["tool_calls"].append({
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments or "{}"
                            }
                        })
                messages.append(assistant_msg)
                
                tool_results_count = 0
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    args_text = tool_call.function.arguments.strip() if tool_call.function.arguments else "{}"
                    function_args = json.loads(args_text) if args_text else {}
                    
                    print(f"[tool] LLM called: {function_name}({function_args})", file=sys.stderr)
                    
                    function_to_call = self.available_functions.get(function_name)
                    if function_to_call:
                        try:
                            # Call the function (don't pass kwargs to no-arg functions)
                            if function_name in ["get_items", "get_learners", "trigger_sync"]:
                                function_response = await function_to_call()
                            else:
                                function_response = await function_to_call(**function_args)
                            result_str = json.dumps(function_response)
                            # Or better print the size
                            print(f"[tool] Result: return value of type {type(function_response)}", file=sys.stderr)
                        except Exception as e:
                            result_str = f"Error calling {function_name}: {str(e)}"
                            print(f"[tool] Error: {result_str}", file=sys.stderr)
                    else:
                        result_str = f"Error: Tool {function_name} not found"
                        print(f"[tool] Error: Tool {function_name} not found", file=sys.stderr)
                        
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": result_str,
                        }
                    )
                    tool_results_count += 1
                    
                print(f"[summary] Feeding {tool_results_count} tool results back to LLM", file=sys.stderr)
                
                # Call LLM again with tool results
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                )
                response_message = response.choices[0].message

            return response_message.content or "I finished my tasks but don't have a final answer."

        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"LLM Error: {str(e)}"

llm_service = LLMService()
