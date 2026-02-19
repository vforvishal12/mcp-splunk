import re

def parse_logs(raw_logs):
    events = []

    for line in raw_logs.splitlines():

        if "Failed password" in line:
            events.append({
                "type": "security",
                "message": line
            })

        elif "pam_unix" in line:
            events.append({
                "type": "auth_session",
                "message": line
            })

        elif "VendorID" in line:
            events.append({
                "type": "transaction",
                "message": line
            })

        elif "GET" in line or "POST" in line:
            events.append({
                "type": "web_access",
                "message": line
            })

        else:
            events.append({
                "type": "other",
                "message": line
            })

    return events
