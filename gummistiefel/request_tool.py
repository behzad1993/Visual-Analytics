import requests
import pandas as pd
import plotly.express as px

main_url = "http://rz-vm154.gfz-potsdam.de:8080/highprecip/events/"


def getRequest(id):
    request_url = main_url + "get?id=" + id
    print(request_url)
    response_json = requests.get(request_url).text
    return response_json


def queryRequest(parameters):
    request_url = main_url + "query?"
    for parameter in parameters:
        request_url += "subset=" + parameter + "&"
    print(request_url)
    response_json = requests.get(request_url).text
    return response_json


def getDataframeForGraph(parameters):
    response = queryRequest(parameters)
    df = pd.read_json(response)
    return df
