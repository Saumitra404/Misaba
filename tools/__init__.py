from .calculate_tool import calculate_tool
from .datetime_tool import datetime_tool

try:
    from .gmail_tool import gmail_tool
except ImportError:
    def _raise_gmail_import_error(*args, **kwargs):
        raise ImportError(
            "You are missing required dependencies for the Gmail tool! Try running: \n"
            "pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib"
        )

    gmail_tool = StandardTool(
        name="gmail_search",
        instruction="[UNAVAILABLE] Please install Google client libraries to use this tool.",
        execute_func=_raise_gmail_import_error
    )
