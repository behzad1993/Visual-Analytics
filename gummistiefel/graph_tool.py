"""
Created on Nov 15, 2020

@author: Akhmad
"""

import plotly.express as px

custom_labels = {"start": "start", "si": "si"}


def getGraph(df, x_column, y_column):
    fig = px.scatter(df,
                     x=x_column,
                     y=y_column,
                     labels=custom_labels,
                     title='Visual Analytics')
    return fig


def getMap(df):
    # https://plotly.com/python/mapbox-layers/
    fig = px.scatter_mapbox(df, lat="event_lat", lon="event_lon", hover_name="main_start", hover_data=["event_stdv", "event_si"],
                            color_discrete_sequence=["fuchsia"], zoom=3, height=300)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig
