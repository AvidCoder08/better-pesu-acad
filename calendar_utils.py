import json
import requests
from datetime import date
from github_utils import _get_github_config

CALENDAR_FILE_PATH = "data/calendar_events.json"


def get_calendar_events():
    """
    Fetch calendar events from GitHub JSON file.
    Returns a list of event dictionaries.
    """
    try:
        config = _get_github_config()
        url = f"https://raw.githubusercontent.com/{config['repo']}/{config['branch']}/{CALENDAR_FILE_PATH}"

        response = requests.get(url)
        if response.status_code == 404:
            # File doesn't exist yet, return empty list
            return []

        response.raise_for_status()
        events = response.json()
        return events if isinstance(events, list) else []
    except Exception as e:
        raise RuntimeError(f"Failed to fetch calendar events: {e}")


def save_calendar_events(events):
    """
    Save calendar events to GitHub JSON file.
    """
    try:
        from github_utils import upload_to_github

        # Convert events to JSON
        json_bytes = json.dumps(events, indent=2).encode('utf-8')

        # Upload to GitHub
        upload_to_github(
            file_bytes=json_bytes,
            file_path=CALENDAR_FILE_PATH,
            commit_message="Update calendar events"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to save calendar events: {e}")


def add_calendar_event(title, event_type, start_date, end_date=None, description=""):
    """
    Add a new calendar event.
    """
    events = get_calendar_events()

    # Generate a simple ID
    event_id = f"evt_{len(events) + 1}_{int(date.today().timestamp())}"

    new_event = {
        "id": event_id,
        "title": title,
        "type": event_type,
        "start_date": start_date.isoformat() if isinstance(start_date, date) else start_date,
        "end_date": end_date.isoformat() if isinstance(end_date, date) and end_date else None,
        "description": description
    }

    events.append(new_event)
    save_calendar_events(events)
    return event_id


def update_calendar_event(event_id, title, event_type, start_date, end_date=None, description=""):
    """
    Update an existing calendar event.
    """
    events = get_calendar_events()

    for event in events:
        if event.get("id") == event_id:
            event["title"] = title
            event["type"] = event_type
            event["start_date"] = start_date.isoformat() if isinstance(start_date, date) else start_date
            event["end_date"] = end_date.isoformat() if isinstance(end_date, date) and end_date else None
            event["description"] = description
            break

    save_calendar_events(events)


def delete_calendar_event(event_id):
    """
    Delete a calendar event by ID.
    """
    events = get_calendar_events()
    events = [e for e in events if e.get("id") != event_id]
    save_calendar_events(events)
