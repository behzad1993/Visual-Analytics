# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 15:03:35 2020
@author: David
"""


#https://plotly.github.io/plotly.py-docs/generated/plotly.express.scatter_mapbox.html
#https://plotly.com/python/builtin-colorscales/
#!pip install plotly_express
#!pip install dash
#!pip install pandas
#!pip install numpy
#!pip install matplotlib

import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import numpy as np
import pandas as pd
import copy
import matplotlib.pyplot as plt
import plotly.express as px
import dash
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html


# =============================================================================
# Settinga & Data
# =============================================================================
app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server


mapbox_token = 'pk.eyJ1IjoiZGF2aWQ5OTgiLCJhIjoiY2tobWliNDdrMGZvYTJxazFvcXpseHFvZSJ9.CpgPLYfVXI3qUH4zI90gBQ'

# df = pd.read_csv("../events_all.csv")
# df = df[df['event_si'] >= 0.01]
#df = pd.read_csv("events_filtered_country.csv")
#df['event_start'] = pd.to_datetime(df['event_start'])
#df['event_year'] = df['event_start'].dt.year
#df['event_month'] = df['event_start'].dt.month
#df['country'] = df['country'].fillna('INT')
#df.to_pickle("event_filtered.pickle")

#df.dtypes

df = pd.read_pickle("event_filtered.pickle")
df['event_si'] = df['event_si'] * 100
df['event_area'] = df['event_area'] * 10
df.reset_index(inplace=True, drop=True)

#df['event_si'].describe()
si_labels = ['Weak', 'Medium', 'Strong', 'Very Strong']
df['label_si'] = pd.cut(df['event_si'], bins=[0, 4, 10, 50, 300],labels=si_labels)

country_list = sorted(list(df['country'].unique()))
countries_options = [
    {"label": str(country), "value": str(country)}
    for country in country_list
]

# =============================================================================
# Header
# =============================================================================
# Create app layout
app.layout = html.Div([
    
    # empty Div to trigger javascript file for graph resizing
    html.Div(id="output-clientside"),
   
    
    html.Div([
         html.Div(
             [html.Img(src=app.get_asset_url("rain-logo.png"),id="plotly-image",
                     style={"height": "100px","width": "auto","margin-bottom": "0px"})],
             className="one-third column",
         ),
         
     
         html.Div(
             [html.Div([
                         html.H3("Heavy Rain Events", style={"margin-bottom": "0px"}),
                         html.H4("in Central Europe", style={"margin-top": "0px"}),
                         html.H5("-Vergleichsanalyse-", style={"margin-top": "0px"}),])],
             className="one-half column",id="title",
         ),
         
         
         html.Div(
             [html.A(html.Button("Switch to: Einzelanalyse", id="learn-more-button"),
                          href="http://127.0.0.1:8080/single",)],
             className="one-third column", id="button",
         ),
     ],
         id="header",
         className="row flex-display",
         style={"margin-bottom": "25px"},
     ),

# =============================================================================
# Filters                
# =============================================================================
html.Div([
    html.Div([
        
       #Filter Year 
       html.P("Year",className="control_label"),
       html.Div(id='output_year',className="filter-label"),
       dcc.RangeSlider(
           id='year_slider',
           min=1979,
           max=2017,
           value=[1990, 2002],
           marks={
               1980: {'label': '1980'},
               1985: {'label': '1985'},
               1990: {'label': '1990'},
               1995: {'label': '1995'},
               2000: {'label': '2000'},
               2005: {'label': '2005'},
               2010: {'label': '2010'},
               2015: {'label': '2015'}
           },
           included=True
       )  ,
       
       #Filter Year 
       html.P("Month",className="control_label"),
       html.Div(id='output_month',className="filter-label"),
       dcc.RangeSlider(
           id='month_slider',
           min=1,
           max=12,
           value=[1, 12],
           marks={
               1: {'label': '1'},
               2: {'label': '2'},
               3: {'label': '3'},
               4: {'label': '4'},
               5: {'label': '5'},
               6: {'label': '6'},
               7: {'label': '7'},
               8: {'label': '8'},
               9: {'label': '9'},
               10: {'label': '10'},
               11: {'label': '11'},
               12: {'label': '12'}
           },
           included=True
       ),
       
       #Filter Severity
       html.P("Severity",className="control_label"),
       html.Div(id='output_si',className="filter-label"),
       dcc.RangeSlider(
           id='si_slider',
           min=0,
           max=250,
           value=[30, 250],
           marks={
               0: {'label': '0'},
               50: {'label': '0.5'},
               100: {'label': '1'},
               150: {'label': '1.5'},
               200: {'label': '2'},
               250: {'label': '2.5'}
           },
           included=True
       ),
       
       #Filter Area
       html.P("Area",className="control_label"),
       html.Div(id='output_area',className="filter-label"),
       dcc.RangeSlider(
           id='area_slider',
           min=0,
           max=200,
           value=[0, 200], #max 17.45 -> 200
           marks={
               0: {'label': '0'},
               50: {'label': '50'},
               100: {'label': '100'},
               150: {'label': '150'},   
               200: {'label': '200'}
                            
           },
           included=True
       ),
          
       #Filter Hours
       html.P("Hour",className="control_label"),
       html.Div(id='output_hours',className="filter-label"),
       dcc.RangeSlider(
           id='hours_slider',
           min=1,
           max=100,
           value=[1, 100], 
           marks={
               1: {'label': '0'},
               5: {'label': '5'},
               10: {'label': '10'},
               24: {'label': '24'},
               100: {'label': '100'},                        
           },
           included=True
       ),
      
       #Select color-map-feature radio button
       html.P("Select variable as color:",className="control_label"),
       dcc.RadioItems(
           className="control_label",
           id='map_size_radio_items',
           options=[
               {'label': 'Year', 'value': 'event_year'},
               {'label': 'Severity', 'value': 'event_si'}
           ],
           value='event_year',
           labelStyle={'display': 'inline-block'}
       ),html.Div(id='output_size_button'),

       #Select country
       html.P("Country",className="control_label"),                          
        dcc.Dropdown(
            id="country_selector",
            options=countries_options,
            multi=True,
            value=country_list,
            className="dcc_control",
        ),#html.Div(id='output_country_list'),
           
                              
       ],             
    className="pretty_container four columns",
    id="cross-filter-options",
),

                
               
# =============================================================================
# Plots                
# =============================================================================
    html.Div([
        html.Div(
            [dcc.Graph(id="map")],
            className="pretty_container",
            #id="map",
            #className="pretty_container",
        )],
        id="right-column",
        className="eight columns",
    )],
 className="row flex-display",
 ), #END DIV ROW 1


    
#DIV ROW 2
    html.Div(
        [
            html.Div(
                [dcc.Graph(id="count_year_graph")],
                  className="pretty_container seven columns",
            ),
            html.Div(
                [dcc.Graph(id="map_events_graph")],
                  className="pretty_container five columns",
            ),
        ],
        className="row flex-display",
    ),

#DIV ROW 3        
    html.Div(
        [
            html.Div(
                [dcc.Graph(id="count_month_graph")],
                className="pretty_container seven columns",
            ),
            html.Div(
                [dcc.Graph(id="si_pie_graph")],
                className="pretty_container five columns",
            ),
        ],
        className="row flex-display",
    ),      


        
        
        
#Close Header        
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)
# =============================================================================
# Functions
# =============================================================================
def filter_events(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list):
    tmp = df[df["country"].isin(country_list)]
    tmp = tmp[(df['event_year'] >= year_range[0]) & (df['event_year'] <= year_range[1])]
    tmp = tmp[(tmp['event_month'] >= month_range[0]) & (tmp['event_month'] <= month_range[1])]
    tmp = tmp[(tmp['event_si'] >= si_range[0]) & (tmp['event_si'] <= si_range[1])]
    tmp = tmp[(tmp['event_area'] >= area_range[0]) & (tmp['event_area'] <= area_range[1])]
    tmp = tmp[(tmp['event_length'] >= hours_range[0]) & (tmp['event_length'] <= hours_range[1])]
    return tmp

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    mapbox=dict(
        accesstoken=mapbox_token,
        style="light",
        center=dict(lon=-78.05, lat=42.54),
        zoom=7,
    ),
)
                        
# =============================================================================
# Callbacks
# =============================================================================


@app.callback(
    Output("output_year", "children"),
    [Input("year_slider", "value")])
def update_filter_year(year_slider):
    return str(year_slider)


@app.callback(
    Output("output_month", "children"),
    [Input("month_slider", "value")])
def update_filter_month(year_slider):
    return str(year_slider)


@app.callback(
    Output("output_si", "children"),
    [Input("si_slider", "value")])
def update_filter_si(si_slider):
    return str(si_slider)


@app.callback(
    Output("output_area", "children"),
    [Input("area_slider", "value")])
def update_filter_area(area_slider):
    return str(area_slider)


@app.callback(
    Output("output_hours", "children"),
    [Input("hours_slider", "value")])
def update_filter_hours(hours_slider):
    return str(hours_slider)

# @app.callback(
#     Output("output_country_list", "children"),
#     [Input("country_selector", "value")])
# def update_filter_hours(country_selector):
#     return str(country_selector)

# @app.callback(
#     Output("output_size_button", "children"),
#     [Input("map_size_radio_items", "value")])
# def update_filter_buttons(map_size_radio_items):
#     return str(map_size_radio_items)


@app.callback(
    Output(component_id='map', component_property='figure'),
    [Input("year_slider", "value"),
     Input("month_slider", "value"),
     Input("si_slider", "value"),
     Input("area_slider", "value"),
     Input("map_size_radio_items", "value"),
     Input("hours_slider", "value"),
     Input("country_selector", "value")])
def plot_scatter_mapbox(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list): 

    tmp = filter_events(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list)
    

    #plot map
    #https://plotly.com/python/reference/scattermapbox/
    px.set_mapbox_access_token(mapbox_token)
    fig = px.scatter_mapbox(tmp,
                            lat="lat", lon="lon", 
                            color=map_size_radio_items, 
                            text='event_id',
                            size="area", size_max=20, 
                            zoom=3,
                            color_continuous_scale=px.colors.sequential.Inferno)    
    
    fig.update_traces(mode='markers', selector=dict(type='scattermapbox'))
    fig.update_layout(
        autosize = True,
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor="#F9F9F9",
        legend=dict(font=dict(size=10), orientation="h"),
        plot_bgcolor="#F9F9F9",       
        mapbox=dict(style="light")
        )
    
    return fig


#Main graph -> individual graph
@app.callback(Output("map_events_graph", "figure"), [Input("map", "hoverData")])
def plot_map_events_graph(map_events_graph):

    layout_individual = copy.deepcopy(layout)
    
    try:
        event_id = int(map_events_graph['points'][0]['text']) 
    except:
        event_id = 201706413
        
    tmp = df[df['event_id'] == event_id ]


    data = [
        # dict(
        #     type="scatter",
        #     mode="lines+markers",
        #     name="Severity",
        #     x=tmp.date,
        #     y=tmp.si * 1000,
        #     line=dict(shape="spline", smoothing=2, width=1, color="#a9bb95"),
        #     marker=dict(symbol="diamond-open"),
        # ),
        dict(
            type="scatter",
            mode="lines+markers",
            name="Area",
            x=tmp.date,
            y=tmp.area * 10,
            line=dict(shape="spline", smoothing=2, width=1, color="#92d8d8"),
            marker=dict(symbol="diamond-open"),
        ),
        dict(
            type="scatter",
            mode="lines+markers",
            name="Max Precipitation",
            x=tmp.date,
            y=tmp.maxPrec,
            line=dict(shape="spline", smoothing=2, width=1, color="#fac1b7"),
            marker=dict(symbol="diamond-open"),
        ),
    ]
    layout_individual["title"] = str('Event ' + str(event_id) + ' (map hover)')

    figure = dict(data=data, layout=layout_individual) 
    return figure


@app.callback(
    Output(component_id='count_year_graph', component_property='figure'),
    [Input("year_slider", "value"),
     Input("month_slider", "value"),
     Input("si_slider", "value"),
     Input("area_slider", "value"),
     Input("map_size_radio_items", "value"),
     Input("hours_slider", "value"),
     Input("country_selector", "value")])
def plot_count_year(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list): 
    
    tmp = filter_events(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list)
    tmp = tmp.drop_duplicates(subset='event_id', keep='first')
    tmp = tmp.groupby('event_year').event_id.count().reset_index()
      
    layout_count = copy.deepcopy(layout)

    data = [
        dict(
            type="scatter",
            mode="markers",
            x=tmp.event_year,
            y=tmp.event_id,
            name="unique events",
            opacity=0,
            hoverinfo="skip",
        ),
        dict(
            type="bar",
            x=tmp.event_year,
            y=tmp.event_id,
            name="unique events",
            marker=dict(color="rgb(123, 199, 255)"),
        ),
    ]

    layout_count["title"] = "Events/Year"
    layout_count["dragmode"] = "select"
    layout_count["showlegend"] = False
    layout_count["autosize"] = True

    figure = dict(data=data, layout=layout_count)
    return figure


@app.callback(
    Output(component_id='count_month_graph', component_property='figure'),
    [Input("year_slider", "value"),
     Input("month_slider", "value"),
     Input("si_slider", "value"),
     Input("area_slider", "value"),
     Input("map_size_radio_items", "value"),
     Input("hours_slider", "value"),
     Input("country_selector", "value")])
def plot_count_month(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list): 
    
    tmp = filter_events(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list)
    tmp = tmp.drop_duplicates(subset='event_id', keep='first')
    tmp = tmp.groupby('event_month').event_id.count().reset_index()

    months = pd.DataFrame({'event_month':[1,2,3,4,5,6,7,8,9,10,11,12], 'event_id':[0,0,0,0,0,0,0,0,0,0,0,0]})    	
    tmp = tmp.append(months).drop_duplicates(subset='event_month', keep='first')      

    layout_count = copy.deepcopy(layout)

    data = [
        dict(
            type="scatter",
            mode="markers",
            x=tmp.event_month,
            y=tmp.event_id,
            name="unique events",
            opacity=0,
            hoverinfo="skip",
        ),
        dict(
            type="bar",
            x=tmp.event_month,
            y=tmp.event_id,
            name="unique events",
            marker=dict(color="rgb(123, 199, 255)"),
        ),
    ]

    layout_count["title"] = "AVG Events/Month"
    layout_count["dragmode"] = "select"
    layout_count["showlegend"] = False
    layout_count["autosize"] = True

    figure = dict(data=data, layout=layout_count)
    return figure



# Selectors, main graph -> pie graph
@app.callback(
    Output(component_id='si_pie_graph', component_property='figure'),
    [Input("year_slider", "value"),
     Input("month_slider", "value"),
     Input("si_slider", "value"),
     Input("area_slider", "value"),
     Input("map_size_radio_items", "value"),
     Input("hours_slider", "value"),
     Input("country_selector", "value")])
def plot_count_month(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list): 

    layout_pie = copy.deepcopy(layout)
    si_range = [0,300]
    tmp = filter_events(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list)
    tmp = tmp.drop_duplicates(subset='event_id', keep='first')
    tmp = tmp.groupby('label_si').event_id.count().reset_index()



    data = [
        dict(
            type="pie",
            labels=si_labels,
            values=tmp.event_id,
            #name="Production Breakdown",
            # text=[
            #     "Total Gas Produced (mcf)",
            #     "Total Oil Produced (bbl)",
            #     "Total Water Produced (bbl)",
            # ],
            hoverinfo="text+value+percent",
            textinfo="label+percent+value",
            # hole=0.5,
            marker=dict(colors=["#fac1b7", "#a9bb95", "#92d8d8", "#72d8d8"]),
            #domain={"x": [0, 0.45], "y": [0.2, 0.8]},
        ),
        # dict(
        #     type="pie",
        #     labels=[WELL_TYPES[i] for i in aggregate.index],
        #     values=aggregate["API_WellNo"],
        #     name="Well Type Breakdown",
        #     hoverinfo="label+text+value+percent",
        #     textinfo="label+percent+name",
        #     hole=0.5,
        #     marker=dict(colors=[WELL_COLORS[i] for i in aggregate.index]),
        #     domain={"x": [0.55, 1], "y": [0.2, 0.8]},
        # ),
    ]
    layout_pie["title"] = "Severity of Events: {} to {}".format(
        year_range[0], year_range[1]
    )
    layout_pie["font"] = dict(color="#777777")
    layout_pie["legend"] = dict(
        font=dict(color="#CCCCCC", size="4"), orientation="h", bgcolor="rgba(0,0,0,0)"
    )

    figure = dict(data=data, layout=layout_pie)
    return figure

    
    
    
# =============================================================================
# Main
# =============================================================================

def run_server():
    app.run_server(debug=True, port=8882, use_reloader=False)

if __name__ == "__main__":
    run_server()