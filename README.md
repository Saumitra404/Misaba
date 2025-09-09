# mini-agent-py: A ReAct Agent Framework

This project provides a lightweight and extensible Python library for the implementation of ReAct-style agents. The framework is designed to be LLM-agnostic and allows for the straightforward integration of custom tools.

## Quickstart

#### 1. Clone the repository

Download it from github directly or use ```git clone https://github.com/Saumitra404/Misaba.git```

#### 2. Set up your LLM

Here is an example with Ollama's qwen3 model. We create a wrapper function for the LLM which takes a system prompt and message as its parameters and returns the raw string output of the LLM's response:
```python
import ollama
# Make sure you have the model pulled locally: ollama pull qwen3
def ollama_func(system: str, prompt: str) -> str:
    """A wrapper function for the Ollama chat endpoint."""
    response = ollama.chat(
        model='qwen3',
        messages=[
           {'role': 'system', 'content': system},
            {'role': 'user', 'content': prompt},
        ]
    )
    return response['message']['content']
```

Or, if we were using an API:
```
import <API PACKAGE>
def claude-func(system: str, prompt: str) -> str:
  ...
```
  
#### 3. Set up your tools

The library comes with a ToolManager to handle all tool-related operations, and a few pre-built tools for you to use out of the box.
```
from Misaba import agent, ToolManager
from Misaba.tools import calculate_tool, datetime_tool, gmail_tool
1. Create a list of the tools you want the agent to have.
# Note: The gmail_tool requires extra setup (see documentation).
tools = [calculate_tool, datetime_tool, gmail_tool]
# 2. Instantiate the ToolManager with your list of tools.
tool_manager = ToolManager(tools=tools)
```

