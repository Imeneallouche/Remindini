from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timezone
import os

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def main():
    # Supprimer le token existant pour forcer une nouvelle authentification
    if os.path.exists('token.pickle'):
        os.remove('token.pickle')

    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    
    service = build('calendar', 'v3', credentials=creds)
    
    now = datetime.now(timezone.utc).isoformat()
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    if not events:
        print('Aucun événement trouvé.')
    else:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"- {event['summary']} ({start})")

if __name__ == '__main__':
    main()