from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from googleapiclient import discovery
import datetime
import threading
import time


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1jjX68ObzNl3QcMqvwPm-m5MFNV5Kgieks0gdqociAbY'
SAMPLE_RANGE_NAME = 'Hoja 1!A1:Z100000'


import hubspot
from hubspot.crm.contacts import ApiException

client = hubspot.Client.create(access_token="pat-na1-a99cdf8e-0af7-401f-8396-6a25f8f582ee")

def get_leads():
    try:
        all_contacts = client.crm.contacts.get_all(
            properties=["hs_lead_status", "phone", "firstname", "lastname", "hubspot_owner_id", "createdate"])
        leads = []
        for lead in all_contacts:
            leads.append(lead.to_dict())
        # return JsonResponse({'leads': leads})
        return leads
    except ApiException as e:
        print("Exception when calling basic_api->get_page: %s\n" % e)

def check_hour():
    hour = datetime.datetime.now().hour
    return hour

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
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
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    while True:
        hour = check_hour()
        
        print(hour)
        if(hour == 14 or hour == 23):
            print("Ejecutando")
            try:
                service = discovery.build('sheets', 'v4', credentials=creds)

                # Call the Sheets API
                sheet = service.spreadsheets()
                request = sheet.values().clear(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                            range=SAMPLE_RANGE_NAME, body={})
                response = request.execute()
                print("Cargando leads...")
                leads = get_leads()
                data = []
                for lead in leads:
                    lead_data = []
                    lead_data.append(lead["properties"]["firstname"])
                    lead_data.append(lead["properties"]["lastname"])
                    lead_data.append(lead["properties"]["phone"])
                    lead_data.append(lead["properties"]["hs_lead_status"])

                    data.insert(0, lead_data)
                    
                data.insert(0, ["Nombre", "Apellido", "Telefono", "Estado"])


                
                value_input_option = "USER_ENTERED"
                insert_data_option = 'OVERWRITE'
                value_range_body = {
                    "majorDimension": "DIMENSION_UNSPECIFIED",
                    "range": "Hoja 1!A1:Z100000",
                    "values": data
                    }    
                    
                
                append = sheet.values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)

                response = append.execute()

                print("Leads cargados en sheet")
                
                    
            except HttpError as err:
                print(err) 

        
        time.sleep(3600)    
    


t=threading.Thread(target=main)
t.start()