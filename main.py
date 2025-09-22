import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# Google Sheets auth
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

# Open the sheet
sheet = client.open("Delta_Data").sheet1

# Get current time in IST
ist = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d %H:%M:%S")

# Save IST timestamp to Google Sheets
try:
    sheet.append_row([ist, "Script ran successfully", "Success"])
except Exception as e:
    sheet.append_row([ist, str(e), "Error"])
