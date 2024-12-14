#BLS_data_collection

import requests
import json
import prettytable
import pandas as pd
headers = {'Content-type': 'application/json'}
data = json.dumps({"seriesid": ['LNS12000000',
                                'LNS13000000',
                                'LNS14000000', 
                                'CES0000000001',
                                'CES0500000002', 
                                'CES0500000003' ],"startyear":"2019", "endyear":"2024"})
p = requests.post('https://api.bls.gov/publicAPI/v1/timeseries/data/', data=data, headers=headers)




