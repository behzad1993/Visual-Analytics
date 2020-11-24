# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 13:56:01 2020

@author: David
"""

import requests
import pandas as pd
from request_tool import getRequest

response = requests.get("http://rz-vm154.gfz-potsdam.de:8080/highprecip/events/query") 
json = response.json()


dfs = []
num_events = len(json)

for index, event in enumerate(json[0:100000]):
    print("Requesting {}/{}".format(index, num_events))
    
    event_id = event['id']
    event_area = event['area']
    event_length = event['length']
    event_si = event['si']
    event_start = event['start']

    response = getRequest(event_id)
    event_dict = response.json()

    for timeserie in event_dict["timeseries"]:       
        timeserie["event_area"] = event_area
        timeserie["event_length"] = event_length
        timeserie["event_si"] = event_si
        timeserie["event_start"] = event_start
        dfs.append(timeserie)

data = pd.DataFrame(dfs)
data = data.rename(columns={'index':'event_id'})




