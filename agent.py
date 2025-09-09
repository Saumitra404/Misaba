import textwrap
import re
from dataclasses import dataclass
from collections.abc import Callable
from typing import List, Tuple, Optional
from tool import ToolManager

class agent:
    """
    A ReAct-style agent that uses an LLM to reason and act with tools.
    """
    sp1 = """
        Answer the questions as best you can. You have access to the following tools: {tool_list}

        Below is an explanation for how to use each tool:
        {instructions}
        
        Use the following format:
        Thought: You should always think about what to do.
        Action: The action to take, should be one of {tool_list}. (All on one line)
        Action Input: The input to the action. (All on one line)

        Additionally, if you are ready to answer, use 'Action: Answer' and 'Action Input: None'
        
        DO NOT INCLUDE ANYTHING ELSE IN YOUR RESPONSE. END IT ON 'Action Input'. IF YOU TRULY BELIEVE
        YOU DO NOT REQUIRE MORE INFORMATION TO ANSWER THE PROMPT, USE 'Action: None'. DO NOT MANUFACTURE
        INFORMATION.

        Remember, you will have multiple opportunities to perform tool calls, so only do one at a time.
        """

    ACTION_TAG = "Action:"
    ACTION_INPUT_TAG = "Action Input:"
    FINAL_ANSWER_ACTION = "Answer"
    NONE_ACTION = "None"

    def __init__(self, llm: Callable[[str, str], str], tool_manager: ToolManager, system_prompt: str = sp1):
        """
        Initializes the agent.

        Args:
            llm (Callable[[str, str], str]): The language model function to call. Must accept a system prompt and prompt, and return just the llm's response.
            tool_manager (ToolManager): The manager that handles all tool-related operations.
            system_prompt (str, optional): The system prompt template. Defaults to sp1.
        """
        self.llm = llm
        self.system_prompt = system_prompt
        self.tool_manager = tool_manager

    def generate(self, prompt: str, max_cycles: int, debug: bool = False, window_length: Optional[int] = None) -> 'agent.Response':
        """
        Runs the agent's think-act-observe loop to generate a response.
        """
        if window_length is None:
            window_length = max_cycles

        tool_list = self.tool_manager.get_tool_names()
        instructions = self.tool_manager.format_tool_instructions()
        system_message = self.system_prompt.format(tool_list=tool_list, instructions=instructions)

        scratchpad_history: List[str] = []
        debug_log = f'\nParsed prompt: {prompt} \n' if debug else ""
        base_prompt = prompt + '\nYour scratchpad is below. DO NOT REPEAT TOOL CALLS YOU HAVE ALREADY DONE, use the information on your scratchpad.'

        for i in range(max_cycles):
            scratchpad = "".join(scratchpad_history)
            current_prompt = base_prompt + '\n\nScratchpad:\n' + scratchpad
            
            try:
                response = self.llm(system_message, current_prompt)
            except Exception as e:
                raise ValueError(f'There was an issue with the LLM response: {e}')

            if debug:
                debug_log += f'\n--- Cycle {i+1} ---\n\nLLM Response:\n{textwrap.indent(response, "  ")}\n\n'

            action, action_input = self.parseActions(response)
            
            if debug:
                debug_log += f'Parsed Action: {action}\nParsed Action Input: {action_input}\n'

            gathered_info = f"\n{self.ACTION_TAG} {action}\n{self.ACTION_INPUT_TAG} {action_input}\n"
            
            if not action:
                gathered_info += "Error: Malformed response. No 'Action' was specified.\n"
                scratchpad_history.append(gathered_info)
                continue

            # Check if the agent is ready to give the final answer.
            if action.lower() in (self.FINAL_ANSWER_ACTION.lower(), self.NONE_ACTION.lower()):
                break

            # Execute the tool using the tool manager.
            action_output = self.tool_manager.execute_tool(action, action_input)
            gathered_info += f"Action Output: {action_output}\n"
            
            scratchpad_history.append(gathered_info)
            if len(scratchpad_history) > window_length:
                scratchpad_history.pop(0)

        # Final answer synthesis phase.
        final_scratchpad = "".join(scratchpad_history)
        final_prompt = base_prompt + '\n\nScratchpad:\n' + final_scratchpad
        answer = self.llm("Answer the user's prompt using the information from the scratchpad.", final_prompt)
            
        return self.Response(debug_log, final_scratchpad, answer)

    @staticmethod
    def parseActions(response: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parses the LLM's response to extract the action and action input.
        """
        action_match = re.search(rf"{agent.ACTION_TAG}\s*(\S+)", response, re.IGNORECASE)
        action_input_match = re.search(rf"{agent.ACTION_INPUT_TAG}\s*(.*)", response, re.IGNORECASE)

        action = action_match.group(1).strip().replace('"', '') if action_match else None
        action_input = action_input_match.group(1).strip().replace('"', '') if action_input_match else None

        return action, action_input

    @dataclass
    class Response:
        debug_log: str
        scratchpad: str
        response: str
