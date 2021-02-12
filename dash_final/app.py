# -*- coding: utf-8 -*-

# https://plotly.github.io/plotly.py-docs/generated/plotly.express.scatter_mapbox.html
# https://plotly.com/python/builtin-colorscales/
# !pip install plotly_express
# !pip install dash
# !pip install pandas
# !pip install numpy
# !pip install matplotlib
# !pip install dash_daq
# !pip install bubbly
# !pip install joblib

import os

os.environ['OPENBLAS_NUM_THREADS'] = '1'
import pandas as pd
import copy
import plotly.express as px
import dash
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import data_builder
import dash_daq as daq
from bubbly.bubbly import bubbleplot
import plotly.graph_objects as go
from plotly.subplots import make_subplots


import warnings; warnings.simplefilter('ignore')

color_set = ['#72d499','#cbabff','#fcc168','#f08686','#88ccee','#b5e66c']
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
# df = pd.read_csv("events_filtered_country.csv")
# df['event_start'] = pd.to_datetime(df['event_start'])
# df['event_year'] = df['event_start'].dt.year
# df['event_month'] = df['event_start'].dt.month
# df['country'] = df['country'].fillna('INT')
# df.to_pickle("event_filtered.pickle")
# df.dtypes

df = pd.read_pickle("event_filtered.pickle")

df['event_si'] = df['event_si'] * 100
df['event_area'] = df['event_area'] * 10
df.reset_index(inplace=True, drop=True)

