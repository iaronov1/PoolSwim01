#!/usr/bin/env python3
"""
Google Calendar Lap Swim Event Extractor

This script fetches events from a Google Calendar ICS feed and extracts
lap swim events occurring within the next 72 hours, displaying the time
and number of lanes available.

Usage:
    python extract_calendar_events.py              # Normal mode (filtered output)
    python extract_calendar_events.py --debug      # Debug mode (show all events)
"""

import argparse
import re
import sys
from datetime import datetime, timedelta
from typing import List, Tuple, Optional

import pytz
import requests
import recurring_ical_events
from icalendar import Calendar


# Configuration constants
CALENDAR_URL = "https://calendar.google.com/calendar/ical/l8r245s2qee54b6o3n5us88la4%40group.calendar.google.com/public/basic.ics"
LOCAL_TIMEZONE = pytz.timezone('America/New_York')  # EST/EDT timezone


def fetch_calendar_data(url: str) -> str:
    """
    Fetch the ICS calendar data from the provided URL.

    Args:
        url: The URL of the ICS calendar feed

    Returns:
        The raw ICS calendar data as a string

    Raises:
        requests.RequestException: If the HTTP request fails
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching calendar data: {e}", file=sys.stderr)
        sys.exit(1)


def parse_calendar(ics_data: str) -> Calendar:
    """
    Parse the ICS calendar data into a Calendar object.

    Args:
        ics_data: The raw ICS calendar data as a string

    Returns:
        A parsed Calendar object from the icalendar library
    """
    try:
        return Calendar.from_ical(ics_data)
    except Exception as e:
        print(f"Error parsing calendar data: {e}", file=sys.stderr)
        sys.exit(1)


def extract_lane_count(event_summary: str) -> Optional[int]:
    """
    Extract the number of lanes from an event summary containing "lap swim".

    The event summary should contain text like "lap swim 5 lanes" or "1 lane".
    This function uses a regular expression to find and extract the number.

    Args:
        event_summary: The event summary/title text

    Returns:
        The number of lanes as an integer, or None if not found or invalid format
    """
    # Convert to lowercase for case-insensitive matching
    summary_lower = event_summary.lower()

    # Check if "lap swim" is in the summary
    if "lap swim" not in summary_lower:
        return None

    # Pattern to match a number followed by "lane" or "lanes"
    # This will match patterns like "5 lanes", "1 lane", "10 lanes", etc.
    pattern = r'(\d+)\s*lanes?'
    match = re.search(pattern, summary_lower)

    if match:
        # Extract the number from the first capture group
        return int(match.group(1))

    return None


def normalize_to_local_timezone(dt: datetime, local_tz: pytz.timezone) -> datetime:
    """
    Convert a datetime object to the local timezone.

    If the datetime is naive (no timezone info), it's assumed to be UTC.

    Args:
        dt: The datetime object to convert
        local_tz: The target local timezone

    Returns:
        A timezone-aware datetime in the local timezone
    """
    # If the datetime is naive (no timezone), assume it's UTC
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)

    # Convert to the local timezone
    return dt.astimezone(local_tz)


def get_events_in_next_72_hours(calendar: Calendar, local_tz: pytz.timezone) -> List[Tuple[datetime, datetime, str]]:
    """
    Extract all events from the calendar that occur within the next 72 hours.

    This function now properly handles recurring events by expanding them using
    the recurring-ical-events library. This means that events with RRULE
    (recurrence rules) will be expanded into individual instances.

    Args:
        calendar: The parsed Calendar object
        local_tz: The local timezone to use for filtering and display

    Returns:
        A list of tuples containing (start_time, end_time, summary) for each event
        All datetime objects are in the local timezone
    """
    # Get the current time in the local timezone
    now = datetime.now(local_tz)

    # Calculate the end of the 72-hour window
    seventy_two_hours_later = now + timedelta(hours=72)

    events = []

    # Use recurring-ical-events to expand recurring events within our time window
    # This library automatically handles RRULE, EXDATE, RDATE, and other recurrence features
    # The 'between()' method returns expanded event instances, not just the base definitions
    # Convert to list to ensure all events are fetched
    expanded_events = list(recurring_ical_events.of(calendar).between(now, seventy_two_hours_later))

    # Process each expanded event instance
    for component in expanded_events:
        # Extract event details
        summary = str(component.get('summary', 'No Title'))
        dtstart = component.get('dtstart')
        dtend = component.get('dtend')

        # Skip if the event doesn't have start/end times
        if not dtstart or not dtend:
            continue

        # Get the datetime values (icalendar stores them in a special format)
        start_dt = dtstart.dt
        end_dt = dtend.dt

        # Handle all-day events (date objects instead of datetime)
        # Convert date objects to datetime at midnight
        if not isinstance(start_dt, datetime):
            start_dt = datetime.combine(start_dt, datetime.min.time())
        if not isinstance(end_dt, datetime):
            end_dt = datetime.combine(end_dt, datetime.min.time())

        # Normalize both times to the local timezone
        start_local = normalize_to_local_timezone(start_dt, local_tz)
        end_local = normalize_to_local_timezone(end_dt, local_tz)

        # Add the event to our list
        # Note: We don't need to filter by time here because recurring-ical-events
        # already filtered events to be within our time window
        events.append((start_local, end_local, summary))

    # Sort events by start time
    events.sort(key=lambda x: x[0])

    return events


def filter_lap_swim_events(events: List[Tuple[datetime, datetime, str]]) -> List[Tuple[datetime, datetime, int]]:
    """
    Filter events to only include lap swim events with lane information.

    Args:
        events: List of (start_time, end_time, summary) tuples

    Returns:
        List of (start_time, end_time, lane_count) tuples for lap swim events only
    """
    lap_swim_events = []

    for start_time, end_time, summary in events:
        # Try to extract the lane count from the summary
        lane_count = extract_lane_count(summary)

        # Only include events that have valid lane information
        if lane_count is not None:
            lap_swim_events.append((start_time, end_time, lane_count))

    return lap_swim_events


def format_time(dt: datetime) -> str:
    """
    Format a datetime object as HH:MM in 24-hour format.

    Args:
        dt: The datetime to format

    Returns:
        Time string in HH:MM format
    """
    return dt.strftime("%H:%M")


def print_filtered_output(events: List[Tuple[datetime, datetime, int]]) -> None:
    """
    Print lap swim events in the requested format: HH:MM - HH:MM N lanes

    Args:
        events: List of (start_time, end_time, lane_count) tuples
    """
    for start_time, end_time, lane_count in events:
        start_str = format_time(start_time)
        end_str = format_time(end_time)

        # Use proper singular/plural form
        lane_word = "lane" if lane_count == 1 else "lanes"

        print(f"{start_str} - {end_str} {lane_count} {lane_word}")


def print_debug_output(events: List[Tuple[datetime, datetime, str]]) -> None:
    """
    Print all events in debug mode with full details.

    Args:
        events: List of (start_time, end_time, summary) tuples
    """
    print("=== DEBUG MODE: All events in the next 72 hours ===\n")

    if not events:
        print("No events found in the next 72 hours.")
        return

    for i, (start_time, end_time, summary) in enumerate(events, 1):
        print(f"Event {i}:")
        print(f"  Start:   {start_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"  End:     {end_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"  Summary: {summary}")

        # Show lane extraction attempt
        lane_count = extract_lane_count(summary)
        if lane_count is not None:
            print(f"  Lanes:   {lane_count} (MATCHES FILTER)")
        else:
            print(f"  Lanes:   Not detected (does not match filter)")

        print()  # Blank line between events


def main():
    """
    Main entry point for the script.
    """
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description='Extract lap swim events from Google Calendar within the next 72 hours'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode to show all events without filtering'
    )

    args = parser.parse_args()

    # Step 1: Fetch the calendar data from the URL
    ics_data = fetch_calendar_data(CALENDAR_URL)

    # Step 2: Parse the ICS data into a Calendar object
    calendar = parse_calendar(ics_data)

    # Step 3: Extract events occurring in the next 72 hours
    all_events = get_events_in_next_72_hours(calendar, LOCAL_TIMEZONE)

    # Step 4: Display results based on mode
    if args.debug:
        # Debug mode: Show all events with full details
        print_debug_output(all_events)
    else:
        # Normal mode: Filter and show only lap swim events
        lap_swim_events = filter_lap_swim_events(all_events)

        if not lap_swim_events:
            # No matching events found - exit silently or with a message
            # (You can remove this if you prefer silent output when no events found)
            pass
        else:
            print_filtered_output(lap_swim_events)


if __name__ == "__main__":
    main()
