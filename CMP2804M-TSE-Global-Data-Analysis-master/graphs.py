import plotly.graph_objects as go
import plotly_express as px
import pandas as pd

# Lists of avaliable plotly continuous colourscales etc.
CONTINUOUS_COLOUR_SCALES = px.colors.named_colorscales()


UNIVARIATE_GRAPHS = [
    'Histogram',
    'Box Plot'
]


BIVARIATE_GRAPHS = [
    'Overlaid Histogram',
    'Scatter Plot',
    'Contour Plot',
    'Heat Map'
]



def choropleth(df, x_variable, countries, colour_scheme):
    fig = go.Figure(data=go.Choropleth(
        locations=df[countries],  # Spatial coordinates
        z=df[x_variable].astype(float),  # Data to be color-coded
        locationmode='country names',  # set of locations match entries in `locations`
        colorscale=colour_scheme,
        text=df[countries],
    ))
    fig.update_layout(
        autosize=True,
        margin=go.layout.Margin(
            l=10, r=10, b=25, t=25,
            pad=2
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=x_variable,
        title_x=0.5,
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="#ffffff"
        )
    )
    return fig


# TODO finish implementation of histogram fig
def histogram(df, x_variable, margplot):
    if margplot == 'Rug':
        fig = px.histogram(df, x=x_variable, marginal='rug', hover_data=df.columns)
    else:
        fig = px.histogram(df, x=x_variable, hover_data=df.columns)

    fig.update_layout(
        autosize=True,
        margin=go.layout.Margin(
            l=10, r=10, b=25, t=25,
            pad=2
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=x_variable,
        title_x=0.5,
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="#ffffff"
        )
    )
    return fig


def overlaid_histogram(df, x1_variable, x2_variable):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=df[x1_variable], name=x1_variable))
    fig.add_trace(go.Histogram(x=df[x2_variable], name=x2_variable))

    fig.update_layout(
        xaxis_title_text='Value', # xaxis label
        yaxis_title_text='Count', # yaxis label
        autosize=True,
        margin=go.layout.Margin(
            l=10, r=10, b=25, t=25,
            pad=2
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="#ffffff"
        )
    )
    fig.update_traces(opacity=0.75)
    return fig


def scatter_plot(df, x_variable, y_variable, countries, regression, colour):
    if colour == 'None' and regression == 'None':
        fig = px.scatter(df, x=x_variable, y=y_variable, hover_name=countries, color=x_variable)
    elif colour == 'None' and regression == 'ols':
        if df[x_variable].isna().sum() != 0:
                df[x_variable] = df[x_variable].fillna(df[x_variable].mean())
        if df[y_variable].isna().sum() != 0:
                df[y_variable] = df[y_variable].fillna(df[y_variable].mean())
        fig = px.scatter(df, x=x_variable, y=y_variable, trendline="ols", hover_name=countries, color=x_variable)
    elif colour == 'None' and regression == 'lowess':
        fig = px.scatter(df, x=x_variable, y=y_variable, trendline="lowess", hover_name=countries, color=x_variable)
    elif not colour == 'None' and regression == 'None':
        fig = px.scatter(df, x=x_variable, y=y_variable, hover_name=countries,
            color_continuous_scale=colour, color=x_variable)
    elif not colour == 'None' and regression == 'ols':
        if df[x_variable].isna().sum() != 0:
                df[x_variable] = df[x_variable].fillna(df[x_variable].mean())
        if df[y_variable].isna().sum() != 0:
                df[y_variable] = df[y_variable].fillna(df[y_variable].mean())
        fig = px.scatter(df, x=x_variable, y=y_variable, trendline="ols", hover_name=countries,
            color=x_variable, color_continuous_scale=colour)
    else:
        fig = px.scatter(df, x=x_variable, y=y_variable, trendline="lowess", hover_name=countries,
            color=x_variable, color_continuous_scale=colour)

    fig.update_layout(
        autosize=True,
        margin=go.layout.Margin(
            l=10, r=10, b=25, t=25,
            pad=2
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="#ffffff"
        )
    )
    return fig


def box_plot(df, x_variable):
    fig = go.Figure()
    fig.add_trace(go.Box(y=df[x_variable], name=x_variable))

    fig.update_layout(
        autosize=True,
        margin=go.layout.Margin(
            l=10, r=10, b=25, t=25,
            pad=2
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=x_variable,
        title_x=0.5,
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="#ffffff"
        )
    )
    return fig


def contour_plot(df, x_variable, y_variable):
    fig = px.density_contour(df, x=x_variable, y=y_variable)

    fig.update_layout(
        autosize=True,
        margin=go.layout.Margin(
            l=10, r=10, b=25, t=25,
            pad=2
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="#ffffff"
        )
    )
    return fig


def heat_map(df, x_variable, y_variable, colour):
    if colour == 'None':
        fig = px.density_heatmap(df, x=x_variable, y=y_variable)
    else:
        fig = px.density_heatmap(df, x=x_variable, y=y_variable, color_continuous_scale=colour)
    fig.update_layout(
        autosize=True,
        margin=go.layout.Margin(
            l=10, r=10, b=25, t=25,
            pad=2
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="#ffffff"
        )
    )
    return fig
