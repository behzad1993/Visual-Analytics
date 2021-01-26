# Duration

# %%
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd

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
# TODO: dont read for every plot
def filter_events(year_range, month_range, si_range, area_range, hours_range, country_list):
    filtered_df = df[df["country"].isin(country_list)]
    filtered_df = filtered_df[
        (filtered_df['event_year'] >= year_range[0]) & (filtered_df['event_year'] <= year_range[1])]
    filtered_df = filtered_df[
        (filtered_df['event_month'] >= month_range[0]) & (filtered_df['event_month'] <= month_range[1])]
    filtered_df = filtered_df[(filtered_df['event_si'] >= si_range[0]) & (filtered_df['event_si'] <= si_range[1])]
    filtered_df = filtered_df[
        (filtered_df['event_area'] >= area_range[0]) & (filtered_df['event_area'] <= area_range[1])]
    filtered_df = filtered_df[
        (filtered_df['event_length'] >= hours_range[0]) & (filtered_df['event_length'] <= hours_range[1])]
    return filtered_df


def add_year_cluster(cluster_range, filtered_df):
    filtered_df['year_cluster'] = filtered_df.event_year - filtered_df.event_year % cluster_range
    return filtered_df


def get_duration_in_hours(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range,
                          country_list):
    filtered_df = filter_events(year_range, month_range, si_range, area_range, hours_range, country_list)

    avg_duration = filtered_df.groupby(['event_year'])['event_length'].mean()
    avg_duration = pd.DataFrame(avg_duration)
    avg_duration['event_year'] = avg_duration.index
    avg_duration.reset_index(drop=True, inplace=True)

    max_duration = filtered_df.groupby(['event_year'])['event_length'].max()
    max_duration = pd.DataFrame(max_duration)
    max_duration['event_year'] = max_duration.index
    max_duration.reset_index(drop=True, inplace=True)

    filtered_df['day'] = [e.strftime('%Y-%m-%d') for e in filtered_df.event_start]

    year_mean = filtered_df.groupby(['event_year'])['event_length'].mean()
    year_mean = pd.DataFrame(year_mean)
    year_mean['date'] = year_mean.index
    year_mean.reset_index(drop=True, inplace=True)

    return plot_duration_in_hours(year_mean.date, year_mean.event_length, avg_duration.event_year,
                                  avg_duration.event_length, max_duration.event_year, max_duration.event_length,
                                  "Duration in Hours")


def plot_duration_in_hours(x, y, x_avg, y_avg, x_max, y_max, title):
    figure = make_subplots(specs=[[{"secondary_y": True}]])
    figure.add_bar(x=x, y=y, name='average per year')
    figure.add_trace(go.Scatter(x=x_max, y=y_max, name='max per year'))
    figure.update_xaxes(title_text='Time')
    figure.update_yaxes(title_text=title)
    get_layout(figure, "Time", "log")
    return figure


def get_severity_per_year(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range,
                          country_list):
    filtered_df = filter_events(year_range, month_range, si_range, area_range, hours_range, country_list)

    avg_si = filtered_df.groupby(['event_year'])['event_si'].mean()
    avg_si = pd.DataFrame(avg_si)
    avg_si['event_year'] = avg_si.index
    avg_si.reset_index(drop=True, inplace=True)

    max_si = filtered_df.groupby(['event_year'])['event_si'].max()
    max_si = pd.DataFrame(max_si)
    max_si['event_year'] = max_si.index
    max_si.reset_index(drop=True, inplace=True)

    x_avg = avg_si.event_year
    y_avg = avg_si.event_si

    x_max = max_si.event_year
    y_max = max_si.event_si

    return plot_severity_per_year(x_avg, y_avg, x_max, y_max)


def plot_severity_per_year(x_avg, y_avg, x_max, y_max):
    figure = make_subplots(specs=[[{"secondary_y": True}]])
    figure.add_bar(x=x_avg, y=y_avg, name='average per year')
    figure.add_trace(go.Scatter(x=x_max, y=y_max, name='max per year'))
    figure.update_xaxes(title_text='Time')
    figure.update_yaxes(title_text='Severity')
    get_layout(figure, "Severity Index", "log")
    return figure


def get_area_per_year(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range,
                      country_list):
    filtered_df = filter_events(year_range, month_range, si_range, area_range, hours_range, country_list)

    avg_area = filtered_df.groupby(['event_year'])['event_area'].mean()
    avg_area = pd.DataFrame(avg_area)
    avg_area['event_year'] = avg_area.index
    avg_area.reset_index(drop=True, inplace=True)

    max_area = filtered_df.groupby(['event_year'])['event_area'].max()
    max_area = pd.DataFrame(max_area)
    max_area['event_year'] = max_area.index
    max_area.reset_index(drop=True, inplace=True)

    x_avg = avg_area.event_year
    y_avg = avg_area.event_area

    x_max = max_area.event_year
    y_max = max_area.event_area

    return plot_area_per_year(x_avg, y_avg, x_max, y_max)


