import json
import re
from datetime import date, datetime
from urllib.parse import urlparse

import requests
from icalendar import Calendar

def get_biu_assignment_tasks(calendar_url: str) -> str:
    """
    Read a BIU / Moodle calendar export URL and return only submission tasks.

    Returns tasks with:
    - course
    - title
    - due_date

    Excludes office hours, Zoom meetings, lectures, and other non-submission events.
    """

    if not calendar_url.startswith("https://lemida.biu.ac.il/calendar/export_execute.php"):
        return "Invalid calendar URL. Expected a BIU Moodle calendar export URL."

    try:
        response = requests.get(calendar_url, timeout=20)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Failed to fetch calendar: {e}"

    try:
        calendar = Calendar.from_ical(response.content)
    except Exception as e:
        return f"Failed to parse calendar ICS content: {e}"

    exclude_patterns = [
        "zoom",
        "זום",
        "שעת קבלה",
        "שעות קבלה",
        "office hour",
        "office hours",
        "הרצאה",
        "lecture",
        "מפגש",
        "meeting",
        "class",
        "שיעור",
    ]

    submission_patterns = [
        "מטלה",
        "הגשה",
        "להגשה",
        "מועד הגשה",
        "assignment",
        "assignments",
        "submission",
        "submit",
        "due",
        "quiz",
        "בוחן",
        "תרגיל",
        "עבודה",
    ]

    def clean_text(value: object) -> str:
        if value is None:
            return ""
        text = str(value)
        text = re.sub(r"<[^>]+>", " ", text)
        text = text.replace("\\n", " ")
        text = " ".join(text.split())
        return text.strip()

    def format_due(value: object) -> str:
        if value is None:
            return ""

        raw = getattr(value, "dt", value)

        if isinstance(raw, datetime):
            return raw.isoformat()

        if isinstance(raw, date):
            return raw.isoformat()

        return str(raw)

    def get_course_and_title(summary: str, description: str) -> tuple[str, str]:
        course = ""
        title = summary.strip()

        # Common Moodle format: "Course name: Event title"
        if ":" in summary:
            left, right = summary.split(":", 1)
            if len(left.strip()) > 2 and len(right.strip()) > 2:
                course = left.strip()
                title = right.strip()

        # Try to recover course from description if it exists there
        course_patterns = [
            r"קורס[:\s]+([^|\\n]+)",
            r"Course[:\s]+([^|\\n]+)",
            r"course[:\s]+([^|\\n]+)",
        ]

        for pattern in course_patterns:
            match = re.search(pattern, description)
            if match:
                course = match.group(1).strip()
                break

        return course, title

    tasks = []

    for component in calendar.walk():
        if component.name != "VEVENT":
            continue

        summary = clean_text(component.get("summary"))
        description = clean_text(component.get("description"))
        location = clean_text(component.get("location"))
        categories = clean_text(component.get("categories"))

        combined = f"{summary} {description} {location} {categories}".lower()

        if any(pattern.lower() in combined for pattern in exclude_patterns):
            continue

        is_submission = any(pattern.lower() in combined for pattern in submission_patterns)

        if not is_submission:
            continue

        due_value = component.get("dtend") or component.get("dtstart")
        due_date = format_due(due_value)

        course, title = get_course_and_title(summary, description)

        tasks.append({
            "course": course,
            "title": title,
            "due_date": due_date,
        })

    tasks.sort(key=lambda task: task["due_date"] or "9999-12-31")

    return json.dumps(tasks, ensure_ascii=False, indent=2)