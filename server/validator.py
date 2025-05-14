# validators.py
import re
import datetime
from datetime import datetime, timedelta
from googleapiclient.errors import HttpError

import pytz

from config import BUSINESS_HOURS, WEEKDAYS, service, CALENDAR_ID


def handle_general_exception(e):

    return {'error': f"שגיאה: {str(e)}"}, 500


def handle_google_error(e: HttpError):
    return {'error': f"שגיאת API של Google: {e.resp.status}"}, 502


# def validate_appointment_input(data):
#     required_fields = ['user_id', 'date', 'start_time']
#     for field in required_fields:
#         if not data.get(field):
#             return f"שדה חובה חסר: {field}", None
#
#     try:
#         duration = int(data.get('duration', 30))
#     except ValueError:
#         return "משך הפגישה חייב להיות מספר שלם", None
#
#     tz = data.get('tz', 'UTC')
#     try:
#         local_tz = pytz.timezone(tz)
#     except pytz.UnknownTimeZoneError:
#         return f"אזור הזמן לא תקין: {tz}", None
#
#     try:
#         start_time_str = f"{data['date']}T{data['start_time']}"
#         start_time = local_tz.localize(datetime.datetime.fromisoformat(start_time_str))
#
#         end_time = start_time + timedelta(minutes=duration)
#     except ValueError:
#         return "פורמט תאריך/שעה לא תקין. יש להשתמש ב-YYYY-MM-DD ו-HH:MM", None
#
#     if start_time <datetime.now(pytz.utc):
#         return "לא ניתן לקבוע תור בעבר", None
#
#     if not is_within_business_hours(start_time, duration):
#         return 'מחוץ לשעות הפעילות', 409
#
#     return None, {
#         'user_id': data['user_id'],
#         'start_time': start_time,
#         'end_time': end_time,
#         'duration': duration,
#         'tz': tz
#     }
#
#
# def parse_datetime(date_str, time_str, tz_str='UTC'):
#     try:
#         start_time_str = f"{date_str}T{time_str}"
#         local_tz = pytz.timezone(tz_str)
#         return local_tz.localize(datetime.fromisoformat(start_time_str))
#     except Exception:
#         return None
from datetime import datetime, timedelta
import pytz

def validate_appointment_input(data):
    required_fields = ['user_id', 'date', 'start_time']
    for field in required_fields:
        if not data.get(field):
            return f"שדה חובה חסר: {field}", None

    try:
        duration = int(data.get('duration', 30))
    except ValueError:
        return "משך הפגישה חייב להיות מספר שלם", None

    tz = data.get('tz', 'UTC')
    try:
        local_tz = pytz.timezone(tz)
    except pytz.UnknownTimeZoneError:
        return f"אזור הזמן לא תקין: {tz}", None

    try:
        start_time_str = f"{data['date']}T{data['start_time']}"
        # שימוש ב-strptime במקום fromisoformat כדי להימנע מתקלות
        naive_start = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M")
        start_time = local_tz.localize(naive_start)
        end_time = start_time + timedelta(minutes=duration)
    except Exception:
        return "פורמט תאריך/שעה לא תקין. יש להשתמש ב-YYYY-MM-DD ו-HH:MM", None

    if start_time < datetime.now(pytz.utc):
        return "לא ניתן לקבוע תור בעבר", None

    if not is_within_business_hours(start_time, duration):
        return 'מחוץ לשעות הפעילות', 409

    return None, {
        'user_id': data['user_id'],
        'start_time': start_time,
        'end_time': end_time,
        'duration': duration,
        'tz': tz
    }


def is_valid_time_format(time_str):
    try:
        hour, minute = map(int, time_str.split(":"))
        return 0 <= hour < 24 and 0 <= minute < 60
    except Exception:
        return False


def is_within_business_hours(start_time, duration_minutes):
    start_hour, end_hour = BUSINESS_HOURS
    end_time = start_time + timedelta(minutes=duration_minutes)
    return start_hour <= start_time.hour < end_hour and end_time.hour <= end_hour


def validate_appointment_request(data):
    date_str = data.get('date')
    time_str = data.get('start_time')
    tz = data.get('tz', 'UTC')

    if not is_valid_time_format(time_str):
        return 'שעה לא תקינה. יש לוודא שהשעה בפורמט HH:MM', None, None

    parsed = validate_appointment_input(data)
    if parsed[0]:
        return parsed[0], None, None

    return None, parsed[1]['start_time'], parsed[1]['end_time']


def validate_israeli_id(id_number):
    if not re.match(r'^\d{9}$', id_number):
        return {'error': 'תעודת הזהות אינה תקינה.'}, 400

    digits = [int(d) for d in id_number]
    checksum = sum(
        d if i % 2 == 0 else (d * 2 if d * 2 < 10 else d * 2 - 9)
        for i, d in enumerate(digits[:-1])
    ) + digits[-1]

    if checksum % 10 != 0:
        return {'error': 'תעודת הזהות אינה תקינה.'}, 400

    return None, None


def is_valid_phone_number(phone: str) -> bool:
    # הסרה של רווחים ומקפים
    cleaned = re.sub(r'[-\s]', '', phone)
    # בדיקת פורמט: מתחיל ב-05 וכולל 10 ספרות
    return re.fullmatch(r'^05\d{8}$', cleaned) is not None


def is_valid_email(email):
    """
    בודקת אם כתובת הדוא"ל תקינה לפי תבנית בסיסית
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def is_time_available(start_str, end_str):
    start = datetime.fromisoformat(start_str)
    end = datetime.fromisoformat(end_str)

    if start.weekday() not in WEEKDAYS or not (BUSINESS_HOURS[0] <= start.hour < BUSINESS_HOURS[1]):
        return False

    events = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start.isoformat(),
        timeMax=end.isoformat(),
        singleEvents=True
    ).execute()

    return len(events.get('items', [])) == 0


