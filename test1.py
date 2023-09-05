import gspread
import pandas as pd

# Authenticate using the JSON key file you obtained from Google Cloud Console
gc = gspread.service_account(filename='your-credentials.json')

# Open the Google Sheets spreadsheet by its title or URL
spreadsheet = gc.open('https://docs.google.com/spreadsheets/d/1AG89W1nwRzZxYreM6i1qmwS6APf-8GM2K_HDyX7REG4/edit#gid=0')

# Select a specific worksheet (by title or index)
worksheet = spreadsheet.worksheet('교육과정수료현황')  # Replace 'Sheet1' with your sheet name

# Get all values from the worksheet as a list of lists
data = worksheet.get_all_values()

# Convert the data into a Pandas DataFrame
df = pd.DataFrame(data[1:], columns=data[0])

# Now you have your Google Sheets data in a Pandas DataFrame (df)
print(df)