import re

LOG_START_PATTERN = r'(Thu|Fri|Sat|Sun|Mon|Tue|Wed)\s[A-Z][a-z]{2}\s+\d{1,2}\s\d{4}'


def split_events(raw_logs: str):
    parts = re.split(f'(?={LOG_START_PATTERN})', raw_logs)
    return [p.strip() for p in parts if p.strip()]


def parse_logs(raw_logs):
    events = []

    lines = raw_logs.splitlines()

    if len(lines) <= 1:
        lines = split_events(raw_logs)

    for line in lines:

        if "Failed password" in line:
            events.append({"type": "security", "message": line})

        elif "pam_unix" in line:
            events.append({"type": "auth_session", "message": line})

        elif "VendorID" in line:
            events.append({"type": "transaction", "message": line})

        elif "GET" in line or "POST" in line:
            events.append({"type": "web_access", "message": line})

        else:
            events.append({"type": "other", "message": line})

    return events
