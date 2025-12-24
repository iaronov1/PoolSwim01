#!/usr/bin/env python3
"""
Test script to check events in a 72-hour window, focusing on 2025-12-26
"""

import sys
from datetime import datetime, timedelta
import pytz
import requests
import recurring_ical_events
from icalendar import Calendar

CALENDAR_URL = "https://calendar.google.com/calendar/ical/l8r245s2qee54b6o3n5us88la4%40group.calendar.google.com/public/basic.ics"
LOCAL_TIMEZONE = pytz.timezone('America/New_York')

# Fetch and parse calendar
print("Fetching calendar data...")
response = requests.get(CALENDAR_URL, timeout=30)
response.raise_for_status()
calendar = Calendar.from_ical(response.text)

# Set up 72-hour window
now = datetime.now(LOCAL_TIMEZONE)
seventy_two_hours_later = now + timedelta(hours=72)

print(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"Window ends:  {seventy_two_hours_later.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print()

# Expand recurring events
print("Expanding recurring events...")
expanded_events = list(recurring_ical_events.of(calendar).between(now, seventy_two_hours_later))
print(f"Total expanded events in 72-hour window: {len(expanded_events)}\n")

# Process and display all events
events_list = []
for component in expanded_events:
    summary = str(component.get('summary', 'No Title'))
    dtstart = component.get('dtstart')
    dtend = component.get('dtend')

    if not dtstart or not dtend:
        continue

    start_dt = dtstart.dt
    end_dt = dtend.dt

    # Handle all-day events
    if not isinstance(start_dt, datetime):
        start_dt = datetime.combine(start_dt, datetime.min.time())
    if not isinstance(end_dt, datetime):
        end_dt = datetime.combine(end_dt, datetime.min.time())

    # Normalize to local timezone
    if start_dt.tzinfo is None:
        start_dt = pytz.utc.localize(start_dt)
    if end_dt.tzinfo is None:
        end_dt = pytz.utc.localize(end_dt)

    start_local = start_dt.astimezone(LOCAL_TIMEZONE)
    end_local = end_dt.astimezone(LOCAL_TIMEZONE)

    events_list.append((start_local, end_local, summary))

# Sort by start time
events_list.sort(key=lambda x: x[0])

# Filter for 2025-12-26
print("=" * 80)
print("EVENTS ON 2025-12-26:")
print("=" * 80)

dec26_events = [e for e in events_list if e[0].date() == datetime(2025, 12, 26).date()]
print(f"\nTotal events on December 26, 2025: {len(dec26_events)}\n")

for i, (start_time, end_time, summary) in enumerate(dec26_events, 1):
    print(f"{i}. {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')} | {summary}")

# Show all events grouped by date
print("\n" + "=" * 80)
print("ALL EVENTS IN 72-HOUR WINDOW (grouped by date):")
print("=" * 80 + "\n")

from itertools import groupby

for date, group in groupby(events_list, key=lambda x: x[0].date()):
    print(f"\n{date.strftime('%Y-%m-%d (%A)')}:")
    print("-" * 40)
    for start_time, end_time, summary in group:
        print(f"  {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')} | {summary}")
