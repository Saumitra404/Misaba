from tool import StandardTool
import math

def calculate(expression: str) -> str:
    """Evaluates a mathematical expression."""
    allowed_funcs = {
        "sqrt": math.sqrt,
        "pow": math.pow,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "radians": math.radians,
    }
    safe_env = {
        "__builtins__": None,
        **allowed_funcs
    }
    try:
        result = eval(expression, safe_env)
        return str(result)
    except Exception as e:
        return f"Error: Invalid expression. {e}"

calculate_tool = StandardTool(
    name='calculate',
    instruction="""This tool evaluates mathematical expressions. It supports standard symbols (+, -, *, /, (, )) and the functions: sqrt(x), pow(x, y), sin(x), cos(x), tan(x), and radians(x). 
    IMPORTANT: The trigonometric functions (sin, cos, tan) expect the angle 'x' to be in radians. Use the radians(x) function to convert from degrees to radians.
    Example 1 (Hypotenuse): To find the hypotenuse of a triangle with sides 5 and 6, use "Action Input: sqrt(pow(5, 2) + pow(6, 2))".
    Example 2 (Trigonometry): To find the height of a building 100 meters away with an angle of elevation of 30 degrees, use "Action Input: 100 * tan(radians(30))".""",
    execute_func=calculate
)