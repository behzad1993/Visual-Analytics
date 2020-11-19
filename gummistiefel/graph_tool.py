"""
Created on Nov 15, 2020

@author: Akhmad
"""

import plotly.express as px

custom_labels = {"start": "start", "si": "si"}


def getGraph(df, x_column, y_column):
    fig = px.line(df,
                  x=x_column,
                  y=y_column,
                  labels=custom_labels,
                  title='Visual Analytics')
    return fig
