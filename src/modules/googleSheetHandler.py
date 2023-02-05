from __future__ import print_function

import os.path
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1s6QsVH1MHG1-OBUabHIWrdHM71zbgNmo7Vx1UEBtWro'
SAMPLE_RANGE_NAME = 'Sheet1!A1:C'

def googleSheetUpdater(POTicketNumber, POTicketDescription, POTicketStatus, userName):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return

        print("This could be the total number of rows in the google sheet:", len(values))
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print(row)
        
        currTotalRows = len(values)
        # sheet.update_cell(currTotalRows + 1, 0, time.time) #For updating the time stamp
        # sheet.update_cell(currTotalRows + 1, 1, userName) #For updating the username
        # sheet.update_cell(currTotalRows + 1, 2, POTicketNumber) #For updating the PO ticket number
        # sheet.update_cell(currTotalRows + 1, 3, POTicketDescription) #For updating the PO ticket description
        # sheet.update_cell(currTotalRows + 1, 4, POTicketStatus) #For updating the PO ticket status
        values = [
            [str(datetime.now()), userName, POTicketNumber, POTicketDescription, POTicketStatus]
        ]
        range = "A" + str(currTotalRows + 1) + ":F" + str(currTotalRows + 1)
        print("These are the values that we are passing to the update function:", values, range)
        updateSheetValues(creds, range, values)

    except HttpError as err:
        print(err)

def updateSheetValues(creds,range_name, values, spreadsheet_id = SPREADSHEET_ID, value_input_option = "USER_ENTERED"):
    # pylint: disable=maybe-no-member
    try:
        service = build('sheets', 'v4', credentials=creds)
        body = {
            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()
        print(f"{result.get('updatedCells')} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error
