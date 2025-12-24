#!/usr/bin/env python3
"""
Diagnostic script to debug calendar event expansion issues
"""

import sys
from datetime import datetime, timedelta
import pytz
import requests
import recurring_ical_events
from icalendar import Calendar

CALENDAR_URL = "https://calendar.google.com/calendar/ical/l8r245s2qee54b6o3n5us88la4%40group.calendar.google.com/public/basic.ics"
LOCAL_TIMEZONE = pytz.timezone('America/New_York')

# Fetch calendar
print("Fetching calendar data...")
response = requests.get(CALENDAR_URL, timeout=30)
response.raise_for_status()
ics_data = response.text

# Parse calendar
print("Parsing calendar...")
calendar = Calendar.from_ical(ics_data)

# Count base events
base_events = [c for c in calendar.walk() if c.name == "VEVENT"]
print(f"\n=== BASE EVENTS IN CALENDAR: {len(base_events)} ===\n")

# Show first few base events
for i, event in enumerate(base_events[:5], 1):
    print(f"Base Event {i}:")
    print(f"  Summary: {event.get('summary', 'No Title')}")
    print(f"  Start: {event.get('dtstart').dt if event.get('dtstart') else 'N/A'}")
    print(f"  RRULE: {event.get('rrule', 'None')}")
    print()

# Now try to expand with recurring-ical-events
print("\n=== TESTING RECURRING-ICAL-EVENTS LIBRARY ===\n")

now = datetime.now(LOCAL_TIMEZONE)
twenty_four_hours_later = now + timedelta(hours=24)

print(f"Current time (local): {now}")
print(f"Search window end: {twenty_four_hours_later}")
print()

# Try with timezone-aware datetimes
print("Attempting expansion with timezone-aware datetimes...")
try:
    expanded_events = list(recurring_ical_events.of(calendar).between(now, twenty_four_hours_later))
    print(f"SUCCESS: Expanded to {len(expanded_events)} events")
    for i, event in enumerate(expanded_events[:10], 1):
        print(f"  Expanded Event {i}:")
        print(f"    Summary: {event.get('summary', 'No Title')}")
        print(f"    Start: {event.get('dtstart').dt if event.get('dtstart') else 'N/A'}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print()

# Try with naive datetimes
print("Attempting expansion with naive datetimes...")
now_naive = now.replace(tzinfo=None)
later_naive = twenty_four_hours_later.replace(tzinfo=None)
try:
    expanded_events = list(recurring_ical_events.of(calendar).between(now_naive, later_naive))
    print(f"SUCCESS: Expanded to {len(expanded_events)} events")
    for i, event in enumerate(expanded_events[:10], 1):
        print(f"  Expanded Event {i}:")
        print(f"    Summary: {event.get('summary', 'No Title')}")
        print(f"    Start: {event.get('dtstart').dt if event.get('dtstart') else 'N/A'}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print()

# Try with dates instead of datetimes
print("Attempting expansion with date objects...")
today = now.date()
tomorrow = (now + timedelta(days=1)).date()
try:
    expanded_events = list(recurring_ical_events.of(calendar).between(today, tomorrow))
    print(f"SUCCESS: Expanded to {len(expanded_events)} events")
    for i, event in enumerate(expanded_events[:10], 1):
        print(f"  Expanded Event {i}:")
        print(f"    Summary: {event.get('summary', 'No Title')}")
        print(f"    Start: {event.get('dtstart').dt if event.get('dtstart') else 'N/A'}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
