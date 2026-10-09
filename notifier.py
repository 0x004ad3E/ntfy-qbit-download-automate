import json
import logging
import time
import base64
from pathlib import Path
from urllib.parse import urlencode

import requests


# ============================================================
# Configuration
# ============================================================
OUTPUT_DIR = Path("/output")

JSON_FILE = OUTPUT_DIR / "results.json"

# Your ntfy server
NTFY_SERVER = "https://ntfy.sh"

# Normal notification topic
NOTIFY_TOPIC = "scraper"

# Topic receiving the Download button command
COMMAND_TOPIC = "scraper-command"

# Delay between notifications, in seconds
PUBLISH_DELAY = 3

NTFY_TOKEN = "tk_werwerdsfsfsdf"
QBIT_API_KEY = "qbt_wrwer23423sfsd"

QBIT_URL="192.168.50.93:6520"
# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


# ============================================================
# Authentication
# ============================================================

def auth_headers() -> dict:
    """
    Return authentication headers for ntfy.
    """

    return {
        "Authorization": f"Bearer {NTFY_TOKEN}",
    }


# ============================================================
# Send notification
# ============================================================
def post_json(payload: dict) -> bool:

    tags = payload.get("mags", "").strip()

    headers = {
        **auth_headers(),
        "Tags": tags,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            NTFY_SERVER,
            json=payload,
            headers=headers,
            timeout=15,
        )

        if not response.ok:
            logger.error(
                "ntfy returned HTTP %s: %s",
                response.status_code,
                response.text,
            )
            return False

        logger.info(
            "Notification sent: %s",
            payload.get("title", ""),
        )

        return True

    except requests.RequestException as exc:
        logger.error(
            "Failed to send notification: %s",
            exc,
        )
        return False

def og_post_json(payload: dict) -> bool:
    """
    Publish a JSON notification to ntfy.

    Returns:
        True  - notification was successfully published
        False - publishing failed
    """

    headers = {
        **auth_headers(),
        "Content-Type": "application/json",
    }
    print(headers)
    try:
        response = requests.post(
            NTFY_SERVER,
            json=payload,
            headers=headers,
            timeout=15,
        )

        response.raise_for_status()

        logger.info(
            "Notification sent: %s",
            payload.get("title", ""),
        )

        return True

    except requests.RequestException as exc:
        logger.error(
            "Failed to send notification: %s",
            exc,
        )

        return False


# ============================================================
# Create and send notification for one JSON record
# ============================================================

def notify_entry(entry: dict) -> bool:
    """
    Send one JSON record as an ntfy notification.

    Uses:
        title         -> ntfy notification title
        first_image   -> ntfy attachment
        magnet_links[0] -> Download button body
    """

    title = entry.get("title", "").strip()
    image_url = entry.get("first_image", "").strip()

    magnet_links = entry.get("magnet_links", [])
    tags = entry.get("tags", "").strip()

    # --------------------------------------------------------
    # Validate record
    # --------------------------------------------------------

    if not title:
        logger.warning(
            "Skipping record without title"
        )
        return False

    if not isinstance(magnet_links, list) or not magnet_links:
        logger.warning(
            "Skipping '%s': no magnet_links",
            title,
        )
        return False

    magnet = magnet_links[0].strip()

    if not magnet:
        logger.warning(
            "Skipping '%s': first magnet is empty",
            title,
        )
        return False

    # --------------------------------------------------------
    # Build ntfy notification
    # --------------------------------------------------------

    service_body = urlencode({
    "urls": magnet,
    })

    payload = {
        "topic": NOTIFY_TOPIC,

        # Use title directly from the JSON record
        "title": title,

        # Keep the notification body simple
        "message": "Download available",

        # Tags to specify additional information
        "mags": tags,

        "actions": [
            {
                "action": "http",
                "label": "Download",
                "url": f"http://{QBIT_URL}/api/v2/torrents/add",
                "method": "POST",
                "headers": {
                    "Authorization": f"Bearer {QBIT_API_KEY}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                "body": service_body,
            },
        ],
    }

    # --------------------------------------------------------
    # Add image if available
    # --------------------------------------------------------

    if image_url:
        payload["attach"] = image_url

    # --------------------------------------------------------
    # Publish
    # --------------------------------------------------------

    return post_json(payload)


# ============================================================
# Main
# ============================================================

def main():

    logger.info(
        "Reading JSON file: %s",
        JSON_FILE,
    )

    try:
        with open(
            JSON_FILE,
            "r",
            encoding="utf-8",
        ) as f:
            entries = json.load(f)

    except FileNotFoundError:
        logger.error(
            "JSON file not found: %s",
            JSON_FILE,
        )
        return

    except json.JSONDecodeError as exc:
        logger.error(
            "Invalid JSON: %s",
            exc,
        )
        return

    # --------------------------------------------------------
    # Validate top-level JSON
    # --------------------------------------------------------

    if not isinstance(entries, list):
        logger.error(
            "Expected JSON file to contain a list of records"
        )
        return

    logger.info(
        "Found %d records",
        len(entries),
    )

    # --------------------------------------------------------
    # Publish records
    # --------------------------------------------------------

    successful = 0
    failed = 0

    for index, entry in enumerate(entries, start=1):

        logger.info(
            "Processing %d/%d",
            index,
            len(entries),
        )

        if not isinstance(entry, dict):
            logger.warning(
                "Skipping record %d: not an object",
                index,
            )
            failed += 1
            continue

        success = notify_entry(entry)

        if success:
            successful += 1
        else:
            failed += 1

        # ----------------------------------------------------
        # Delay between publishes
        # ----------------------------------------------------

        # Don't sleep after the final record.
        if index < len(entries):
            logger.info(
                "Waiting %s seconds before next notification...",
                PUBLISH_DELAY,
            )

            time.sleep(PUBLISH_DELAY)

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    logger.info(
        "Finished. Successful: %d, Failed: %d",
        successful,
        failed,
    )


if __name__ == "__main__":
    main()
