# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 15:03:35 2020
@author: David
"""

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
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import data_builder
import dash_daq as daq
from bubbly.bubbly import bubbleplot

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
        html.Div(
            [html.Img(src=app.get_asset_url("rain-logo.png"), id="plotly-image",
                      style={"height": "100px", "width": "auto", "margin-bottom": "0px"})],
            className="one-third column",
        ),

        html.Div(
            [html.Div([
                html.H3("Heavy Rain Events", style={"margin-bottom": "0px"}),
                html.H5("in Central Europe", style={"margin-top": "0px"}), ])],
            className="one-half column", id="title",
        ),

        html.Div(
            [html.A(html.Button("About us", id="learn-more-button"),
                    href="https://www.hu-berlin.de/de", )],
            className="one-third column", id="button",
        ),
    ],
        id="header",
        className="row flex-display",
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
                style={'textAlign': 'right'}
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
                style={'textAlign': 'left'}
            ),

        ],
        className="row flex-display",
    ),
    
    
    
    
    
    
    
    

    # =============================================================================
    # CONTAINER SINGLE START
    # =============================================================================

    html.Div(
        id="single-container",
        children=[

            # =============================================================================
            # Filters SINGLE
            # =============================================================================

            html.Div([
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
                    ),  # html.Div(id='output_country_list'),

                ],
                    className="twelve columns",
                    id="cross-filter-options",
                    style={'backgroundColor': 'white'}
                ),

            ],
                className="pretty_container row",
                style={'backgroundColor': 'white'}
            ),  # END Filter single

            
            
            
            # =============================================================================
            # Plots
            # =============================================================================
            
            # DIV ROW 1
            html.Div([
                html.Div(
                    [dcc.Graph(id="count_year_graph")],
                    className="twelve columns",
                )],
                className="pretty_container row",
                style={'backgroundColor': 'white'}
            ),
            
            # DIV ROW 2
            html.Div([
                html.Div(
                    [dcc.Graph(id="map")],
                    className="twelve columns",
                )],
                className="pretty_container row",
                style={'backgroundColor': 'white'}
            ),
            
            # DIV ROW 3
            html.Div([
                html.Div(
                    [dcc.Graph(id="map_events_graph")],
                    className="twelve columns",
                )],
                className="pretty_container row",
                style={'backgroundColor': 'white'}
            ),
            
            # DIV ROW 4
            html.Div([
                html.Div(
                    [dcc.Graph(id="si_pie_graph")],
                    className="twelve columns",
                )],
                className="pretty_container row",
                style={'backgroundColor': 'white'}
            ),
            
            # DIV ROW 5
            html.Div([
                html.Div(
                    [dcc.Graph(id="plots_boxplot")],
                    className="twelve columns",
                )],
                className="pretty_container row",
                style={'backgroundColor': 'white'}
            ),

            # DIV ROW 6
            html.Div(
                [
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
                        className="twelve columns",
                        style={'backgroundColor': 'white'}
                    ),
                ],
                className="pretty_container row",
                style={'backgroundColor': 'white'}
            ),

            # DIV ROW 7
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
                        style={'backgroundColor': 'white'}
                    ),
                ],
                className="pretty_container row",
                style={'backgroundColor': 'white'}
            ),

        ]),

    # =============================================================================
    # START CONTAINER COMPARE
    # =============================================================================

    html.Div(
        id="compare-container",
        children=[

            # =============================================================================
            # Filters COMPARE
            # =============================================================================

            html.Div([
                html.Div([

                    # Filter Year
                    html.P("Year", className="control_label"),
                    html.Div(id='output_year_left', className="filter-label"),
                    dcc.RangeSlider(
                        id='year_slider_left',
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
                    ),

                    # Filter Year
                    html.P("Month", className="control_label"),
                    html.Div(id='output_month_left', className="filter-label"),
                    dcc.RangeSlider(
                        id='month_slider_left',
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
                    html.P("Severity", className="control_label"),
                    html.Div(id='output_si_left', className="filter-label"),
                    dcc.RangeSlider(
                        id='si_slider_left',
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

                    # Filter Area
                    html.P("Area", className="control_label"),
                    html.Div(id='output_area_left', className="filter-label"),
                    dcc.RangeSlider(
                        id='area_slider_left',
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
                    html.P("Hour", className="control_label"),
                    html.Div(id='output_hours_left', className="filter-label"),
                    dcc.RangeSlider(
                        id='hours_slider_left',
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

                    # Select color-map-feature radio button
                    html.P("Select variable as color:", className="control_label"),
                    dcc.RadioItems(
                        className="control_label",
                        id='map_size_radio_items_left',
                        options=[
                            {'label': 'Year', 'value': 'event_year'},
                            {'label': 'Severity', 'value': 'event_si'}
                        ],
                        value='event_year',
                        labelStyle={'display': 'inline-block'}
                    ), html.Div(id='output_size_button_left'),

                    # Select country
                    html.P("Country", className="control_label"),
                    dcc.Dropdown(
                        id="country_selector_left",
                        options=countries_options,
                        multi=True,
                        value=country_list,
                        className="dcc_control",
                    ),

                ],
                    className="pretty_container six columns",

                ),

                html.Div([
                    html.Div([
                        # Filter Year
                        html.P("Year", className="control_label"),
                        html.Div(id='output_year_right', className="filter-label"),
                        dcc.RangeSlider(
                            id='year_slider_right',
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
                        ),

                        # Filter Year
                        html.P("Month", className="control_label"),
                        html.Div(id='output_month_right', className="filter-label"),
                        dcc.RangeSlider(
                            id='month_slider_right',
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
                        html.P("Severity", className="control_label"),
                        html.Div(id='output_si_right', className="filter-label"),
                        dcc.RangeSlider(
                            id='si_slider_right',
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

                        # Filter Area
                        html.P("Area", className="control_label"),
                        html.Div(id='output_area_right', className="filter-label"),
                        dcc.RangeSlider(
                            id='area_slider_right',
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
                        html.P("Hour", className="control_label"),
                        html.Div(id='output_hours_right', className="filter-label"),
                        dcc.RangeSlider(
                            id='hours_slider_right',
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

                        # Select color-map-feature radio button
                        html.P("Select variable as color:", className="control_label"),
                        dcc.RadioItems(
                            className="control_label",
                            id='map_size_radio_items_right',
                            options=[
                                {'label': 'Year', 'value': 'event_year'},
                                {'label': 'Severity', 'value': 'event_si'}
                            ],
                            value='event_year',
                            labelStyle={'display': 'inline-block'}
                        ), html.Div(id='output_size_button_right'),

                        # Select country
                        html.P("Country", className="control_label"),
                        dcc.Dropdown(
                            id="country_selector_right",
                            options=countries_options,
                            multi=True,
                            value=country_list,
                            className="dcc_control",
                        ),

                    ],
                    )],
                    className="pretty_container six columns",

                )],
                className="row flex-display",
            ),  # END DIV ROW 1

            # =============================================================================
            # PLOTS COMPARE
            # =============================================================================
            # DIV ROW 2
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id="si_pie_graph_2")],
                        className="pretty_container six columns",
                    ),
                    html.Div(
                        [dcc.Graph(id="count_year_graph_2")],
                        className="pretty_container six columns",
                    ),

                ],
                className="row flex-display",
            ),

            # END CONTAINER COMPARE
        ]),

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








# =============================================================================
# Einzel/Vergleichanalyse Switcher
# =============================================================================
@app.callback(Output('single-container', 'style'), [Input('my-input', 'value')])
def hide_single(my_input):
    if my_input:
        return {'display': 'none'}
    return {'display': 'block'}


@app.callback(Output('compare-container', 'style'), [Input('my-input', 'value')])
def show_compare(my_input):
    if my_input:
        return {'display': 'block'}
    return {'display': 'none'}








# =============================================================================
# Events average per Year
# =============================================================================
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
    return data_builder.get_events_per_year(year_range, month_range, si_range, area_range, map_size_radio_items,
                                            hours_range, country_list, False, interval_radio_items)



# =============================================================================
# Map
# =============================================================================
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

    # plot map
    # https://plotly.com/python/reference/scattermapbox/
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
        autosize=True,
        margin=dict(l=0, r=0, b=0, t=0),
        legend=dict(font=dict(size=10), orientation="h"),
        mapbox=dict(style="light")
    )

    return fig


# =============================================================================
# Event from Map
# =============================================================================
@app.callback(Output("map_events_graph", "figure"), [Input("map", "hoverData")])
def plot_map_events_graph(map_events_graph):
    layout_individual = copy.deepcopy(layout)

    try:
        event_id = int(map_events_graph['points'][0]['text'])
    except:
        event_id = 201706413

    tmp = df[df['event_id'] == event_id]

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


# =============================================================================
# Severety of events
# =============================================================================
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
    figure = plot_pie(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list)
    return figure



# =============================================================================
# Box plots
# =============================================================================
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
    tmp = filter_events(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list)

    # TODO CODE
    # Histogram with all outliers combined as e.g. >30 hours

    # return figure

    from sklearn.preprocessing import MinMaxScaler
    import plotly.graph_objects as go

    scaler = MinMaxScaler()
    min_max_scaler = MinMaxScaler()
    scaled = tmp.copy()
    scaled[['event_si', 'event_area', 'event_pre', 'event_length']] = min_max_scaler.fit_transform(
        scaled[['event_si', 'event_area', 'event_pre', 'event_length']])  # event_area instead of area used!

    scaled['event_si'] = scaled['event_si'].round(decimals=3)
    scaled['event_area'] = scaled['event_area'].round(decimals=3)
    scaled['event_pre'] = scaled['event_pre'].round(decimals=3)
    scaled['event_length'] = scaled['event_length'].round(decimals=3)

    fig = go.Figure()
    fig.add_trace(go.Box(y=scaled.event_si, name="Severity"))
    fig.add_trace(go.Box(y=scaled.event_area, name="Area"))
    fig.add_trace(go.Box(y=scaled.event_pre, name="Precipitation"))
    fig.add_trace(go.Box(y=scaled.event_length, name="Duration"))

    return fig



# =============================================================================
# ... over time
# =============================================================================
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
def plot_duration(current_figure, year_range, month_range, si_range, area_range, map_size_radio_items, hours_range,
                  country_list, interval_radio_items):
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



# =============================================================================
# Events per Month/Year
# =============================================================================
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
def plot_events_per_year_or_month(current_figure, year_range, month_range, si_range, area_range, map_size_radio_items,
                                  hours_range, country_list, interval_radio_items):
    if current_figure == "events_per_month":
        return data_builder.get_events_per_month(year_range, month_range, si_range, area_range, map_size_radio_items,
                                                 hours_range, country_list)

    if current_figure == "events_per_year":
        return data_builder.get_events_per_year(year_range, month_range, si_range, area_range, map_size_radio_items,
                                                hours_range, country_list, True, interval_radio_items)

    return None








###################################################################################################################################################


# Help function
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
            marker=dict(colors=["#fac1b7", "#a9bb95", "#92d8d8", "#72d8d8"]),
        ),
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


df.columns.names

# =============================================================================
# Main
# =============================================================================


if __name__ == "__main__":
    app.run_server(debug=False, host='0.0.0.0', port=8050)