# df['event_si'].describe()
si_labels = ['Weak', 'Medium', 'Strong', 'Very Strong']
df['label_si'] = pd.cut(df['event_si'], bins=[0, 4, 10, 50, 300], labels=si_labels)

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
        # html.Div(
        #     [html.Img(src=app.get_asset_url("rain-logo.png"), id="plotly-image",
        #               style={"height": "100px", "width": "auto", "margin-bottom": "0px"})],
        #     className="one-third column",
        # ),

        html.Div(
            [html.Div([
                html.H1("Heavy Rain Events", style={"margin-bottom": "0px","margin-top": "40px"}),
                html.H3("in Central Europe", style={"margin-top": "0px"}), ])],
            id="title", #className="one-half column",
        ),

        # html.Div(
        #     [html.A(html.Button("About us", id="learn-more-button"),
        #             href="https://www.hu-berlin.de/de", )],
        #     className="one-third column", id="button",
        # ),
    ],
        id="header",
        className="row", #flex-display
        style={"margin-bottom": "25px"},
    ),

    # =============================================================================
    # EINZEL / VERGLEICH SLIDER #
    # =============================================================================

    # DIV ROW 2
    html.Div(
        [
            html.Div(
                html.Label("Individual analysis"),
                className="five columns",
                style={'textAlign': 'right','font-size':'20px'}
            ),
            html.Div(

                html.Div([
                    daq.ToggleSwitch(size=60,
                                     id='my-input',
                                     value=False
                                     ),

                    html.Div(id='toggle-switch-output')
                ]),
                className="two columns",
            ),

            html.Div(
                html.Label("Comparative analysis"),
                className="five columns",
                style={'textAlign': 'left','font-size':'20px'}
            ),

        ],
        className="row flex-display",style={'padding-bottom':'20px'}
    ),

    # =============================================================================
    # CONTAINER SINGLE START
    # =============================================================================

    html.Div(
        id="single-container",
        children=[

            # =============================================================================
            # Filters 
            # =============================================================================

            html.Div([
                
                # First filter
                html.Div([
                    # Filter Year
                    html.Span("Year", className="control_label"),
                    html.Span(id='output_year', className="filter-label"),
                    dcc.RangeSlider(
                        id='year_slider',
                        min=1979,
                        max=2017,
                        value=[1979, 2017],
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
                    ),

                    # Filter Year
                    html.Span("Month", className="control_label"),
                    html.Span(id='output_month', className="filter-label"),
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

                    # Filter Severity
                    html.Span("Severity", className="control_label"),
                    html.Span(id='output_si', className="filter-label"),
                    dcc.RangeSlider(
                        id='si_slider',
                        min=0,
                        max=250,
                        value=[0, 250],
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

                    # Filter Area
                    html.Span("Area", className="control_label"),
                    html.Span(id='output_area', className="filter-label"),
                    dcc.RangeSlider(
                        id='area_slider',
                        min=0,
                        max=200,
                        value=[0, 200],  # max 17.45 -> 200
                        marks={
                            0: {'label': '0'},
                            50: {'label': '50'},
                            100: {'label': '100'},
                            150: {'label': '150'},
                            200: {'label': '200'}

                        },
                        included=True
                    ),

                    # Filter Hours
                    html.Span("Hour", className="control_label"),
                    html.Span(id='output_hours', className="filter-label"),
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
                            48: {'label': '48'},
                            72: {'label': '72'},
                            100: {'label': '100'},
                        },
                        included=True
                    ),

                    # Select color-map-feature radio button
                    html.P("Select variable as color:", className="control_label"),
                    dcc.RadioItems(
                        className="control_label",
                        id='map_size_radio_items',
                        options=[
                            {'label': 'Year', 'value': 'event_year'},
                            {'label': 'Severity', 'value': 'event_si'}
                        ],
                        value='event_year',
                        labelStyle={'display': 'inline-block'}
                    ), html.Div(id='output_size_button'),

                    # Select time intervals 
                    html.P("Select time interval:", className="control_label"),
                    dcc.RadioItems(
                        className="control_label",
                        id='interval_radio_items',
                        options=[
                            {'label': '1 year', 'value': 1},
                            {'label': '3 year', 'value': 3},
                            {'label': '5 years', 'value': 5},
                            {'label': '7 years', 'value': 7},
                            {'label': '10 years', 'value': 10}
                        ],
                        value=5,
                        labelStyle={'display': 'inline-block'}
                    ), html.Div(id='output_interval_button'),

                    # Select country
                    html.P("Country", className="control_label"),
                    dcc.Dropdown(
                        id="country_selector",
                        options=countries_options,
                        multi=True,
                        value=country_list,
                        className="dcc_control",
                    ),

                ],
                    className="pretty_container five columns",
                    id="cross-filter-options",
                    style={'backgroundColor': 'white'}
                ),
                
                
                # Second filter
                html.Div([
                    # Filter Year
                    html.Span("Year", className="control_label"),
                    html.Span(id='output_year_2', className="filter-label"),
                    dcc.RangeSlider(
                        id='year_slider_2',
                        min=1979,
                        max=2017,
                        value=[1979, 2017],
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
                    ),

                    # Filter Year
                    html.Span("Month", className="control_label"),
                    html.Span(id='output_month_2', className="filter-label"),
                    dcc.RangeSlider(
                        id='month_slider_2',
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

                    # Filter Severity
                    html.Span("Severity", className="control_label"),
                    html.Span(id='output_si_2', className="filter-label"),
                    dcc.RangeSlider(
                        id='si_slider_2',
                        min=0,
                        max=250,
                        value=[0, 250],
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

                    # Filter Area
                    html.Span("Area", className="control_label"),
                    html.Span(id='output_area_2', className="filter-label"),
                    dcc.RangeSlider(
                        id='area_slider_2',
                        min=0,
                        max=200,
                        value=[0, 200],  # max 17.45 -> 200
                        marks={
                            0: {'label': '0'},
                            50: {'label': '50'},
                            100: {'label': '100'},
                            150: {'label': '150'},
                            200: {'label': '200'}

                        },
                        included=True
                    ),

                    # Filter Hours
                    html.Span("Hour", className="control_label"),
                    html.Span(id='output_hours_2', className="filter-label"),
                    dcc.RangeSlider(
                        id='hours_slider_2',
                        min=1,
                        max=100,
                        value=[1, 100],
                        marks={
                            1: {'label': '0'},
                            5: {'label': '5'},
                            10: {'label': '10'},
                            24: {'label': '24'},
                            48: {'label': '48'},
                            72: {'label': '72'},
                            100: {'label': '100'},
                        },
                        included=True
                    ),

                    # Select color-map-feature radio button
                    html.P("Select variable as color:", className="control_label"),
                    dcc.RadioItems(
                        className="control_label",
                        id='map_size_radio_items_2',
                        options=[
                            {'label': 'Year', 'value': 'event_year'},
                            {'label': 'Severity', 'value': 'event_si'}
                        ],
                        value='event_year',
                        labelStyle={'display': 'inline-block'}
                    ), html.Div(id='output_size_button_2'),

                    # Select time intervals 
                    html.P("Select time interval:", className="control_label"),
                    dcc.RadioItems(
                        className="control_label",
                        id='interval_radio_items_2',
                        options=[
                            {'label': '1 year', 'value': 1},
                            {'label': '3 year', 'value': 3},
                            {'label': '5 years', 'value': 5},
                            {'label': '7 years', 'value': 7},
                            {'label': '10 years', 'value': 10}
                        ],
                        value=5,
                        labelStyle={'display': 'inline-block'}
                    ), html.Div(id='output_interval_button_2'),

                    # Select country
                    html.P("Country", className="control_label"),
                    dcc.Dropdown(
                        id="country_selector_2",
                        options=countries_options,
                        multi=True,
                        value=country_list,
                        className="dcc_control",
                    ),

                ],
                    className="pretty_container six columns",
                    id="cross-filter-options_2",
                    style={'display': 'none'} #'backgroundColor': 'white', 
                )

            ],
                className="row flex-display",
            ),  # END Filter single

            
            
            
            # =============================================================================
            # Plots
            # =============================================================================
            
            # DIV ROW 1
            html.Div(
                children=[
                
                    html.Div(
                        [dcc.Graph(id="count_year_graph")],
                        className="pretty_container six columns",
                        id="count_year_graph_div_1",
                        #style={'backgroundColor': 'white'}
                        
                    ),
                    
                    html.Div(
                        [dcc.Graph(id="count_year_graph_2")],
                        className="pretty_container six columns",
                        id="count_year_graph_div_2",
                        style={'display': 'none'} #'backgroundColor': 'white', 
                    )
                    
                ],
                className="row flex-display",
            ),
            
            # DIV ROW 2
            html.Div(
                children=[
                
                    html.Div(
                        [dcc.Graph(id="map")],
                        id="map_div_1",
                        className="pretty_container six columns",
                        #style={'backgroundColor': 'white'}
                    ),
                    
                    html.Div(
                        [dcc.Graph(id="map_2")],
                        id="map_div_2",
                        className="pretty_container six columns",
                        style={'display': 'none'} #'backgroundColor': 'white', 
                    )
                
                ],
                className="row flex-display",
            ),
            
            # DIV ROW 3
            html.Div(
                children=[
                
                    html.Div(
                        [dcc.Graph(id="map_events_graph")],
                        id="map_events_graph_div_1",
                        className="pretty_container six columns",
                        #style={'backgroundColor': 'white'}
                    ),
                    
                    html.Div(
                        [dcc.Graph(id="map_events_graph_2")],
                        id="map_events_graph_div_2",
                        className="pretty_container six columns",
                        style={'display': 'none'} #'backgroundColor': 'white', 
                    )
                
                ],
                className="row flex-display",
            ),
            
            # DIV ROW 4
            html.Div(
                children=[
                
                    html.Div(
                        [dcc.Graph(id="si_pie_graph")],
                        id="si_pie_graph_div_1",
                        className="pretty_container six columns",
                        #style={'backgroundColor': 'white'}
                    ),
                    
                    html.Div(
                        [dcc.Graph(id="si_pie_graph_2")],
                        id="si_pie_graph_div_2",
                        className="pretty_container six columns",
                        style={'display': 'none'} #'backgroundColor': 'white', 
                    )
                
                ],
                className="row flex-display",
            ),
            
            # DIV ROW 5
            html.Div(
                children=[
                
                    html.Div(
                        [dcc.Graph(id="plots_boxplot")],
                        id="plots_boxplot_div_1",
                        className="pretty_container six columns",
                        #style={'backgroundColor': 'white'}
                    ),
                    
                    html.Div(
                        [dcc.Graph(id="plots_boxplot_2")],
                        id="plots_boxplot_div_2",
                        className="pretty_container six columns",
                        style={'display': 'none'} #'backgroundColor': 'white', 
                    )
                
                ],
                className="row flex-display",
            ),

            # DIV ROW 6
            html.Div(
                children=[
                
                    html.Div([
                        html.Div(
                            [
                                dcc.Dropdown(
                                    id='input_multi_graph_overTime',
                                    options=[
                                        {'label': 'Duration over time', 'value': 'event_length'},
                                        {'label': 'Severity over time', 'value': 'event_si'},
                                        {'label': 'Area over time', 'value': 'event_area'},
                                        {'label': 'Precipitation over time', 'value': 'event_pre'}
                                    ],
                                    value='event_length',
                                    searchable=False
                                )
                            ],
                        ),

                        html.Div(
                            [dcc.Graph(id="multi_graph")],
                        ),
                        
                        ],
                        id="input_multi_graph_overTime_div_1",
                        className="pretty_container six columns",
                        #style={'backgroundColor': 'white'}
                    ),
                    
                    html.Div([
                        html.Div(
                            [
                                dcc.Dropdown(
                                    id='input_multi_graph_overTime_2',
                                    options=[
                                        {'label': 'Duration over time', 'value': 'event_length'},
                                        {'label': 'Severity over time', 'value': 'event_si'},
                                        {'label': 'Area over time', 'value': 'event_area'},
                                        {'label': 'Precipitation over time', 'value': 'event_pre'}
                                    ],
                                    value='event_length',
                                    searchable=False
                                )
                            ],
                        ),

                        html.Div(
                            [dcc.Graph(id="multi_graph_2")],
                        ),
                        
                        ],
                        id="input_multi_graph_overTime_div_2",
                        className="pretty_container six columns",
                        style={'display': 'none'} #'backgroundColor': 'white', 
                    )
                    
                ],
                className="row flex-display",
            ),

            # DIV ROW 7
            html.Div(
                children=[
            
                    html.Div(
                        [
                            dcc.Dropdown(
                                id='input_multi_graph_events',
                                options=[
                                    {'label': 'Events average per Month', 'value': 'events_per_month'},
                                    {'label': 'Events average per Year', 'value': 'events_per_year'}
                                ],
                                value='events_per_month',
                                searchable=False
                            ),
                            html.Div(
                                [dcc.Graph(id="output_multi_graph_events")],
                                className="twelve columns",
                                #style={'backgroundColor': 'white'}
                            ),
                        ],
                        id="multi_graph_events_div_1",
                        className="pretty_container six columns",
                        #style={'backgroundColor': 'white'}
                    ),
                    
                    html.Div(
                        [
                            dcc.Dropdown(
                                id='input_multi_graph_events_2',
                                options=[
                                    {'label': 'Events average per Month', 'value': 'events_per_month'},
                                    {'label': 'Events average per Year', 'value': 'events_per_year'}
                                ],
                                value='events_per_month',
                                searchable=False
                            ),
                            html.Div(
                                [dcc.Graph(id="output_multi_graph_events_2")],
                                className="twelve columns",
                                #style={'backgroundColor': 'white'}
                            ),
                        ],
                        id="multi_graph_events_div_2",
                        className="pretty_container six columns",
                        style={'display': 'none'} #'backgroundColor': 'white', 
                    )

                ],
                className="row flex-display",
            )

        ]),

    # =============================================================================
    # START CONTAINER COMPARE
    # =============================================================================

    

    # Close Header
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

def plot_pie(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list):
    layout_pie = copy.deepcopy(layout)
    si_range = [0, 300]
    tmp = filter_events(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list)
    tmp = tmp.drop_duplicates(subset='event_id', keep='first')
    tmp = tmp.groupby('label_si').event_id.count().reset_index()

    data = [
        dict(
            type="pie",
            labels=si_labels,
            values=tmp.event_id,
            hoverinfo="text+value+percent",
            textinfo="label+percent+value",
            # hole=0.5,
             marker=dict(colors=[color_set[0],color_set[1],color_set[2],color_set[4]]),
        ),
    ]
    layout_pie["title"] = "Severity of Events: {} to {}".format(
        year_range[0], year_range[1]
    )
    #layout_pie["font"] = dict(color="#777777")
    layout_pie["legend"] = dict(
        font=dict(size="12"), orientation="h"
    )
    #layout_pie["plot_bgcolor"] = '#FFFFFF'
    #layout_pie["paper_bgcolor"] = '#FFFFFF'


    figure = dict(data=data, layout=layout_pie)
    return figure





layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    #plot_bgcolor="#F9F9F9",
    #paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    #title="Satellite Overview",
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








# =============================================================================
# Einzel/Vergleichanalyse Switcher
# =============================================================================
@app.callback(
    [
        Output('cross-filter-options', 'className'), Output('cross-filter-options_2', 'style'),
        Output('count_year_graph_div_1', 'className'), Output('count_year_graph_div_2', 'style'),
        Output('map_div_1', 'className'), Output('map_div_2', 'style'),
        Output('map_events_graph_div_1', 'className'), Output('map_events_graph_div_2', 'style'),
        Output('si_pie_graph_div_1', 'className'), Output('si_pie_graph_div_2', 'style'),
        Output('plots_boxplot_div_1', 'className'), Output('plots_boxplot_div_2', 'style'),
        Output('input_multi_graph_overTime_div_1', 'className'), Output('input_multi_graph_overTime_div_2', 'style'),
        Output('multi_graph_events_div_1', 'className'), Output('multi_graph_events_div_2', 'style'),
    ],
    [Input('my-input', 'value')])
def show_rules(my_input):
    if my_input:
        # rule for Verlgleichsanalyse
        return [
                    "pretty_container six columns", {'display': 'block'},#, 'backgroundColor': 'white'},
                    "pretty_container six columns", {'display': 'block'},#, 'backgroundColor': 'white'},
                    "pretty_container six columns", {'display': 'block'},#, 'backgroundColor': 'white'},
                    "pretty_container six columns", {'display': 'block'},#, 'backgroundColor': 'white'},
                    "pretty_container six columns", {'display': 'block'},#, 'backgroundColor': 'white'},
                    "pretty_container six columns", {'display': 'block'},#, 'backgroundColor': 'white'},
                    "pretty_container six columns", {'display': 'block'},#, 'backgroundColor': 'white'},
                    "pretty_container six columns", {'display': 'block'},#, 'backgroundColor': 'white'},
                ]
    
    # rule for Einzelanalyse
    return [
                "pretty_container twelve columns", {'display': 'none'},
                "pretty_container twelve columns", {'display': 'none'},
                "pretty_container twelve columns", {'display': 'none'},
                "pretty_container twelve columns", {'display': 'none'},
                "pretty_container twelve columns", {'display': 'none'},
                "pretty_container twelve columns", {'display': 'none'},
                "pretty_container twelve columns", {'display': 'none'},
                "pretty_container twelve columns", {'display': 'none'},
            ]











# =============================================================================
# Events average per Year
# =============================================================================
def getFigure_events_per_year(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list, interval_radio_items):
    return data_builder.get_events_per_year(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list, False, interval_radio_items)


@app.callback(
    Output(component_id='count_year_graph', component_property='figure'),
    [Input("year_slider", "value"),
     Input("month_slider", "value"),
     Input("si_slider", "value"),
     Input("area_slider", "value"),
     Input("map_size_radio_items", "value"),
     Input("hours_slider", "value"),
     Input("country_selector", "value"),
     Input("interval_radio_items", "value")])
def plot_events_per_year(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range,
                         country_list, interval_radio_items):
    return getFigure_events_per_year(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list, interval_radio_items)


@app.callback(
    Output(component_id='count_year_graph_2', component_property='figure'),
    [Input("year_slider_2", "value"),
     Input("month_slider_2", "value"),
     Input("si_slider_2", "value"),
     Input("area_slider_2", "value"),
     Input("map_size_radio_items_2", "value"),
     Input("hours_slider_2", "value"),
     Input("country_selector_2", "value"),
     Input("interval_radio_items_2", "value")])
def plot_events_per_year_2(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range,
                         country_list, interval_radio_items):
    return getFigure_events_per_year(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list, interval_radio_items)






# =============================================================================
# Map
# =============================================================================
def getFigure_scatter_mapbox(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list):
    tmp = filter_events(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list)

    # plot map
    # https://plotly.com/python/reference/scattermapbox/
    px.set_mapbox_access_token(mapbox_token)
    fig = px.scatter_mapbox(tmp,
                            lat="lat", lon="lon",
                            color=map_size_radio_items,
                            text='event_id',
                            size="area", size_max=20,
                            zoom=3,
                            color_continuous_scale=px.colors.sequential.Purp)

    fig.update_traces(mode='markers', selector=dict(type='scattermapbox'))
    fig.update_layout(
        autosize=True,
        margin=dict(l=0, r=0, b=0, t=0),
        legend=dict(font=dict(size=10), orientation="h"),
        mapbox=dict(style="light")
    )

    return fig

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
    return getFigure_scatter_mapbox(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list)


@app.callback(
    Output(component_id='map_2', component_property='figure'),
    [Input("year_slider_2", "value"),
     Input("month_slider_2", "value"),
     Input("si_slider_2", "value"),
     Input("area_slider_2", "value"),
     Input("map_size_radio_items_2", "value"),
     Input("hours_slider_2", "value"),
     Input("country_selector_2", "value")])
def plot_scatter_mapbox_2(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list):
    return getFigure_scatter_mapbox(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list)




# =============================================================================
# Event from Map
# =============================================================================
def getFigure_map_events_graph(map_events_graph):
    layout_individual = copy.deepcopy(layout)

    try:
        event_id = int(map_events_graph['points'][0]['text'])
    except:
        event_id = 201706413

    tmp = df[df['event_id'] == event_id]

    data = [
        dict(
            type="scatter",
            mode="lines+markers",
            name="Area",
            x=tmp.date,
            y=tmp.area * 10,
            line=dict(shape="spline", smoothing=2, color=color_set[1]),
            marker=dict(symbol="circle"),
        ),
        dict(
            type="scatter",
            mode="lines+markers",
            name="Max Precipitation",
            x=tmp.date,
            y=tmp.maxPrec,
            line=dict(shape="spline", smoothing=2, color=color_set[0]),
            marker=dict(symbol="circle"),
        ),
    ]
    layout_individual["title"] = str('Event ' + str(event_id) + ' (map hover)')
    #layout_individual["plot_bgcolor"] = '#FFFFFF'
    #layout_individual["paper_bgcolor"] = '#FFFFFF'
    layout_individual["legend"] = dict(font=dict(size="12"), orientation="h")
    
    figure = dict(data=data, layout=layout_individual)
    return figure

@app.callback(Output("map_events_graph", "figure"), [Input("map", "hoverData")])
def plot_map_events_graph(map_events_graph):
    return getFigure_map_events_graph(map_events_graph)


@app.callback(Output("map_events_graph_2", "figure"), [Input("map_2", "hoverData")])
def plot_map_events_graph_2(map_events_graph):
    return getFigure_map_events_graph(map_events_graph)



# =============================================================================
# Severety of events
# =============================================================================
def getFigure_pie_graph(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list):
    figure = plot_pie(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list)
    return figure


@app.callback(
    Output(component_id='si_pie_graph', component_property='figure'),
    [Input("year_slider", "value"),
     Input("month_slider", "value"),
     Input("si_slider", "value"),
     Input("area_slider", "value"),
     Input("map_size_radio_items", "value"),
     Input("hours_slider", "value"),
     Input("country_selector", "value")])
def plot_pie_graph(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list):
    return getFigure_pie_graph(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list)


@app.callback(
    Output(component_id='si_pie_graph_2', component_property='figure'),
    [Input("year_slider_2", "value"),
     Input("month_slider_2", "value"),
     Input("si_slider_2", "value"),
     Input("area_slider_2", "value"),
     Input("map_size_radio_items_2", "value"),
     Input("hours_slider_2", "value"),
     Input("country_selector_2", "value")])
def plot_pie_graph_2(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list):
    return getFigure_pie_graph(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list)



# =============================================================================
# Box plots
# =============================================================================
def getFigure_boxplots(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list):
    tmp = filter_events(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list)

    # TODO CODE
    # Histogram with all outliers combined as e.g. >30 hours

    # return figure

    # from sklearn.preprocessing import MinMaxScaler
    # import plotly.graph_objects as go

    # scaler = MinMaxScaler()
    # min_max_scaler = MinMaxScaler()
    # scaled = tmp.copy()
    # scaled[['event_si', 'event_area', 'event_pre', 'event_length']] = min_max_scaler.fit_transform(
    #     scaled[['event_si', 'event_area', 'event_pre', 'event_length']])  # event_area instead of area used!

    # scaled['event_si'] = scaled['event_si'].round(decimals=3)
    # scaled['event_area'] = scaled['event_area'].round(decimals=3)
    # scaled['event_pre'] = scaled['event_pre'].round(decimals=3)
    # scaled['event_length'] = scaled['event_length'].round(decimals=3)

    # fig = go.Figure()
    # fig.add_trace(go.Box(y=scaled.event_si, name="Severity"))
    # fig.add_trace(go.Box(y=scaled.event_area, name="Area"))
    # fig.add_trace(go.Box(y=scaled.event_pre, name="Precipitation"))
    # fig.add_trace(go.Box(y=scaled.event_length, name="Duration"))
    
    fig = make_subplots(rows=1,cols=4)
    fig.append_trace(go.Box(y=tmp.event_si, name="Severity",marker=dict(color=color_set[0])),row=1,col=1)
    fig.append_trace(go.Box(y=tmp.event_area, name="Area",marker=dict(color=color_set[1])),row=1,col=2)
    fig.append_trace(go.Box(y=tmp.event_pre, name="Precipitation",marker=dict(color=color_set[2])),row=1,col=3)
    fig.append_trace(go.Box(y=tmp.event_length, name="Duration",marker=dict(color=color_set[3])),row=1,col=4)
    fig.update_layout(title="Dispertion of Attributes",legend=dict(orientation="h"))
    return fig


@app.callback(
    Output(component_id='plots_boxplot', component_property='figure'),
    [Input("year_slider", "value"),
     Input("month_slider", "value"),
     Input("si_slider", "value"),
     Input("area_slider", "value"),
     Input("map_size_radio_items", "value"),
     Input("hours_slider", "value"),
     Input("country_selector", "value")])
def plot_boxplots(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list):
    return getFigure_boxplots(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list)


@app.callback(
    Output(component_id='plots_boxplot_2', component_property='figure'),
    [Input("year_slider_2", "value"),
     Input("month_slider_2", "value"),
     Input("si_slider_2", "value"),
     Input("area_slider_2", "value"),
     Input("map_size_radio_items_2", "value"),
     Input("hours_slider_2", "value"),
     Input("country_selector_2", "value")])
def plot_boxplots_2(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list):
    return getFigure_boxplots(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list)




# =============================================================================
# ... over time
# =============================================================================
def getFigure_duration(current_figure, year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list, interval_radio_items):
    if current_figure == "event_length":
        return data_builder.get_duration_per_year(year_range, month_range, si_range, area_range,
                                                  map_size_radio_items, hours_range, country_list, interval_radio_items)

    if current_figure == "event_si":
        return data_builder.get_severity_per_year(year_range, month_range, si_range, area_range, map_size_radio_items,
                                                  hours_range, country_list, interval_radio_items)

    if current_figure == "event_area":
        return data_builder.get_area_per_year(year_range, month_range, si_range, area_range, map_size_radio_items,
                                              hours_range, country_list, interval_radio_items)

    if current_figure == "event_pre":
        return data_builder.get_precipitation_per_year(year_range, month_range, si_range, area_range,
                                                       map_size_radio_items, hours_range, country_list,
                                                       interval_radio_items)

    return None


@app.callback(
    Output(component_id='multi_graph', component_property='figure'),
    [Input("input_multi_graph_overTime", "value"),
     Input("year_slider", "value"),
     Input("month_slider", "value"),
     Input("si_slider", "value"),
     Input("area_slider", "value"),
     Input("map_size_radio_items", "value"),
     Input("hours_slider", "value"),
     Input("country_selector", "value"),
     Input("interval_radio_items", "value")])
def plot_duration(current_figure, year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list, interval_radio_items):
    return getFigure_duration(current_figure, year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list, interval_radio_items)


@app.callback(
    Output(component_id='multi_graph_2', component_property='figure'),
    [Input("input_multi_graph_overTime_2", "value"),
     Input("year_slider_2", "value"),
     Input("month_slider_2", "value"),
     Input("si_slider_2", "value"),
     Input("area_slider_2", "value"),
     Input("map_size_radio_items_2", "value"),
     Input("hours_slider_2", "value"),
     Input("country_selector_2", "value"),
     Input("interval_radio_items_2", "value")])
def plot_duration_2(current_figure, year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list, interval_radio_items):
    return getFigure_duration(current_figure, year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list, interval_radio_items)




# =============================================================================
# Events per Month/Year
# =============================================================================
def getFigure_events_per_year_or_month(current_figure, year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list, interval_radio_items):
    if current_figure == "events_per_month":
        return data_builder.get_events_per_month(year_range, month_range, si_range, area_range, map_size_radio_items,
                                                 hours_range, country_list)

    if current_figure == "events_per_year":
        return data_builder.get_events_per_year(year_range, month_range, si_range, area_range, map_size_radio_items,
                                                hours_range, country_list, True, interval_radio_items)

    return None


@app.callback(
    Output(component_id='output_multi_graph_events', component_property='figure'),
    [Input("input_multi_graph_events", "value"),
     Input("year_slider", "value"),
     Input("month_slider", "value"),
     Input("si_slider", "value"),
     Input("area_slider", "value"),
     Input("map_size_radio_items", "value"),
     Input("hours_slider", "value"),
     Input("country_selector", "value"),
     Input("interval_radio_items", "value")])
def plot_events_per_year_or_month(current_figure, year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list, interval_radio_items):
    return getFigure_events_per_year_or_month(current_figure, year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list, interval_radio_items)


@app.callback(
    Output(component_id='output_multi_graph_events_2', component_property='figure'),
    [Input("input_multi_graph_events_2", "value"),
     Input("year_slider_2", "value"),
     Input("month_slider_2", "value"),
     Input("si_slider_2", "value"),
     Input("area_slider_2", "value"),
     Input("map_size_radio_items_2", "value"),
     Input("hours_slider_2", "value"),
     Input("country_selector_2", "value"),
     Input("interval_radio_items_2", "value")])
def plot_events_per_year_or_month_2(current_figure, year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list, interval_radio_items):
    return getFigure_events_per_year_or_month(current_figure, year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list, interval_radio_items)






###################################################################################################################################################

df.columns.names

# =============================================================================
# Main
# =============================================================================


if __name__ == "__main__":
    app.run_server(debug=False, host='0.0.0.0', port=8050)
