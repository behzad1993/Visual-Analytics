"""
Created on Nov 15, 2020

@author: Akhmad
"""

import requests
import pandas as pd
import plotly.express as px

main_url = "http://rz-vm154.gfz-potsdam.de:8080/highprecip/events/"


def getRequest(id):
    request_url = main_url + "get?id=" + id
    # print(request_url)
    response_json = requests.get(request_url)
    return response_json


def queryRequest(parameters):
    request_url = main_url + "query?"
    for parameter in parameters:
        request_url += "subset=" + parameter + "&"
    # print(request_url)
    response_json = requests.get(request_url)
    return response_json

# Depreacted


def getDataframeForGraph(parameters):
    response = queryRequest(parameters)
    df = pd.read_json(response.text)
    return df


def getDataframeFromServer(parameters, fullData=False):
    query_response = queryRequest(parameters)
    json = query_response.json()

    dfs = []
    for event in json:
        main_area = event['area']
        event_id = event['id']
        main_length = event['length']
        main_si = event['si']
        main_start = event['start']

        response = getRequest(event_id)
        event_dict = response.json()

        for timeserie in event_dict["timeseries"]:
            if(fullData):
                timeserie["main_area"] = main_area
                timeserie["main_length"] = main_length
                timeserie["main_si"] = main_si
                timeserie["main_start"] = main_start
            dfs.append(timeserie)
    data = pd.DataFrame(dfs)
    data = data.rename(columns={"area": "event_area", "date": "event_date",
                                "index": "event_id", "lat": "event_lat", "latMax": "event_latMax", "lon": "event_lon",
                                "lonMax": "event_lonMax", "maxPrec": "event_maxPrec", "meanPre": "event_meanPre", "si": "event_si", "size": "event_size", "stdv": "event_stdv"})
    return data
