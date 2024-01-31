#Imports for sheet integration
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pintref import u,Q_


class Sheet():
    # Defines the scope that the Google OAuth will ask to modify.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    #Initialize with SHEET ID
    #PINT_MODE 
    def __init__(self,SHEET_ID,PINT_MODE = 0):
        # Define the TEMP Sheet ID.
        self.SHEET_ID = SHEET_ID
        #Initialize the sheet (this creates the self.sheet object). Returns true if sucessfull.
        self.initialized = self.initalizeSheets()
        if PINT_MODE == "ENABLED" or PINT_MODE == 1:
            self.PINT_MODE = 1
        elif PINT_MODE == 0 or PINT_MODE == "DISABLED":
            self.PINT_MODE = 0
        else:
            print("Incorrect paramter for Pint Mode given. Should be 0,1,Enabled,Disabled")
            

    def __str__(self):
        return f'Sheet ID: {self.SHEET_ID} and its initilization state is: {self.initialized}'

    #Function to generate token.json using present credentials.json and verify it if it is already present.
    #Looks for credentials/existing token in current working directory.
    def initalizeSheets(self):
        creds = None
        if not(os.path.exists('credentials.json')):
            exit('Gsheet needs a valid credentials file. Please supply one in the current working directory.')
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
            print("GSheet found token.json file")

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            print("GSheets could not find token JSON file or credentials have expired. Generating new!")
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        service = build('sheets', 'v4', credentials=creds)
        #Set the self.sheet variable to our spreadsheet object.
        self.sheet = service.spreadsheets()
        return True
    

    #Function to read from a range. Accepts named ranged and A1 notation.
    def read(self,RANGE):
        try:
            if self.PINT_MODE == 1:
                #if you wanted to read/write a named range instead of A1 values, you just put the name of the named range in quotes.
                result = self.sheet.values().get(spreadsheetId=self.SHEET_ID, range=RANGE).execute()
                values = result.get('values',[])
                
                quant = Q_(float(values[0][0]),values[0][1])
                return quant
            else:
                result = self.sheet.values().get(spreadsheetId=self.SHEET_ID, range=RANGE).execute()
                values = result.get('values',[])

                #If reading one value, don't return a 2d array.
                #If reading one row, just return that row. Not a 2d array.
                if len(values) == 1:
                    values = values[0]
                    if len(values[0]) == 1:
                        values = values[0]

                return values
        except HttpError as err:
            print(err)

    #Function to write values to range. Accetps named range and A1 Notation.
    def write(self,RANGE,DATA):
        if self.PINT_MODE == 1:
            quant = [[DATA.magnitude, str(DATA.units)]]
            DATA = quant

        #Put in dict as required by google sheet API.
        body = {
            'values': DATA
        }
        try:
            result = self.sheet.values().update(spreadsheetId=self.SHEET_ID, range=RANGE, valueInputOption="USER_ENTERED", body=body).execute()
            return result
        except HttpError as err:
            print(err)


    def setPintMode(self,setMode):
        if setMode == 1 or setMode == "ENABLED" or setMode == True:
            self.PINT_MODE = 1
        elif setMode == 0 or setMode == "DISABLED" or setMode == False:
            self.PINT_MODE = 0
        else:
            print("Invalid input for sePintMode. Valid inputs are 1,0,ENABLED,DISABLED,True,False.")

    def returnPintMode(self):
        return self.PINT_MODE






