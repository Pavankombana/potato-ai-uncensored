"""
Autonomous Coding Agent Loop (ReAct Architecture).
Coordinates tool execution, live DuckDuckGo web search augmentation,
and multi-turn streaming interaction with the local uncensored model.
"""

import re
import json
import threading
from typing import List, Dict, Any, Optional, Callable
from core.tools import ToolExecutor
from core.search import search_duckduckgo
from core.model_client import ModelClient
from core.prompt_templates import UNCENSORED_AGENT_SYSTEM_PROMPT, format_web_search_context

TOOL_REGEX = re.compile(
    r"```tool:(?P<tool_name>[a-zA-Z0-9_\-]+)\s*\n(?P<args>\{.*?\})\s*```",
    re.DOTALL
)

XML_TOOL_REGEX = re.compile(
    r"<tool_call\s+name=[\"'](?P<tool_name>[a-zA-Z0-9_\-]+)[\"']\s*>(?P<args>\{.*?\})</tool_call>",
    re.DOTALL
)

class Agent:
    def __init__(self, model_client: ModelClient, workspace_dir: str):
        self.client = model_client
        self.tools = ToolExecutor(workspace_dir)
        self.workspace_dir = workspace_dir
        self.system_prompt = UNCENSORED_AGENT_SYSTEM_PROMPT
        self.conversation_history: List[Dict[str, str]] = []
        self._is_stopped = False
        self._thread: Optional[threading.Thread] = None

    def set_workspace(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        self.tools = ToolExecutor(workspace_dir)

    def stop(self):
        self._is_stopped = True
        self.client.abort()

    def parse_tool_call(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract tool name and JSON arguments from model response."""
        match = TOOL_REGEX.search(text)
        if match:
            try:
                name = match.group("tool_name").strip()
                args = json.loads(match.group("args").strip())
                return {"name": name, "args": args, "raw_match": match.group(0)}
            except json.JSONDecodeError:
                pass

        xml_match = XML_TOOL_REGEX.search(text)
        if xml_match:
            try:
                name = xml_match.group("tool_name").strip()
                args = json.loads(xml_match.group("args").strip())
                return {"name": name, "args": args, "raw_match": xml_match.group(0)}
            except json.JSONDecodeError:
                pass

        return None

    def run_query(
        self,
        user_prompt: str,
        web_search_enabled: bool = False,
        on_token: Optional[Callable[[str], None]] = None,
        on_tool_start: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        on_tool_end: Optional[Callable[[str, str], None]] = None,
        on_done: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
        max_iterations: int = 6
    ):
        """
        Execute agent loop in background thread.
        """
        self._is_stopped = False

        def _worker():
            try:
                # 1. Web Search Pre-fetching if enabled
                extra_context = ""
                if web_search_enabled and user_prompt.strip():
                    if on_token:
                        on_token("🌐 *Searching web for live documentation & context...*\n\n")
                    search_results = search_duckduckgo(user_prompt, max_results=4)
                    if search_results:
                        extra_context = format_web_search_context(user_prompt, search_results)
                        if on_token:
                            on_token(f"🌐 *Retrieved {len(search_results)} relevant web sources.*\n\n")

                # 2. Build initial message list
                messages: List[Dict[str, str]] = [
                    {"role": "system", "content": self.system_prompt}
                ]

                # Append history
                for m in self.conversation_history[-8:]:
                    messages.append(m)

                # Current prompt with web context if available
                current_user_content = user_prompt
                if extra_context:
                    current_user_content = f"{extra_context}\n\nUser Question:\n{user_prompt}"

                messages.append({"role": "user", "content": current_user_content})
                self.conversation_history.append({"role": "user", "content": user_prompt})

                # 3. Autonomous Tool Execution Loop (ReAct)
                iteration = 0
                final_text = ""

                while iteration < max_iterations and not self._is_stopped:
                    iteration += 1
                    turn_accumulated = []
                    turn_done_event = threading.Event()
                    turn_error = []

                    def _t_cb(tok: str):
                        turn_accumulated.append(tok)
                        if on_token:
                            on_token(tok)

                    def _d_cb(res: str):
                        turn_done_event.set()

                    def _e_cb(err: str):
                        turn_error.append(err)
                        turn_done_event.set()

                    self.client.stream_chat(
                        messages=messages,
                        token_callback=_t_cb,
                        done_callback=_d_cb,
                        error_callback=_e_cb
                    )
                    turn_done_event.wait()

                    if turn_error:
                        if on_error:
                            on_error(turn_error[0])
                        return

                    if self._is_stopped:
                        break

                    response_text = "".join(turn_accumulated)
                    final_text = response_text
                    messages.append({"role": "assistant", "content": response_text})

                    # Check for tool call
                    tool_call = self.parse_tool_call(response_text)
                    if tool_call:
                        tool_name = tool_call["name"]
                        tool_args = tool_call["args"]

                        if on_tool_start:
                            on_tool_start(tool_name, tool_args)

                        # Execute tool
                        output = self.tools.execute_tool(tool_name, tool_args)

                        if on_tool_end:
                            on_tool_end(tool_name, output)

                        if on_token:
                            on_token(f"\n\n⚙️ **[Tool: `{tool_name}` finished]**\n\n")

                        # Feed result back to agent
                        tool_message = f"[Tool Output for {tool_name}]:\n{output}\nContinue your task or provide the final code."
                        messages.append({"role": "user", "content": tool_message})
                    else:
                        # No tool call; task complete!
                        break

                self.conversation_history.append({"role": "assistant", "content": final_text})
                if on_done:
                    on_done(final_text)

            except Exception as e:
                if on_error:
                    on_error(f"Agent execution failed: {str(e)}")

        self._thread = threading.Thread(target=_worker, daemon=True)
        self._thread.start()
