
import os

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_CREDENTIALS_PATH')
# CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID')
CALENDAR_ID = 's0504128406@gmail.com'
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('calendar', 'v3', credentials=credentials)

BUSINESS_HOURS = (9, 17)  # 9:00–17:00
WEEKDAYS = [0, 1, 2, 3, 4]  # Monday–Friday
