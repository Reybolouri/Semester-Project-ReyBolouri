#BLS_data_collection

import requests
import os
import pandas as pd
import json
import datetime

URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
API_key = "2e94f53db1984894b301b64867ac70c0"

seriesId = ['LNS12000000',#Civilian Employment (Seasonally Adjusted)
            'LNS13000000',#Civilian Unemployment (Seasonally Adjusted)
            'LNS14000000', #Unemployment Rate (Seasonally Adjusted) 
            'CES0000000001', #Total Nonfarm Employment - Seasonally Adjusted
            'CES0500000002', # Total Private Average Weekly Hours of All Employees - Seasonally Adjusted
            'CES0500000003']#Total Private Average Hourly Earnings of All Employees - Seasonally Adjusted

# Function for collecting  data
def get_bls_data(seriesId, start_year, end_year):
    headers = {'Content-type': 'application/json'}
    data = json.dumps({
        "seriesId": seriesId,
        "startyear": str(start_year),
        "endyear": str(end_year),
        "registrationkey": API_KEY
    })
    response = requests.post(URL, data=data, headers=headers)

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception(f"Failed to collect data: {response.status_code}, {response.text}")