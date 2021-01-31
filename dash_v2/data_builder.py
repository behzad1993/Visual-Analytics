# Duration

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

df: pd.DataFrame
cluster_range = 5


def get_duration_per_year(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range,
                          country_list):
    filtered_df = filter_events(year_range, month_range, si_range, area_range, hours_range, country_list)

    event_property = 'event_length'
    plot1, plot2, plot3 = build_plots(event_property, filtered_df)

    return plot_property_per_time_scale(plot1, plot2, plot3, 'Year', 'Duration', 'Duration over time', 'log')


def get_severity_per_year(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range,
                          country_list):
    filtered_df = filter_events(year_range, month_range, si_range, area_range, hours_range, country_list)

    event_property = 'event_si'
    plot1, plot2, plot3 = build_plots(event_property, filtered_df)

    return plot_property_per_time_scale(plot1, plot2, plot3, 'Year', 'Severity', 'Severity over time', 'log')


def get_area_per_year(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range,
                      country_list):
    filtered_df = filter_events(year_range, month_range, si_range, area_range, hours_range, country_list)

    event_property = 'event_area'
    plot1, plot2, plot3 = build_plots(event_property, filtered_df)

    return plot_property_per_time_scale(plot1, plot2, plot3, 'Year', 'Area', 'Area over time', 'log')


def get_precipitation_per_year(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range,
                               country_list):
    filtered_df = filter_events(year_range, month_range, si_range, area_range, hours_range, country_list)

    event_property = 'event_pre'
    plot1, plot2, plot3 = build_plots(event_property, filtered_df)

    return plot_property_per_time_scale(plot1, plot2, plot3, 'Year', 'Precipitation', 'Precipitation over time', 'log')


def get_events_per_year(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range,
                        country_list):
    filtered_df = filter_events(year_range, month_range, si_range, area_range, hours_range, country_list)

    events_filtered = filtered_df.drop_duplicates(subset=['event_id'], keep='first')
    events_filtered = add_year_cluster(cluster_range, events_filtered)

    year_min = events_filtered.event_year.min()
    year_max = events_filtered.event_year.max()
    year_range = [year_min, year_max]

    events_per_year = events_filtered.groupby('event_year')['event_id'].nunique().reset_index()
    events_mean = events_per_year.event_id.mean()

    events_per_cluster = events_filtered.groupby('year_cluster')['event_id'].count()
    events_per_cluster = pd.DataFrame(events_per_cluster)
    events_per_cluster['avg_per_cluster'] = events_per_cluster.event_id / cluster_range
    events_per_cluster.reset_index(inplace=True)

    df_avg = pd.DataFrame(index=np.arange(year_max-year_min+1), columns=['avg'])
    df_avg.index = df_avg.index + year_min
    df_avg['avg'] = events_mean

    plot1 = Plot(events_per_year.event_year, events_per_year.event_id, 'Per year')
    plot2 = Plot(df_avg.index, df_avg.avg, 'Overall average')
    plot3 = Plot(events_per_cluster.year_cluster, events_per_cluster.avg_per_cluster, 'avg per cluster')

    return plot_property_per_time_scale(plot1, plot2, plot3, 'Month', 'Events', 'Events average per Year', 'linear')


def get_events_per_month(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range,
                         country_list):
    events_filtered = filter_events(year_range, month_range, si_range, area_range, hours_range, country_list)

    events_per_month = events_filtered.groupby('event_month')['event_id'].nunique().reset_index()
    avg = events_per_month.event_id.mean()

    plot1 = Plot(events_per_month.event_month, events_per_month.event_id, 'Per month')

    df_avg = pd.DataFrame(index=np.arange(13), columns=['avg'])
    df_avg = df_avg.drop(df_avg.index[0])
    df_avg['avg'] = avg

    plot2 = Plot(df_avg.index, df_avg.avg, 'Overall average')
    plot3 = None

    return plot_property_per_time_scale(plot1, plot2, plot3, 'Month', 'Events', 'Events average per Month', 'linear')


def init_data():
    global df
    df = pd.read_pickle("../dash_v1/event_filtered.pickle")
    # mean precipitation as extra column
    tmp = df.groupby(['event_id']).meanPre.mean()
    tmp = pd.DataFrame(tmp).reset_index()
    tmp = tmp.rename(columns={'event_id': 'event_id', 'meanPre': 'event_pre'})
    df = pd.merge(tmp, df, on='event_id', how='right')

    # exrtacting day from start date and capturing as extra column
    df['day'] = [e.strftime('%Y-%m-%d') for e in df.event_start]

    df = df[
        ['event_id', 'event_start', 'event_area', 'event_length', 'event_si', 'event_pre', 'event_year', 'event_month',
         'day', 'country']]


# read once at initialization of webserver and on every change
def filter_events(year_range, month_range, si_range, area_range, hours_range, country_list):
    filtered_data = df[df["country"].isin(country_list)]
    filtered_data = filtered_data[
        (filtered_data['event_year'] >= year_range[0]) & (filtered_data['event_year'] <= year_range[1])]
    filtered_data = filtered_data[
        (filtered_data['event_month'] >= month_range[0]) & (filtered_data['event_month'] <= month_range[1])]
    filtered_data = filtered_data[
        (filtered_data['event_si'] >= si_range[0]) & (filtered_data['event_si'] <= si_range[1])]
    filtered_data = filtered_data[
        (filtered_data['event_area'] >= area_range[0]) & (filtered_data['event_area'] <= area_range[1])]
    filtered_data = filtered_data[
        (filtered_data['event_length'] >= hours_range[0]) & (filtered_data['event_length'] <= hours_range[1])]
    return filtered_data


