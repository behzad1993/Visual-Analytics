# Duration

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

df: pd.DataFrame

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


def add_year_cluster(cluster_range, filtered_df):
    filtered_df['year_cluster'] = filtered_df.event_year - filtered_df.event_year % cluster_range
    return filtered_df


def get_duration_in_hours_per_year(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range,
                                   country_list):
    filtered_df = filter_events(year_range, month_range, si_range, area_range, hours_range, country_list)

    event_property = 'event_length'
    avg_duration = get_avg(filtered_df, event_property)
    max_duration = get_max(filtered_df, event_property)

    filtered_df['day'] = [e.strftime('%Y-%m-%d') for e in filtered_df.event_start]

    plot1 = Plot(avg_duration.event_year, avg_duration.event_length, 'Average')
    plot2 = Plot(max_duration.event_year, max_duration.event_length, 'Max')
    plot3 = None

    return plot_property_per_time_scale(plot1, plot2, plot3, 'Year', 'Duration', 'Duration over time', 'log')


def get_severity_per_year(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range,
                          country_list):
    filtered_df = filter_events(year_range, month_range, si_range, area_range, hours_range, country_list)

    event_property = 'event_si'
    avg_si = get_avg(filtered_df, event_property)
    max_si = get_max(filtered_df, event_property)

    plot1 = Plot(avg_si.event_year, avg_si.event_si, 'Average')
    plot2 = Plot(max_si.event_year, max_si.event_si, 'Max')
    plot3 = None

    return plot_property_per_time_scale(plot1, plot2, plot3, 'Year', 'Severity', 'Severity over time', 'log')


def get_area_per_year(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range,
                      country_list):
    filtered_df = filter_events(year_range, month_range, si_range, area_range, hours_range, country_list)

    event_property = 'event_area'
    avg_area = get_avg(filtered_df, event_property)
    max_area = get_max(filtered_df, event_property)

    plot1 = Plot(avg_area.event_year, avg_area.event_area, 'Average')
    plot2 = Plot(max_area.event_year, max_area.event_area, 'Max')
    plot3 = None

    return plot_property_per_time_scale(plot1, plot2, plot3, 'Year', 'Area', 'Area over time', 'log')


def get_precipitation_per_year(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range,
                               country_list):
    filtered_df = filter_events(year_range, month_range, si_range, area_range, hours_range, country_list)

    event_property = 'event_pre'
    avg_pre = get_avg(filtered_df, event_property)
    max_pre = get_max(filtered_df, event_property)

    plot1 = Plot(avg_pre.event_year, avg_pre.event_pre, 'Average')
    plot2 = Plot(max_pre.event_year, max_pre.event_pre, 'Max')
    plot3 = None

    return plot_property_per_time_scale(plot1, plot2, plot3, 'Year', 'Precipitation', 'Precipitation over time', 'log')


def get_events_per_year(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range,
                        country_list):
    filtered_df = filter_events(year_range, month_range, si_range, area_range, hours_range, country_list)

    events_filtered = filtered_df.drop_duplicates(subset=['event_id'], keep='first')
    events_filtered = add_year_cluster(5, events_filtered)

    year_min = events_filtered.event_year.min()
    year_max = events_filtered.event_year.max()
    year_range = [year_min, year_max]

    events_per_year = events_filtered.groupby('event_year')['event_id'].nunique().reset_index()
    events_mean = events_per_year.event_id.mean()

    events_per_cluster = events_filtered.groupby('year_cluster')['event_id'].count()
    events_per_cluster = pd.DataFrame(events_per_cluster)
    events_per_cluster['avg_per_cluster'] = events_per_cluster.event_id / 5
    events_per_cluster.reset_index(inplace=True)

    events_per_cluster = events_per_cluster[:-1]
    events_per_cluster = events_per_cluster.drop(events_per_cluster.index[0])

    plot1 = Plot(events_per_year.event_year, events_per_year.event_id, 'Per year')
    plot2 = Plot(year_range, [events_mean, events_mean], 'Overall year')
    plot3 = Plot(events_per_cluster.year_cluster, events_per_cluster.avg_per_cluster, 'avg per cluster')

    return plot_property_per_time_scale(plot1, plot2, plot3, 'Month', 'Events', 'Events average per Year', 'linear')


def get_events_per_month(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range,
                         country_list):
    filtered_df = filter_events(year_range, month_range, si_range, area_range, hours_range, country_list)
    events_filtered = add_year_cluster(5, filtered_df)

    events_per_month = events_filtered.groupby('event_month')['event_id'].nunique().reset_index()
    avg = events_per_month.event_id.mean()

    plot1 = Plot(events_per_month.event_month, events_per_month.event_id, 'Per month')
    plot2 = Plot([1, 12], [avg, avg], 'Overall month')
    plot3 = None

    return plot_property_per_time_scale(plot1, plot2, plot3, 'Month', 'Events', 'Events average per Month', 'linear')


def get_max(filtered_df, event_property):
    max = filtered_df.groupby(['event_year'])[event_property].max()
    max = pd.DataFrame(max)
    max['event_year'] = max.index
    max.reset_index(drop=True, inplace=True)
    return max


def get_avg(filtered_df, event_property):
    avg = filtered_df.groupby(['event_year'])[event_property].mean()
    avg = pd.DataFrame(avg)
    avg['event_year'] = avg.index
    avg.reset_index(drop=True, inplace=True)
    return avg


def plot_property_per_time_scale(plot1, plot2, plot3, x_title, y_title, table_title, scale):
    figure = make_subplots(specs=[[{"secondary_y": True}]])
    figure.add_bar(x=plot1.x, y=plot1.y, name=plot1.name)
    figure.add_trace(go.Scatter(x=plot2.x, y=plot2.y, name=plot2.name))

    if plot3 is not None:
        figure.add_trace(go.Scatter(x=plot3.x, y=plot3.y, name=plot3.name))

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


init_data()


class Plot:
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name
