from flask import Flask, request
import requests
import os
import urllib.parse as urlparse

app = Flask(__name__)

GOTIFY_URL = os.environ["GOTIFY_URL"]
GOTIFY_TOKEN = os.environ["GOTIFY_TOKEN"]

@app.route("/smtp-hook", methods=["POST"])
def hook():
    raw = request.get_data(as_text=True)

    # Debug print original payload to container logs
    print("\n=== RAW SMTP2HTTP MESSAGE ===")
    print(raw)
    print("=== END RAW MESSAGE ===\n")

    # smtp2http sends data like:
    # addresses%5Bfrom%5D=foo&body%5Btext%5D=hello+world
    parsed = urlparse.parse_qs(raw)

    # Helper to safely extract values
    def get(field, subfield=None):
        key = field if not subfield else f"{field}[{subfield}]"
        val = parsed.get(key, [""])[0]
        return urlparse.unquote(val)

    subject = get("subject")
    body = get("body", "text")
    html_body = get("body", "html")  # unused, but some alerts send it
    severity = "Unknown"
    timestamp = ""

    # Attempt to parse iDRAC info from body text
    lines = body.splitlines()
    clean_lines = []
    for line in lines:
        if "Severity:" in line:
            severity = line.split(":", 1)[1].strip()
        elif "Date/Time:" in line:
            timestamp = line.split(":", 1)[1].strip()
        else:
            clean_lines.append(line)

    # Build the cleaned body
    pretty_body = "\n".join(clean_lines).strip()

    # Build final Gotify message
    message = (
        f"**{subject}**\n\n"
        f"**Severity:** {severity}\n"
        f"**Date/Time:** {timestamp}\n\n"
        f"{pretty_body}\n\n"
    )

    # Fix Gotify markdown line breaks (needs two spaces)
    message = message.replace("\n", "  \n")

    # Convert to Gotify markdown breaks
    message = message.replace("\n", "  \n")

    try:
        r = requests.post(
            f"{GOTIFY_URL}/message?token={GOTIFY_TOKEN}",
            json={
                "title": f"iDRAC Alert: {severity}",
                "message": message,
                "priority": 5,
                "extras": {
                    "client::display": {
                        "contentType": "text/markdown"
                    }
                }
            },
            timeout=5
        )
        print(f"Sent to Gotify → status {r.status_code}")
        return "ok", 200
    except Exception as e:
        print(f"Error sending to Gotify: {e}")
        return str(e), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
