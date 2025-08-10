import os
import requests
from typing import Any, Dict, Optional
from dateutil import parser as dateparser
from dateutil import tz

CAL_API_BASE = os.getenv("CAL_API_BASE", "https://api.cal.com/v1")
CAL_API_KEY = os.getenv("CAL_API_KEY", "")
CAL_EVENT_TYPE_ID = os.getenv("CAL_EVENT_TYPE_ID", "")
CAL_ORGANIZER_USERNAME = os.getenv("CAL_ORGANIZER_USERNAME", "")
DEFAULT_TZ = os.getenv("DEFAULT_TIMEZONE", "UTC")


def _headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {CAL_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def parse_to_iso(date_str: str, time_str: Optional[str] = None, timezone: Optional[str] = None) -> str:
    tzinfo = tz.gettz(timezone or DEFAULT_TZ)
    text = date_str if not time_str else f"{date_str} {time_str}"
    dt = dateparser.parse(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tzinfo)
    return dt.astimezone(tzinfo).isoformat()


def check_cal_availability(date_str: str, time_str: Optional[str] = None, duration_minutes: int = 30) -> Dict[str, Any]:
    if not CAL_API_KEY or not CAL_EVENT_TYPE_ID:
        return {"ok": False, "error": "Cal API not configured"}

    # Note: Cal.com public API for availability may vary by version. Here we request event-type availability.
    # If a specific endpoint is unavailable, the tool will instruct the agent to offer alternatives.
    iso_start = parse_to_iso(date_str, time_str)
    try:
        resp = requests.get(
            f"{CAL_API_BASE}/event-types/{CAL_EVENT_TYPE_ID}/availability",
            headers=_headers(),
            params={"startTime": iso_start, "duration": duration_minutes},
            timeout=20,
        )
        if resp.status_code >= 400:
            return {"ok": False, "status": resp.status_code, "error": resp.text}
        return {"ok": True, "data": resp.json()}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def create_cal_booking(
    customer_name: str,
    customer_email: str,
    date_str: str,
    time_str: str,
    notes: Optional[str] = None,
    timezone: Optional[str] = None,
    event_type_id: Optional[str] = None,
) -> Dict[str, Any]:
    if not CAL_API_KEY:
        return {"ok": False, "error": "Cal API key not set"}

    iso_start = parse_to_iso(date_str, time_str, timezone)
    payload: Dict[str, Any] = {
        "eventTypeId": event_type_id or CAL_EVENT_TYPE_ID,
        "start": iso_start,
        "name": customer_name,
        "email": customer_email,
        "notes": notes or "",
        "timeZone": timezone or DEFAULT_TZ,
    }

    try:
        resp = requests.post(
            f"{CAL_API_BASE}/bookings",
            headers=_headers(),
            json=payload,
            timeout=30,
        )
        if resp.status_code >= 400:
            return {"ok": False, "status": resp.status_code, "error": resp.text}
        return {"ok": True, "data": resp.json()}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# LangChain tool wrappers
from langchain_core.tools import tool


@tool
def cal_check_availability(date: str, time: Optional[str] = None, duration_minutes: int = 30) -> dict:
    """Check Cal.com availability for a given date/time and duration. Returns JSON."""
    return check_cal_availability(date, time, duration_minutes)


@tool
def cal_make_booking(name: str, email: str, date: str, time: str, notes: Optional[str] = None, timezone: Optional[str] = None) -> dict:
    """Create a Cal.com booking for the provided customer name/email and date/time. Returns JSON."""
    return create_cal_booking(name, email, date, time, notes, timezone)