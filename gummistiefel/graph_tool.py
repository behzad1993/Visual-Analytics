import plotly.express as px

custom_labels = {"start": "date", "si": "size"}


def getGraph(df, x_column, y_column):
    fig = px.line(df,
                  x=x_column,
                  y=y_column,
                  labels=custom_labels,
                  title='Visual Analytics')
    return fig