def plot_area_per_year(x_avg, y_avg, x_max, y_max):
    figure = make_subplots(specs=[[{"secondary_y": True}]])
    figure.add_bar(x=x_avg, y=y_avg, name='avg per year')
    figure.add_trace(go.Scatter(x=x_max, y=y_max, name='max per year'))
    figure.update_xaxes(title_text='Time')
    figure.update_yaxes(title_text='Area', secondary_y=False)
    get_layout(figure, "Area per year", "log")
    return figure


def get_precipitation_per_year(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range,
                               country_list):
    filtered_df = filter_events(year_range, month_range, si_range, area_range, hours_range, country_list)
    avg_prec = filtered_df.groupby(['event_year'])['event_pre'].mean()
    avg_prec = pd.DataFrame(avg_prec)
    avg_prec['event_year'] = avg_prec.index
    avg_prec.reset_index(drop=True, inplace=True)

    max_prec = filtered_df.groupby(['event_year'])['event_pre'].max()
    max_prec = pd.DataFrame(max_prec)
    max_prec['event_year'] = max_prec.index
    max_prec.reset_index(drop=True, inplace=True)

    x_avg = avg_prec.event_year
    y_avg = avg_prec.event_pre
    x_max = max_prec.event_year
    y_max = max_prec.event_pre

    return plot_precipitation_per_year(x_avg, y_avg, x_max, y_max)


def plot_precipitation_per_year(x_avg, y_avg, x_max, y_max):
    figure = make_subplots(specs=[[{"secondary_y": True}]])
    figure.add_bar(x=x_avg, y=y_avg, name='avg per year')
    figure.add_trace(go.Scatter(x=x_max, y=y_max, name='max per year'))
    figure.update_xaxes(title_text='Time')
    figure.update_yaxes(title_text='Precipitation', secondary_y=False)
    get_layout(figure, "Precipitation per year", "log")

    return figure


def get_events_per_year(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range,
                        country_list):
    filtered_df = filter_events(year_range, month_range, si_range, area_range, hours_range, country_list)

    events_filtered = filtered_df.drop_duplicates(subset=['event_id'], keep='first')
    events_filtered = add_year_cluster(5, events_filtered)

    events_per_year = events_filtered.groupby('event_year')['event_id'].nunique().reset_index()
    events_mean = events_per_year.event_id.mean()

    events_per_cluster = events_filtered.groupby('year_cluster')['event_id'].count()
    events_per_cluster = pd.DataFrame(events_per_cluster)
    events_per_cluster['avg_per_cluster'] = events_per_cluster.event_id / 5
    events_per_cluster.reset_index(inplace=True)

    events_per_cluster = events_per_cluster[:-1]
    events_per_cluster = events_per_cluster.drop(events_per_cluster.index[0])

    return plot_events_per_year(events_per_year, events_per_cluster, events_mean)


def plot_events_per_year(events_per_year, events_per_cluster, events_mean):
    figure = go.Figure()
    figure.add_bar(x=events_per_year.event_year, y=events_per_year.event_id, name='events per year')
    figure.add_trace(go.Scatter(x=events_per_cluster.year_cluster,
                                y=events_per_cluster.avg_per_cluster,
                                name='average per 5 years'))
    figure.add_trace(go.Scatter(x=[1979, 2017], y=[events_mean, events_mean], name='overall average'))
    figure.update_xaxes(title_text='Year')
    figure.update_yaxes(title_text='Events')
    get_layout(figure, "Events per year", "linear")
    return figure


def get_events_per_month(year_range, month_range, si_range, area_range, map_size_radio_items, hours_range,
                         country_list):
    filtered_df = filter_events(year_range, month_range, si_range, area_range, hours_range, country_list)
    events_filtered = add_year_cluster(5, filtered_df)

    events_per_month = events_filtered.groupby('event_month')['event_id'].nunique().reset_index()
    events_mean_month = events_per_month.event_id.mean()
    max_month = events_filtered.groupby(['year_cluster'])['event_si'].max()

    return plot_events_per_month(events_per_month, events_mean_month, max_month)


def plot_events_per_month(events_per_month, events_mean_month, max_month):
    figure = go.Figure()
    figure.add_bar(x=events_per_month.event_month, y=events_per_month.event_id, name='per month')
    figure.add_trace(go.Scatter(x=[1, 12], y=[events_mean_month, events_mean_month], name='overall average'))
    figure.update_xaxes(title_text='Month')
    figure.update_yaxes(title_text='Events')
    get_layout(figure, "Events per Month", "linear")
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
