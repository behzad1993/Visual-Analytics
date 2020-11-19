"""
Created on Nov 15, 2020

@author: Akhmad
"""

import dash
import dash_core_components as dcc
import dash_html_components as html

colors = {
    'background': 'white',
    'text': 'black'
}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Visual Analytics',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='A web application for Visual Analytics.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Input(id='username', value='Initial Value', type='text'),

    html.Button('Button', id='show-secret'),

    dcc.Graph(
        id='my-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5],
                    'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                }
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=False)
