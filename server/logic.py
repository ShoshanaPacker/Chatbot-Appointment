from datetime import datetime

import mysql.connector
from googleapiclient.errors import HttpError

# from error import handle_general_exception
from config import service, CALENDAR_ID
from validator import validate_israeli_id, validate_appointment_input, is_valid_phone_number, is_valid_email, \
    is_time_available, handle_general_exception


# שמירה למסד הנתונים (הוספת תור חדש)
def save_to_db(event_id, user_id, phone, email, start_time, end_time, notes=""):
    conn = mysql.connector.connect(
        host="bz1fm6zwqfueyf94xgxi-mysql.services.clever-cloud.com",
        port=3306,
        user="uaxdsjzmqqypgfap",
        password="xD7LkYCtgvUfCv5yn3SE",
        database="bz1fm6zwqfueyf94xgxi"
    )
    cursor = conn.cursor()

    sql = """
        INSERT INTO appointments (event_id, user_id, phone, email, start_time, end_time, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (event_id, user_id, phone, email, start_time, end_time, notes))
    conn.commit()

    cursor.close()
    conn.close()


# עדכון רשומת תור במסד הנתונים
def update_db(event_id, user_id, phone, email, start_time, end_time, notes):
    conn = mysql.connector.connect(
        host="bz1fm6zwqfueyf94xgxi-mysql.services.clever-cloud.com",
        port=3306,
        user="uaxdsjzmqqypgfap",
        password="xD7LkYCtgvUfCv5yn3SE",
        database="bz1fm6zwqfueyf94xgxi"
    )
    cursor = conn.cursor()

    sql = """
        UPDATE appointments
        SET user_id = %s, phone = %s, email = %s, start_time = %s, end_time = %s, notes = %s
        WHERE event_id = %s
    """
    cursor.execute(sql, (user_id, phone, email, start_time, end_time, notes, event_id))
    conn.commit()

    cursor.close()
    conn.close()


# מחיקת תור ממסד הנתונים


def delete_appointment(event_id, service, CALENDAR_ID):
    try:
        # מחיקה מהיומן
        service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
    except HttpError as e:
        # אם האירוע לא קיים ביומן, ממשיכים למחוק מהמסד
        if e.resp.status != 410 and e.resp.status != 404:
            return {'error': f'שגיאה במחיקת האירוע מהיומן: {str(e)}'}, 500

    try:
        # מחיקה מהמסד
        conn = mysql.connector.connect(
            host="bz1fm6zwqfueyf94xgxi-mysql.services.clever-cloud.com",
            port=3306,
            user="uaxdsjzmqqypgfap",
            password="xD7LkYCtgvUfCv5yn3SE",
            database="bz1fm6zwqfueyf94xgxi"
        )
        cursor = conn.cursor()
        sql = "DELETE FROM appointments WHERE event_id = %s"
        cursor.execute(sql, (event_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return {'message': 'התור נמחק מהמסד ומהיומן בהצלחה.'}, 200

    except Exception as e:
        return {'error': f'שגיאה במחיקת התור מהמסד: {str(e)}'}, 500


# חיפוש תורים לפי ת"ז או תאריך
def search_appointments(user_id=None, date=None):
    conn = mysql.connector.connect(
        host="bz1fm6zwqfueyf94xgxi-mysql.services.clever-cloud.com",
        port=3306,
        user="uaxdsjzmqqypgfap",
        password="xD7LkYCtgvUfCv5yn3SE",
        database="bz1fm6zwqfueyf94xgxi"
    )
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM appointments WHERE 1=1"
    params = []
    if user_id:
        query += " AND user_id = %s"
        params.append(user_id)
    if date:
        query += " AND DATE(start_time) = %s"
        params.append(date)

    cursor.execute(query, tuple(params))
    results = cursor.fetchall()

    cursor.close()
    conn.close()
    return results


# פונקציה לקביעת תור חדש (post)
def post(data):
    user_id = data.get('user_id')
    phone = data.get('phon')
    email = data.get('email')

    error, status = validate_israeli_id(user_id)
    if error:
        return error, status

    if not phone or not is_valid_phone_number(phone):
        return {'error': 'מספר טלפון אינו תקין. יש להזין מספר בפורמט 05XXXXXXXX'}, 400

    if not is_valid_email(email):
        return {'error': 'email לא תקני'}, 400

    error_msg, parsed = validate_appointment_input(data)
    if error_msg:
        return {'error': error_msg}, 400

    start_time = parsed['start_time']
    end_time = parsed['end_time']

    try:
        if not is_time_available(start_time.isoformat(), end_time.isoformat()):
            return {'error': 'התור כבר נקבע למישהו.'}, 409

        summary = f"פגישה עם מזהה {user_id}"

        event = add_event(
            start_time.isoformat(),
            end_time.isoformat(),
            summary,
            extra_fields={'user_id': user_id}
        )

        save_to_db(
            event_id=event['id'],
            user_id=user_id,
            phone=phone,
            email=email,
            start_time=start_time,
            end_time=end_time,
            notes=data.get('notes', '')
        )

        return {
            'message': 'התור נקבע בהצלחה ביומן גוגל ונשמר במסד הנתונים.',
            'event_link': event.get('htmlLink')
        }, 200

    except Exception as e:
        return {'error': f"שגיאה: {str(e)}"}, 500


# פונקציה לעדכון תור קיים (update)
def update_appointment(event_id, data, service, CALENDAR_ID):
    user_id = data.get('user_id')
    phone = data.get('phon')
    email = data.get('email')
    notes = data.get('notes', '')

    error, status = validate_israeli_id(user_id)
    if error:
        return error, status

    error_msg, parsed = validate_appointment_input(data)
    if error_msg:
        return {'error': error_msg}, 400

    start_time = parsed['start_time']
    end_time = parsed['end_time']

    try:
        if not is_time_available(start_time.isoformat(), end_time.isoformat()):
            return {'error': 'התור החדש אינו פנוי או מחוץ לשעות הפעילות.'}, 409

        summary = f"פגישה עם מזהה {user_id}"

        updated_event = service.events().patch(
            calendarId=CALENDAR_ID,
            eventId=event_id,
            body={
                'summary': summary,
                'start': {'dateTime': start_time.isoformat()},
                'end': {'dateTime': end_time.isoformat()},
                'description': f"פגישה עם מזהה {user_id}",
                'extendedProperties': {
                    'private': {
                        'user_id': user_id
                    }
                }
            }
        ).execute()

        update_db(
            event_id=event_id,
            user_id=user_id,
            phone=phone,
            email=email,
            start_time=start_time,
            end_time=end_time,
            notes=notes
        )

        return {
            'message': 'התור עודכן בהצלחה ביומן ובמסד הנתונים.',
            'event_link': updated_event.get('htmlLink')
        }, 200

    except Exception as e:
        return {'error': f"שגיאה בעדכון: {str(e)}"}, 500


def get_all_appointments():
    conn = mysql.connector.connect(
        host="bz1fm6zwqfueyf94xgxi-mysql.services.clever-cloud.com",
        port=3306,
        user="uaxdsjzmqqypgfap",
        password="xD7LkYCtgvUfCv5yn3SE",
        database="bz1fm6zwqfueyf94xgxi"
    )
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM appointments")
    results = cursor.fetchall()

    # המרת שדות datetime למחרוזת בפורמט ISO
    for row in results:
        for key in row:
            if isinstance(row[key], datetime):
                row[key] = row[key].isoformat()

    cursor.close()
    conn.close()
    return results


def add_event(start, end, summary, extra_fields=None):
    user_id = extra_fields.get('user_id') if extra_fields else ""

    event_body = {
        'summary': summary,
        'description': f"פגישה עם מזהה {user_id}",
        'start': {'dateTime': start},
        'end': {'dateTime': end},
        'extendedProperties': {
            'private': {
                'user_id': user_id
            }
        }
    }

    event = service.events().insert(calendarId=CALENDAR_ID, body=event_body).execute()
    return event

def get(service, CALENDAR_ID):
    try:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            singleEvents=True,
            orderBy='startTime',
            timeMin=datetime.utcnow().isoformat() + 'Z'
        ).execute()

        events = events_result.get('items', [])

        formatted_events = [
            {
                'user_id': event.get('extendedProperties', {}).get('private', {}).get('user_id'),
                'summary': event.get('summary'),
                'start': event['start'].get('dateTime', event['start'].get('date')),
                'end': event['end'].get('dateTime', event['end'].get('date')),
                'link': event.get('htmlLink')
            } for event in events
        ]

        return {'events': formatted_events}, 200

    except Exception as e:
        return handle_general_exception(e)


def get_appointments_by_user_id(user_id, service, CALENDAR_ID):
    try:
        # שליפת אירועים מהיומן לפי user_id
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            privateExtendedProperty=f"user_id={user_id}",
            maxResults=2500,
            singleEvents=True,
            timeMin=datetime.utcnow().isoformat() + 'Z',
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        event_map = {event['id']: event for event in events}

        # שליפת נתונים מהמסד על פי user_id
        conn = mysql.connector.connect(
            host="bz1fm6zwqfueyf94xgxi-mysql.services.clever-cloud.com",
            port=3306,
            user="uaxdsjzmqqypgfap",
            password="xD7LkYCtgvUfCv5yn3SE",
            database="bz1fm6zwqfueyf94xgxi"
        )
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM appointments WHERE user_id = %s", (user_id,))
        db_appointments = cursor.fetchall()
        cursor.close()
        conn.close()

        # איחוד הנתונים: מסד + יומן
        combined_appointments = []

        for db_app in db_appointments:
            event = event_map.get(db_app['event_id'])
            if event:
                combined_appointments.append({
                    'event_id': db_app['event_id'],
                    'user_id': db_app['user_id'],
                    'phone': db_app['phone'],
                    'email': db_app['email'],
                    'notes': db_app['notes'],
                    'start_time': db_app['start_time'].isoformat() if isinstance(db_app['start_time'], datetime) else db_app['start_time'],
                    'end_time': db_app['end_time'].isoformat() if isinstance(db_app['end_time'], datetime) else db_app['end_time'],
                    'calendar_summary': event.get('summary'),
                    'calendar_link': event.get('htmlLink')
                })

        return {'appointments': combined_appointments}, 200

    except Exception as e:
        return handle_general_exception(e)