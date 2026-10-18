"""
Agent tool execution engine.
Provides file manipulation (read, write, edit, list) and shell command execution
in the user's workspace directory, plus web search tool integration.
"""

import os
import subprocess
from typing import Dict, Any, Optional
from core.search import search_duckduckgo

class ToolExecutor:
    def __init__(self, workspace_dir: str):
        self.workspace_dir = os.path.abspath(workspace_dir)

    def resolve_path(self, path: str) -> str:
        """Resolve a relative or absolute path within the workspace."""
        if not path:
            return self.workspace_dir
        if os.path.isabs(path):
            return os.path.abspath(path)
        return os.path.abspath(os.path.join(self.workspace_dir, path))

    def read_file(self, path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
        abs_path = self.resolve_path(path)
        if not os.path.exists(abs_path):
            return f"Error: File '{path}' does not exist."
        if os.path.isdir(abs_path):
            return f"Error: '{path}' is a directory, not a file."

        try:
            with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            total_lines = len(lines)
            s = max(1, start_line) if start_line is not None else 1
            e = min(total_lines, end_line) if end_line is not None else total_lines

            if s > total_lines:
                return f"File '{path}' has only {total_lines} lines (requested start {s})."

            selected_lines = lines[s - 1:e]
            numbered = [f"{i + s:4d} | {line}" for i, line in enumerate(selected_lines)]
            header = f"=== File: {path} (Lines {s}-{e} of {total_lines}) ===\n"
            return header + "".join(numbered)
        except Exception as err:
            return f"Error reading file '{path}': {str(err)}"

    def write_file(self, path: str, content: str) -> str:
        abs_path = self.resolve_path(path)
        try:
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)
            line_count = len(content.splitlines())
            byte_size = len(content.encode("utf-8"))
            return f"Success: Wrote {line_count} lines ({byte_size} bytes) to '{path}'."
        except Exception as err:
            return f"Error writing file '{path}': {str(err)}"

    def edit_file(self, path: str, target_content: str, replacement_content: str) -> str:
        abs_path = self.resolve_path(path)
        if not os.path.exists(abs_path):
            return f"Error: File '{path}' does not exist."

        try:
            with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                current_text = f.read()

            count = current_text.count(target_content)
            if count == 0:
                return f"Error: Target content was not found in '{path}'. Please check whitespace and line breaks."
            if count > 1:
                return f"Error: Target content matches {count} locations in '{path}'. Provide a more specific target snippet."

            new_text = current_text.replace(target_content, replacement_content, 1)
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(new_text)

            return f"Success: Successfully edited '{path}'."
        except Exception as err:
            return f"Error editing file '{path}': {str(err)}"

    def list_dir(self, path: str = ".", recursive: bool = False) -> str:
        abs_path = self.resolve_path(path)
        if not os.path.exists(abs_path):
            return f"Error: Directory '{path}' does not exist."
        if not os.path.isdir(abs_path):
            return f"Error: '{path}' is a file, not a directory."

        ignored_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea", ".vscode"}
        lines = [f"=== Directory Listing: {path} ==="]

        if not recursive:
            try:
                entries = sorted(os.scandir(abs_path), key=lambda e: (not e.is_dir(), e.name.lower()))
                for e in entries:
                    if e.name in ignored_dirs:
                        continue
                    if e.is_dir():
                        lines.append(f"[DIR]  {e.name}/")
                    else:
                        size = e.stat().st_size
                        lines.append(f"[FILE] {e.name:<30} ({size} bytes)")
            except Exception as err:
                return f"Error listing directory: {str(err)}"
        else:
            try:
                for root, dirs, files in os.walk(abs_path):
                    dirs[:] = [d for d in dirs if d not in ignored_dirs]
                    rel_root = os.path.relpath(root, abs_path)
                    prefix = "" if rel_root == "." else f"{rel_root}/"
                    for d in sorted(dirs):
                        lines.append(f"[DIR]  {prefix}{d}/")
                    for f in sorted(files):
                        lines.append(f"[FILE] {prefix}{f}")
                    if len(lines) > 200:
                        lines.append("... (truncated: directory has over 200 items)")
                        break
            except Exception as err:
                return f"Error walking directory: {str(err)}"

        return "\n".join(lines)

    def run_command(self, command: str, cwd: Optional[str] = None, timeout: int = 60) -> str:
        exec_cwd = self.resolve_path(cwd) if cwd else self.workspace_dir
        if not os.path.exists(exec_cwd):
            exec_cwd = self.workspace_dir

        try:
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-Command", command],
                cwd=exec_cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False
            )
            output = []
            if proc.stdout:
                output.append(f"[STDOUT]\n{proc.stdout.strip()}")
            if proc.stderr:
                output.append(f"[STDERR]\n{proc.stderr.strip()}")
            output.append(f"[EXIT CODE]: {proc.returncode}")
            return "\n".join(output) if output else "[Command finished with no output (Exit Code 0)]"
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {timeout} seconds."
        except Exception as err:
            return f"Error running command: {str(err)}"

    def execute_tool(self, name: str, args: Dict[str, Any]) -> str:
        """Route tool calls safely to appropriate methods."""
        if name == "read_file":
            return self.read_file(args.get("path", ""), args.get("start_line"), args.get("end_line"))
        elif name == "write_file":
            return self.write_file(args.get("path", ""), args.get("content", ""))
        elif name == "edit_file":
            return self.edit_file(args.get("path", ""), args.get("target_content", ""), args.get("replacement_content", ""))
        elif name == "list_dir":
            return self.list_dir(args.get("path", "."), args.get("recursive", False))
        elif name == "run_command":
            return self.run_command(args.get("command", ""), args.get("cwd"))
        elif name == "web_search":
            query = args.get("query", "")
            results = search_duckduckgo(query, max_results=5)
            if not results:
                return f"No search results found for '{query}'."
            formatted = [f"=== Web Search Results for: '{query}' ==="]
            for i, r in enumerate(results, 1):
                formatted.append(f"[{i}] {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet']}\n")
            return "\n".join(formatted)
        else:
            return f"Unknown tool: '{name}'"
