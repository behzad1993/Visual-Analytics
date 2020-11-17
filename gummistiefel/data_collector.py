# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 13:56:01 2020

@author: David
"""


import requests
import pandas as pd


dfs = []
response = requests.get("http://rz-vm154.gfz-potsdam.de:8080/highprecip/events/query?subset=length(20,100)&subset=si(0.1,0.3)&subset=area(2,5)") 
json = response.json()

for event in json:
    print(event['id'])
    event_id = event['id']
    
    try:
        response = requests.get("http://rz-vm154.gfz-potsdam.de:8080/highprecip/events/get?id=" + event_id)
    except requests.exceptions.HTTPError as errh:
        print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)
    
    event_dict = response.json()

    for timeserie in event_dict["timeseries"]:
        dfs.append(timeserie)
    

data = pd.DataFrame(dfs)
data = data.rename(columns = {"index" : "event_id"})


