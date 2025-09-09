from tool import StandardTool
import datetime

def getDateTime() -> str:
    """Gets the current date and time using standard library formatting."""
    now = datetime.datetime.now()
    # %A: Weekday, %B: Month, %d: Day, %Y: Year
    # %I: Hour (12-hr), %M: Minute, %p: AM/PM
    return now.strftime("Date is %A, %B %d, %Y. Time is %I:%M %p.")

datetime_tool = StandardTool(
    name = 'datetime',
    instruction = 'This tool fetches the current date and time. Takes no input.', # Corrected typo
    execute_func = getDateTime
)

