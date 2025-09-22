import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import datetime

# Google Sheets auth
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

# Open the sheet (তোমার Sheet নাম দিয়ে চেঞ্জ করো)
sheet = client.open("Delta_Data").sheet1  # sheet1 হলো প্রথম ওয়ার্কশীট

# Delta Exchange API call (উদাহরণ, তোমার API URL দিয়ে চেঞ্জ করো)
url = "https://api.delta.exchange/v2/products"  # তোমার actual API endpoint
response = requests.get(url)
data = response.json()  # অথবা response.text যদি JSON না হয়

# Save data to sheet
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
sheet.append_row([timestamp, str(data)])  # ডাটা যেভাবে চাও সেভ করো
