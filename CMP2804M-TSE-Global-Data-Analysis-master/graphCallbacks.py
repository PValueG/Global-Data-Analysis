import os
import re
import plotly.graph_objects as go
import pandas as pd
import dash_table as dt
import dash_html_components as html
import dash_core_components as dcc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from pandas.api.types import is_string_dtype, is_numeric_dtype
from app import app, DATASETS_PATH
from graphs import *
from stats import *
from validator import Validator

# Callback to create the choropleth from user dataset
@app.callback(Output('choropleth-output-area', 'children'),
    [Input('create-dashboard', 'n_clicks')],
    [State('x-variable-dropdown', 'value'), State('countries', 'value'),
    State('files', 'value'), State('colour-dropdown', 'value'),
    State('normalization-radio', 'value'), State('transformation-radio', 'value')])
def create_choropleth(n_clicks,
                    x_variable,
                    countries,
                    filename,
                    colour_scheme,
                    normalization,
                    transformation):
    if n_clicks is None:
        raise PreventUpdate

    df = pd.read_csv(os.path.join(DATASETS_PATH, filename))

    if x_variable is None:
        return html.H4("Error: No X variable selected for analysis with dropdown.")
    # can't create choropleth if no location info selected by user
    if countries is None:
        return html.H4("Error: Unable to create choropleth, no country location information provided")

    # Edge case checking
    if not is_numeric_dtype(df[x_variable]):
        return html.H4("Error: Can not create choropleth from non-quantative variable.")

    if not is_string_dtype(df[countries]):
        return html.H4("Error: Locations for plotting must be a string type.")

    # normalize & transform if applicable
    if normalization != 'None':
        df = normalize(df, normalization)
    if transformation != 'None':
        df = power_transform(df)
    # validate locations
    validator = Validator([df])
    df = validator.validate()


    fig = choropleth(df, x_variable, countries, colour_scheme)
    return [
        dcc.Graph(id='user-choropleth', figure=fig),
    ]


@app.callback(Output('graph-creation-area', 'children'),
    [Input('create-dashboard', 'n_clicks')],
    [State('files', 'value'), State('x-variable-dropdown', 'value'),
    State('y-variable-dropdown', 'value'), State('normalization-radio', 'value'),
    State('transformation-radio', 'value')])
def populate_graph_menu(n_clicks,
                        filename,
                        x_variable,
                        y_variable,
                        normalization,
                        transformation):
    if n_clicks is None:
        raise PreventUpdate

    df = pd.read_csv(os.path.join(DATASETS_PATH, filename))
    if normalization != 'None':
        df = normalize(df, normalization)
    if transformation != 'None':
        df = power_transform(df)


    # Default/starting graph - overlaid histogram if two variables selected
    if x_variable is not None and is_numeric_dtype(df[x_variable]) and y_variable is None:
        fig = histogram(df, x_variable, 'None')
    elif x_variable is not None and is_numeric_dtype(df[x_variable]) and y_variable is not None and is_numeric_dtype(df[y_variable]):
        fig = overlaid_histogram(df, x_variable, y_variable)
    else:
        return html.H4("Error: Can not create graph from none quantatative variable(s)")

    # Merge both lists if two variables selected
    if y_variable is not None:
        GRAPH_TYPES = UNIVARIATE_GRAPHS + BIVARIATE_GRAPHS
    else:
        GRAPH_TYPES = UNIVARIATE_GRAPHS

    return [
        dcc.Dropdown(id='graph-type',
                options=[{'label': graph_type, 'value': graph_type}
                            for graph_type in GRAPH_TYPES],
                placeholder='Select graph type'),
        html.Button('Graph selection', id='graph-selection'),
        html.Div(id='graph-output-area', children=[
            dcc.Graph(id='user-graph', figure=fig)
            ]
        )
    ]


@app.callback(Output('graph-output-area', 'children'),
    [Input('graph-selection', 'n_clicks')],
    [State('graph-type', 'value')])
def graph_type_options(n_clicks, graph_type):
    if n_clicks is None:
        raise PreventUpdate

    if graph_type == 'Histogram':
        return [
            dcc.Checklist(id='histogram-margplot',
            options=[
                {'label': 'Margin Rug plot', 'value': 'Rug'},
            ],
            value='Rug'
            ),
            html.Button('Create Histogram', id='create-histogram'),
            dcc.Graph(id='user-histogram')
        ]
    elif graph_type == 'Overlaid Histogram':
        return [
            html.Button('Create Overlaid Histogram', id='create-overlaid-histogram'),
            dcc.Graph(id='user-overlaid-histogram')
        ]
    elif graph_type == 'Scatter Plot':
        return [
            dcc.RadioItems(id='regression-radio',
                options=[
                    {'label': 'None', 'value': 'None'},
                    {'label': 'OLS Linear Regression', 'value': 'ols'},
                    {'label': 'LOWESS Regression', 'value': 'lowess'},
                ],
                value='None'
            ),
            dcc.RadioItems(id='scatter-colour-radio',
                options=[
                    {'label': 'Use default colours', 'value': 'None'},
                    {'label': 'Use choropleth/map colourscale', 'value': 'Choropleth'},
                ],
                value='Choropleth'
            ),
            html.Button('Create Scatter Plot', id='create-scatter-plot'),
            dcc.Graph(id='user-scatter-plot')
        ]
    elif graph_type == 'Box Plot':
         return [
            html.Button('Create Box Plot', id='create-box-plot'),
            dcc.Graph(id='user-box-plot')
        ]
    elif graph_type == 'Contour Plot':
        return [
            html.Button('Create Contour Plot', id='create-contour-plot'),
            dcc.Graph(id='user-contour-plot')
        ]
    elif graph_type == 'Heat Map':
        return [
            dcc.RadioItems(id='heatmap-colour-radio',
                options=[
                    {'label': 'Use default colours', 'value': 'None'},
                    {'label': 'Use choropleth/map colourscale', 'value': 'Choropleth'},
                ],
                value='Choropleth'
            ),
            html.Button('Create Heat Map', id='create-heat-map'),
            dcc.Graph(id='user-heat-map')
        ]


