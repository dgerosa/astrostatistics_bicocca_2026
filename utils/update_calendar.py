import re
import sys
from datetime import datetime
from ics import Calendar
import requests
from dateutil import tz
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+
# from pytz import timezone  # alternative if using older Python

ITALY_TZ = ZoneInfo("Europe/Rome")  # CET/CEST automatic
readme_path = Path(__file__).resolve().parents[1] / "README.md"

# 🔗 Your ICS link
ICS_URL = "https://calendar.google.com/calendar/ical/7b3eb78f345682c12c065855a0e49c6b21d2f1db72b244bf752dd534a47c6066%40group.calendar.google.com/public/basic.ics"

# Get date range from command line arguments or use defaults
if len(sys.argv) == 3:
    start_str = sys.argv[1]
    end_str = sys.argv[2]
else:
    start_str = "2026-01-01"
    end_str = "2026-12-31"

start = datetime.strptime(start_str, "%Y-%m-%d").replace(tzinfo=tz.UTC)
end = datetime.strptime(end_str, "%Y-%m-%d").replace(tzinfo=tz.UTC)

# Fetch and parse calendar
r = requests.get(ICS_URL)
c = Calendar(r.text)

# Filter events
events = [
    e for e in c.events
    if e.begin and start <= e.begin <= end
]

# Sort events by date
events.sort(key=lambda e: e.begin)

# Format as Markdown
if events:

    md_lines = []

    for i, e in enumerate(events):
        start = e.begin.astimezone(ITALY_TZ)
        end = e.end.astimezone(ITALY_TZ) if e.end else None

        # Format: 2025, Nov 17, 09:30am - 11:30am
        start_str = start.strftime("%Y, %b %d, %I:%M%p")
        end_str = end.strftime("%I:%M%p") if end else ""
        # Fix AM/PM to lowercase
        start_str = start_str.replace("AM", "am").replace("PM", "pm")
        end_str = end_str.replace("AM", "am").replace("PM", "pm")

        time_range = f"**{start_str} - {end_str}**" if end_str else f"**{start_str}**"

        if e.location:
            md_lines.append(f"{i+1}. {time_range}. {e.location}.")
        else:
            md_lines.append(f"{i+1}. {time_range}")
        md_output = "\n".join(md_lines)
else:
    md_output = f"_No events between {start_str} and {end_str}._"

# Update README
with open(readme_path, "r") as f:
    readme = f.read()

new_readme = re.sub(
    r"(<!-- CALENDAR:START -->)(.*?)(<!-- CALENDAR:END -->)",
    f"<!-- CALENDAR:START -->\n{md_output}\n<!-- CALENDAR:END -->",
    readme,
    flags=re.DOTALL
)

with open(readme_path, "w") as f:
    f.write(new_readme)