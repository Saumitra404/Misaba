# mini-agent-py: A ReAct Agent Framework

This project provides a lightweight and extensible Python library for the implementation of ReAct-style agents. The framework is designed to be LLM-agnostic and allows for the straightforward integration of custom tools.

### A Quick Note:
The main reason I created this library to build agents was that I was having trouble getting smaller local models (run on my laptop) to work with langchain and other agent frameworks. This framework is very lightweight and seems to work reasonably well with models like phi4 (14 billion parameters) and qwen3:8b in my testing.

## Included Features

#### 1. `agent` Class: An agent connected to a specified LLM (or SLM) and set of tools
Creating an agent requires passing in an llm wrapper function which recieves a system and main prompt and returns the raw string response (system: str, prompt: str) -> str), as well as a ToolManager object (see below).

The agent has a generate function which requires a prompt, max_cycles which is the maximum number of cycles the agent will run before being forced to answer. Optionally, the generate can also be put into debug mode with debug=True, and window_length which manages the context window of the LLM (for large numbers of cycles)
#### 2. `StandardTool` Class: Used to create custom tools
This class represents a tool to be used by the agent. Each tool needs a name (MUST NOT CONTAIN SPACES), a clear set of instructions for the agent, which may include examples, and the function which runs when the tool is called. Tool functions can optionally take a string input, and must return a string input.

Misaba comes with 3 pre-built tools: a calculator, a datetime tool, and a tool to access gmail. See the quickstart guide or look in the tools folder for more information.
#### 3. `ToolManager` Class: Used to manage all the tools for the agent
Simply put the StandardTool objects into a list.
```python
from Misaba.tools import StandardTool, ToolManager

all_tools = [gmail_tool, calc_tool, datetime_tool]
tool_manager = ToolManager(tools=all_tools)
```
## Quickstart

#### 1. Clone the repository

Download it from github directly or use 
```git clone https://github.com/Saumitra404/Misaba.git```

#### 2. Set up your LLM

Here is an example with Ollama's qwen3 model. We create a wrapper function for the LLM which takes a system prompt and message as its parameters and returns the raw string output of the LLM's response:
```python
import ollama
# Make sure you have the model pulled locally: ollama pull qwen3
`pip install ollama
def llm-func(system: str, prompt: str) -> str:
    return ollama.generate(model='qwen3', system=system, prompt=prompt).response`
```

Or, if we were using an API:
```python
import <API PACKAGE>
def claude-func(system: str, prompt: str) -> str:
  ...
```
From testing I've found this to work well with small models like Qwen3:8b and Phi4.
  
#### 3. Set up your tools

The library comes with a ToolManager to handle all tool-related operations, and a few pre-built tools for you to use out of the box.
```python
from Misaba import agent, ToolManager
from Misaba.tools import calculate_tool, datetime_tool, gmail_tool

# 1. Create a list of the tools you want the agent to have.
tools = [calculate_tool, datetime_tool, gmail_tool]

# 2. Instantiate the ToolManager with your list of tools.
tool_manager = ToolManager(tools=tools)
```

##### Note that for the gmail tool to work, you will to install the required dependencies:
```pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib```

#### 4. Instantiate your agent and run it

```python
my_agent = agent(llm=ollama_func, tool_manager=tool_manager)
prompt = input("Enter your question: ")

response = my_agent.generate(prompt, max_cycles=5, debug=True)
print("\n--- DEBUG LOG ---")
print(response.debug_log)
print("\n--- FINAL ANSWER ---")
print(response.response)

