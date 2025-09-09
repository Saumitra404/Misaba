from tool import StandardTool
import os.path
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
# Catch the specific error for missing modules
except ImportError:
    raise ImportError(
        "You are missing required dependencies! Try running: \n"
        "pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib"
    )
def gmail_today() -> str:
    return get_email_list("category:primary newer_than:24h is:unread")

def gmail_search(keyword: str) -> str:
    return get_email_list(query=keyword, max_results=3)

gmail_tool = StandardTool(
    name = "gmail_search",
    instruction = """To use the Gmail search tool, specify the action as 'Action: gmail_search' and provide your search query in 'Action Input:'. This tool searches for emails only within your Gmail Inbox. You can search for keywords or exact phrases by enclosing them in double quotes, for example, 'Action Input: "project update"'. To find emails from a specific person, use operators like 'from:email@example.com' or 'to:team@example.com'. You can also filter by date using 'after:YYYY/MM/DD' and 'before:YYYY/MM/DD', such as 'Action Input: after:2025/09/01 before:2025/09/08', or use relative times like 'newer_than:7d' for emails from the last seven days. Search for emails by their status with terms like 'is:unread' or 'is:starred'. To find emails with files, use 'has:attachment' or specify the file type with 'filename:pdf'. If you need to search only the subject line, use the 'subject:' operator, for instance, 'Action Input: subject:"Weekly Report"'. You can combine these operators to create very specific searches, which are joined by AND by default. For example, to find unread emails from 'jane@example.com' that are not about 'marketing', you would use 'Action Input: is:unread from:jane@example.com -marketing'. Use 'OR' within parentheses for alternative terms, like 'from:(jane@example.com OR john@example.com)'.""",
    execute_func = gmail_search
)


# ---------------------------------------------------------

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"] 

def get_email_list(query:str, max_results:str = 25) -> str:
    """
    Establishes the Gmail API Authentication using credentials.json from the API and token.json for
    the target email. Pulls emails using the QUERY constant, and returns the relevant information
    """

    # ---------- SECTION HANDLES OAUTH AND API TOKENS ----------

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("Authentication/gmail_token.json"):
        creds = Credentials.from_authorized_user_file("Authentication/gmail_token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("Authentication/gmail_credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("Authentication/gmail_token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)
        results = (service.users().messages().list(userId="me", labelIds=["INBOX"], q=query, maxResults=max_results).execute())
        messages = results.get("messages", [])

        if not messages:
            return "No emails found.\n"
        
        return_list = "Found Emails:\n\n"
        for message in messages:
            return_list += (f'Message ID: {message["id"]}\n')
            msg = (service.users().messages().get(userId="me", id=message["id"], format="metadata").execute())
            for header in msg["payload"]["headers"]:
                match header['name']:
                    case 'From':
                        return_list += f'    From: {header['value']}\n'
                    case 'Subject':
                        return_list += f'    Subject: {header['value']}\n'
                    case 'Date':
                        return_list += f'    Date: {header['value']}\n'
            return_list += f'    Snippet: {msg["snippet"]}\n\n'

        return return_list

    except HttpError as error:
        return f"An error with the tool has occurred: {error}\n"
