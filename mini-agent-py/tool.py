from typing import Callable, List, Dict, Optional

class StandardTool:
    """
    Class to designate tools for the ReAct agent
    """
    def __init__(self, name: str, instruction: str, execute_func: Callable[[Optional[str]], str]):
        """
        Initializes a StandardTool object.

        Args:
            name (str): The unique, single-word name for the tool.
            instruction (str): A detailed instruction for the LLM of what the tool does and how to use it.
            execute_func (Callable[[Optional[str]], str]): The function that contains the tool's execution logic. It must accept an optional string input and return a string output.
        """
        if not isinstance(name, str) or not name:
            raise ValueError("Tool name must be a non-empty string.")
        if not isinstance(instruction, str) or not instruction:
            raise ValueError("Tool instruction must be a non-empty string.")
        if not callable(execute_func):
            raise TypeError("execute_func must be a callable function.")

        self.name = name
        self.instruction = instruction
        self.execute = execute_func



class ToolManager:
    """
    Manages a collection of StandardTool objects and provides an interface for the agent.
    """
    def __init__(self, tools: List[StandardTool]):
        """
        Initializes the ToolManager with a list of tool objects.
        """
        self._tools: Dict[str, StandardTool] = {tool.name: tool for tool in tools}

    def get_tool_names(self) -> List[str]:
        """Returns a list of all tool names available."""
        return list(self._tools.keys())

    def format_tool_instructions(self) -> str:
        """Formats the instructions of all tools for the agent's system prompt."""
        return "\n".join(
            [f"{tool.name}: {tool.instruction}" for tool in self._tools.values()]
        )

    def execute_tool(self, tool_name: str, action_input: Optional[str]) -> str:
        """
        Executes a specified tool with the given input.

        Args:
            tool_name (str): The name of the tool to execute.
            action_input (Optional[str]): The input to pass to the tool's function.

        Returns:
            str: The string output from the tool.
        """
        if tool_name not in self._tools:
            return f"Error: Unknown tool '{tool_name}'. Available tools are: {self.get_tool_names()}"

        tool_to_run = self._tools[tool_name]
        try:
            return tool_to_run.execute(action_input)
        except Exception as e:
            return f"Error executing tool '{tool_name}': {e}"