def add_year_cluster(cluster_size, filtered_df):
    events_filtered = filtered_df.sort_values(by=['event_year'])
    events_filtered = events_filtered.reset_index(drop=True)
    year = events_filtered['event_year'].min()
    j = year + round(cluster_size / 2)
    k = 0

    df_length = len(events_filtered.index)
    for i in range(df_length):
        events_filtered.at[i, 'year_cluster'] = j
        tmp = events_filtered['event_year'].values[i]
        if year < tmp:
            k = k + 1
            year = tmp
        if k == cluster_size:
            k = 0
            j = j + cluster_size

    return events_filtered


def build_plots(event_property, filtered_df):
    avg_area = get_avg(filtered_df, event_property)
    max_area = get_max(filtered_df, event_property)
    cluster_area = get_cluster(filtered_df, event_property)

    plot1 = Plot(avg_area.event_year, avg_area[event_property], 'Average')
    plot2 = Plot(max_area.event_year, max_area[event_property], 'Max')
    plot3 = Plot(cluster_area.year_cluster, cluster_area.avg_per_cluster, 'avg per cluster')

    return plot1, plot2, plot3


def get_max(filtered_df, event_property):
    max_ = filtered_df.groupby(['event_year'])[event_property].max()
    max_ = pd.DataFrame(max_)
    max_['event_year'] = max_.index
    max_.reset_index(drop=True, inplace=True)
    return max_


def get_avg(filtered_df, event_property):
    avg = filtered_df.groupby(['event_year'])[event_property].mean()
    avg = pd.DataFrame(avg)
    avg['event_year'] = avg.index
    avg.reset_index(drop=True, inplace=True)
    return avg


def get_cluster(filtered_df, event_property):
    events_filtered = add_year_cluster(cluster_range, filtered_df)
    events_per_cluster = events_filtered.groupby('year_cluster')['event_id'].count()
    events_per_cluster = pd.DataFrame(events_per_cluster)

    avg_per_cluster = events_filtered.groupby('year_cluster')[event_property].sum()
    avg_per_cluster = pd.DataFrame(avg_per_cluster)
    avg_per_cluster['avg_per_cluster'] = avg_per_cluster[event_property] / events_per_cluster.event_id
    avg_per_cluster.reset_index(inplace=True)
    return avg_per_cluster


def plot_property_per_time_scale(plot1, plot2, plot3, x_title, y_title, table_title, scale):
    figure = make_subplots(specs=[[{"secondary_y": True}]])
    figure.add_bar(x=plot1.x, y=plot1.y, name=plot1.name)
    figure.add_trace(go.Scatter(x=plot2.x, y=plot2.y, name=plot2.name, mode='lines'))

    if plot3 is not None:
        figure.add_trace(go.Scatter(x=plot3.x, y=plot3.y, name=plot3.name, marker_color='rgba(94, 222, 113, 1)'))

    figure.update_xaxes(title_text=x_title)
    figure.update_yaxes(title_text=y_title)
    get_layout(figure, table_title, scale)
    return figure


def get_layout(figure, title, scale):
    figure.update_layout(
        title_text=title,
        yaxis_type=scale,
        hovermode="x",
        hoverdistance=100,  # Distance to show hover label of data point
        spikedistance=1000,  # Distance to show spike
        xaxis=dict(
            showspikes=True,  # Show spike line for X-axis
            spikethickness=2,
            spikedash="dot",
            spikecolor="#999999",
            spikemode="across",
        ),
    )


def get_se_linear(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range, country_list):
    events = filter_events(year_range, month_range, si_range, area_range, hours_range, country_list)
    avg_si = events.groupby(['event_year'])['event_si'].mean()
    avg_si = pd.DataFrame(avg_si)
    avg_si['event_year'] = avg_si.index
    avg_si.reset_index(drop=True, inplace=True)

    max_si = events.groupby(['event_year'])['event_si'].max()
    max_si = pd.DataFrame(max_si)
    max_si['event_year'] = max_si.index
    max_si.reset_index(drop=True, inplace=True)

    events_mean = events.groupby(['day'])['event_si'].mean()
    events_mean = pd.DataFrame(events_mean)

    events_mean['day'] = events_mean.index
    events_mean.reset_index(drop=True, inplace=True)

    x_avg = avg_si.event_year
    y_avg = avg_si.event_si

    x_max = max_si.event_year
    y_max = max_si.event_si

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(x=x_avg, y=y_avg, name='average per year')
    fig.add_trace(go.Scatter(x=x_max, y=y_max, name='max per year'), secondary_y=True, )
    fig.update_layout(title_text="Severity Index")
    fig.update_xaxes(title_text='Time')
    fig.update_yaxes(title_text='Average severity', secondary_y=False)
    fig.update_yaxes(title_text='Max severity', secondary_y=True)

    return fig


init_data()


class Plot:
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name