@app.callback(Output('user-histogram', 'figure'),
    [Input('create-histogram', 'n_clicks')],
    [State('x-variable-dropdown', 'value'), State('files', 'value'),
    State('normalization-radio', 'value'), State('transformation-radio', 'value'),
    State('histogram-margplot', 'value')])
def create_histogram(n_clicks,
                x_variable,
                filename,
                normalization,
                transformation,
                margplot):
    if n_clicks is None:
        raise PreventUpdate

    df = pd.read_csv(os.path.join(DATASETS_PATH, filename))
    if normalization != 'None':
        df = normalize(df, normalization)
    if transformation != 'None':
        df = power_transform(df)

    fig = histogram(df, x_variable, margplot)
    return fig


@app.callback(Output('user-overlaid-histogram', 'figure'),
    [Input('create-overlaid-histogram', 'n_clicks')],
    [State('x-variable-dropdown', 'value'), State('y-variable-dropdown', 'value'),
    State('files', 'value'),State('normalization-radio', 'value'),
    State('transformation-radio', 'value')])
def create_overlaid_histogram(n_clicks,
                x_variable,
                y_variable,
                filename,
                normalization,
                transformation):
    if n_clicks is None:
        raise PreventUpdate

    df = pd.read_csv(os.path.join(DATASETS_PATH, filename))
    if normalization != 'None':
        df = normalize(df, normalization)
    if transformation != 'None':
        df = power_transform(df)

    fig = overlaid_histogram(df, x_variable, y_variable)
    return fig


@app.callback(Output('user-scatter-plot', 'figure'),
    [Input('create-scatter-plot', 'n_clicks')],
    [State('x-variable-dropdown', 'value'), State('y-variable-dropdown', 'value'),
    State('files', 'value'), State('countries', 'value'),
    State('normalization-radio', 'value'), State('regression-radio', 'value'),
    State('transformation-radio', 'value'), State('scatter-colour-radio', 'value'),
    State('colour-dropdown', 'value')])
def create_scatter_plot(n_clicks,
                x_variable,
                y_variable,
                filename,
                countries,
                normalization,
                regression,
                transformation,
                colour_choice,
                colour):
    if n_clicks is None:
        raise PreventUpdate

    df = pd.read_csv(os.path.join(DATASETS_PATH, filename))
    validator = Validator([df])
    df = validator.validate()

    if normalization != 'None':
        df = normalize(df, normalization)
    if transformation != 'None':
        df = power_transform(df)

    if colour_choice == 'None':
        fig = scatter_plot(df, x_variable, y_variable, countries, regression, colour_choice)
    else:
        fig = scatter_plot(df, x_variable, y_variable, countries, regression, colour)
    return fig


@app.callback(Output('user-box-plot', 'figure'),
    [Input('create-box-plot', 'n_clicks')],
    [State('x-variable-dropdown', 'value'), State('files', 'value'),
    State('normalization-radio', 'value'), State('transformation-radio', 'value')])
def create_box_plot(n_clicks,
                x_variable,
                filename,
                normalization,
                transformation):
    if n_clicks is None:
        raise PreventUpdate

    df = pd.read_csv(os.path.join(DATASETS_PATH, filename))
    if normalization != 'None':
        df = normalize(df, normalization)
    if transformation != 'None':
        df = power_transform(df)

    fig = box_plot(df, x_variable)
    return fig


@app.callback(Output('user-contour-plot', 'figure'),
    [Input('create-contour-plot', 'n_clicks')],
    [State('x-variable-dropdown', 'value'), State('y-variable-dropdown', 'value'),
    State('files', 'value'),State('normalization-radio', 'value'),
    State('transformation-radio', 'value')])
def create_contour_plot(n_clicks,
                x_variable,
                y_variable,
                filename,
                normalization,
                transformation):
    if n_clicks is None:
        raise PreventUpdate

    df = pd.read_csv(os.path.join(DATASETS_PATH, filename))
    if normalization != 'None':
        df = normalize(df, normalization)
    if transformation != 'None':
        df = power_transform(df)

    fig = contour_plot(df, x_variable, y_variable)
    return fig


@app.callback(Output('user-heat-map', 'figure'),
    [Input('create-heat-map', 'n_clicks')],
    [State('x-variable-dropdown', 'value'), State('y-variable-dropdown', 'value'),
    State('files', 'value'), State('normalization-radio', 'value'),
    State('transformation-radio', 'value'), State('heatmap-colour-radio', 'value'),
    State('colour-dropdown', 'value')])
def create_heat_map(n_clicks,
                x_variable,
                y_variable,
                filename,
                normalization,
                transformation,
                colour_choice,
                colour):
    if n_clicks is None:
        raise PreventUpdate

    df = pd.read_csv(os.path.join(DATASETS_PATH, filename))
    if normalization != 'None':
        df = normalize(df, normalization)
    if transformation != 'None':
        df = power_transform(df)

    if colour_choice == 'None':
        fig = heat_map(df, x_variable, y_variable, 'None')
    else:
        fig = heat_map(df, x_variable, y_variable, colour)
    return fig
