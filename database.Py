import json
import os.path
from datetime import datetime, timedelta

# Google API Imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class CalendarDB:
    def __init__(self, file_path="calendar_db.json"):
        self.file_path = file_path
        self.data = self._load_db()

    def _load_db(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass 
        return {"metadata": {"last_sync": None}, "events": {}}

    def save(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def sync_with_google(self):
        """Authenticates with Google and fetches all of today's events."""
        print("\n[System] Connecting to Google Calendar...")
        creds = None
        
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('calendar', 'v3', credentials=creds)

            # FIX: Fetch events from the START of today (00:00) instead of current time
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
            print(f"[System] Fetching all events for today...")
            
            events_result = service.events().list(calendarId='primary', 
                                                timeMin=today_start,
                                                maxResults=20, 
                                                singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])

            # Reset local events to ensure sync is identical to Google
            self.data["events"] = {} 

            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                # Parsing Google format to our local format
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                
                date_str = start_dt.strftime("%Y-%m-%d")
                self.add_event(
                    date_str, 
                    start_dt.strftime("%H:%M"), 
                    end_dt.strftime("%H:%M"), 
                    event.get('summary', 'No Title')
                )

            self.data["metadata"]["last_sync"] = datetime.now().isoformat()
            self.save()
            print("[System] Sync completed successfully!")

        except HttpError as error:
            print(f'[Error] An error occurred: {error}')

    def get_event_at(self, dt_object):
        last_sync_str = self.data["metadata"].get("last_sync")
        should_sync = False
        
        if not last_sync_str:
            should_sync = True
        else:
            last_sync_dt = datetime.fromisoformat(last_sync_str)
            if datetime.now() - last_sync_dt > timedelta(hours=1):
                should_sync = True
        
        if should_sync:
            self.sync_with_google()

        date_key = dt_object.strftime("%Y-%m-%d")
        check_time = dt_object.strftime("%H:%M")
        
        day_events = self.data["events"].get(date_key, [])
        for event in day_events:
            if event["start"] <= check_time < event["end"]:
                return event["topic"]
        
        return "Free"

    def add_event(self, date_str, start_t, end_t, topic):
        if date_str not in self.data["events"]:
            self.data["events"][date_str] = []
        
        self.data["events"][date_str].append({
            "start": start_t,
            "end": end_t,
            "topic": topic
        })
        self.save()

    def clear_all(self):
        self.data = {"metadata": {"last_sync": None}, "events": {}}
        self.save()