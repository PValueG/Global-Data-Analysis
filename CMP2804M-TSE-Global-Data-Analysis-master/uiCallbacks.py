import os
import pandas as pd
import dash_html_components as html
import dash_core_components as dcc
import dash_table as dt
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from pandas.api.types import is_numeric_dtype
from app import app, DATASETS_PATH
from helpers import parse_file_to_df
from graphs import *
from six.moves.urllib.parse import quote
from stats import *
from pathlib import Path
from validator import Validator


@app.callback(Output('file-list', 'children'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')])
def update_file_storage(contents, filename):
    if contents is None:
        raise PreventUpdate
    else:
        try:
            df = parse_file_to_df(contents, filename)
        except Exception:
            return html.H4("Error: Incompatible filetype. Please upload a .csv file.")
        validator = Validator([df])
        validator.validate()

        my_file = Path(os.path.join(DATASETS_PATH, filename))
        if not my_file.is_file():
            df.to_csv(my_file)
            return [
                dcc.Dropdown(id='files',
                             options=[{'label': filename, 'value': filename}
                                      for filename in sorted(os.listdir(DATASETS_PATH))],
                             placeholder='Select dataset')
            ]
        else:
            return [
                html.H1("Error: File already exists on disk. Please change filename."),
                dcc.Dropdown(id='files',
                             options=[{'label': filename, 'value': filename}
                                      for filename in sorted(os.listdir(DATASETS_PATH))],
                             placeholder='Select dataset')
            ]


@app.callback(Output('dashboard-creation-area', 'children'),
    [Input('show-dashboard-opts', 'n_clicks')],
    [State('files', 'value')])
def populate_dashboard_menu(n_clicks, filename):
    if n_clicks is None:
        raise PreventUpdate

    df = pd.read_csv(os.path.join(DATASETS_PATH, filename))

    if 'Country Code' in df.columns:
        country_dropdown_text = 'Country Code'
    elif 'Country Names' in df.columns:
        country_dropdown_text = 'Country Names'
    else:
        country_dropdown_text = 'Select Country Names/Code column'
    return [
        dcc.Dropdown(id='x-variable-dropdown', options=[{'label': i, 'value': i}
                                                        for i in sorted(df.columns)],
                            placeholder='Select x variable'),
        dcc.Dropdown(id='y-variable-dropdown', options=[{'label': i, 'value': i}
                                                        for i in sorted(df.columns)],
                            placeholder='Select y variable (optional)'),

        dcc.RadioItems(id='normalization-radio',
            options=[
                {'label': 'No Normalization', 'value': 'None'},
                {'label': 'Min-Max Normalization', 'value': 'Min-Max'},
                {'label': 'Z-Score Normalization', 'value': 'Z-Score'}
            ],
            value='None'
        ),

        dcc.RadioItems(id='transformation-radio',
            options=[
                {'label': 'Do not power transform Non-Gaussian variables', 'value': 'None'},
                {'label': 'Power transform Non-Gaussian variables', 'value': 'Transform'},
            ],
            value='Transform'
        ),
        # Dropdown for indicating where country information is located in df
        dcc.Dropdown(id='countries', options=[{'label': i, 'value': i}
                                                for i in sorted(df.columns)],
                        value=country_dropdown_text),

        # Select colourscheme from list
        dcc.Dropdown(id='colour-dropdown',
                        options=[{'label': colourscheme, 'value': colourscheme}
                                 for colourscheme in sorted(CONTINUOUS_COLOUR_SCALES)],
                        placeholder='Select custom colour scheme for graphs (optional)'),
        # create dashboard
        html.Button('Create Graphs/Analyze selected variables', id='create-dashboard')
    ]


@app.callback(Output('stats', 'children'),
    [Input('create-dashboard', 'n_clicks')],
    [State('x-variable-dropdown', 'value'), State('y-variable-dropdown', 'value'),
    State('files', 'value'), State('normalization-radio','value'),
    State('transformation-radio', 'value')])
def update_summary_stats(n_clicks,
                        x_variable,
                        y_variable,
                        filename,
                        normalization,
                        transformation):
    if n_clicks is None:
        raise PreventUpdate

    df = pd.read_csv(os.path.join(DATASETS_PATH, filename))
    # Apply normalization if selected (Min-Max or Z-Score)
    if normalization != 'None':
        df = normalize(df, normalization)
    if transformation != 'None':
        df = power_transform(df)
        transform_indicator_str = " power transformed to Gaussian distribution,"
    else:
        transform_indicator_str = ""


    if x_variable is not None and is_numeric_dtype(df[x_variable]) and y_variable is not None and is_numeric_dtype(df[y_variable]):
        return [
            html.Ul(id='stats-list', children=[
                html.H6("Summary statistics for" + transform_indicator_str + " X variable: {}".format(x_variable)),
                html.Li("Minimum: {:0.2f}".format(df[x_variable].min())),
                html.Li("Maximum: {:0.2f}".format(df[x_variable].max())),
                html.Li("Mean: {:0.2f}".format(df[x_variable].mean())),
                html.Li("Median: {:0.2f}".format(df[x_variable].median())),
                html.Li("Skewness: {:0.2f}".format(df[x_variable].skew())),
                html.Li("Kurtosis: {:0.2f}".format(df[x_variable].kurtosis())),
                html.Li("Standard Deviation: {:0.2f}".format(df[x_variable].std())),
                html.Li("Variance: {:0.2f}".format(df[x_variable].var())),
                html.Li("Q1: {:0.2f}".format(df[x_variable].quantile(0.25))),
                html.Li("Q3: {:0.2f}".format(df[x_variable].quantile(0.75))),
                html.Li("IQR: {:0.2f}".format(df[x_variable].quantile(0.75) - df[x_variable].quantile(0.25))),

                html.H6("Summary statistics for" + transform_indicator_str + " Y variable: {}".format(y_variable)),
                html.Li("Minimum: {:0.2f}".format(df[y_variable].min())),
                html.Li("Maximum: {:0.2f}".format(df[y_variable].max())),
                html.Li("Mean: {:0.2f}".format(df[y_variable].mean())),
                html.Li("Median: {:0.2f}".format(df[y_variable].median())),
                html.Li("Skewness: {:0.2f}".format(df[y_variable].skew())),
                html.Li("Kurtosis: {:0.2f}".format(df[y_variable].kurtosis())),
                html.Li("Standard Deviation: {:0.2f}".format(df[y_variable].std())),
                html.Li("Variance: {:0.2f}".format(df[y_variable].var())),
                html.Li("Q1: {:0.2f}".format(df[y_variable].quantile(0.25))),
                html.Li("Q3: {:0.2f}".format(df[y_variable].quantile(0.75))),
                html.Li("IQR: {:0.2f}".format(df[y_variable].quantile(0.75) - df[y_variable].quantile(0.25)))]
            )
        ]
    elif x_variable is not None and is_numeric_dtype(df[x_variable]):
        return [
            html.Ul(id='stats-list', children=[
                html.H6("Summary statistics for" + transform_indicator_str + " X variable: {}".format(x_variable)),
                html.Li("Minimum: {:0.2f}".format(df[x_variable].min())),
                html.Li("Maximum: {:0.2f}".format(df[x_variable].max())),
                html.Li("Mean: {:0.2f}".format(df[x_variable].mean())),
                html.Li("Median: {:0.2f}".format(df[x_variable].median())),
                html.Li("Skewness: {:0.2f}".format(df[x_variable].skew())),
                html.Li("Kurtosis: {:0.2f}".format(df[x_variable].kurtosis())),
                html.Li("Standard Deviation: {:0.2f}".format(df[x_variable].std())),
                html.Li("Variance: {:0.2f}".format(df[x_variable].var())),
                html.Li("Q1: {:0.2f}".format(df[x_variable].quantile(0.25))),
                html.Li("Q3: {:0.2f}".format(df[x_variable].quantile(0.75))),
                html.Li("IQR: {:0.2f}".format(df[x_variable].quantile(0.75) - df[x_variable].quantile(0.25)))]
            )
        ]
    else:
        return html.H4("Error: None quantatative variable(s) selected for analysis with dropdowns")


@app.callback(Output('covar-corr', 'children'),
    [Input('create-dashboard', 'n_clicks')],
    [State('x-variable-dropdown', 'value'), State('y-variable-dropdown', 'value'),
    State('files', 'value'), State('normalization-radio','value'),
    State('transformation-radio', 'value'), State('countries', 'value'),
    State('colour-dropdown', 'value')])
def update_covariance_correlation(n_clicks,
                        x_variable,
                        y_variable,
                        filename,
                        normalization,
                        transformation,
                        countries,
                        colour):
    if n_clicks is None or y_variable is None:
        raise PreventUpdate

    df = pd.read_csv(os.path.join(DATASETS_PATH, filename))
    validator = Validator([df])
    df = validator.validate()

    if normalization != 'None':
        df = normalize(df, normalization)
    if transformation != 'None':
        df = power_transform(df)

    fig = scatter_plot(df, x_variable, y_variable, countries, 'None', colour)

    if x_variable is not None and is_numeric_dtype(df[x_variable]) and y_variable is not None and is_numeric_dtype(df[y_variable]):
        return [
            html.Ul(id='covar-corr-list', children=[
                html.H6("Correlation coefficients & Covariance for: {} and {}".format(x_variable, y_variable)),
                html.Li("Pearson's correlation coefficient: {:0.2f}".format(df[x_variable].corr(df[y_variable], method='pearson'))),
                html.Li("Spearman's correlation coefficient: {:0.2f}".format(df[x_variable].corr(df[y_variable], method='spearman'))),
                html.Li("Kendall's correlation coefficient: {:0.2f}".format(df[x_variable].corr(df[y_variable], method='kendall'))),
                html.Li("Pairwise covariance: {:0.2f}".format(df[x_variable].cov(df[y_variable])))
            ]),
            dcc.Graph(id='corr-scatter-plot', figure = fig)
        ]
    else:
        return html.H4("Error: Non quantatative variable(s) selected for analysis with dropdowns")


@app.callback(Output('header', 'children'),
    [Input('show-dashboard-opts', 'n_clicks')],
    [State('files', 'value')])
def update_header(n_clicks, filename):
    if n_clicks is None:
        raise PreventUpdate
    return [
        html.H1("GDAT - Global Data Analysis Tool"),
        html.Button('Preview {} download'.format(filename), id='preview-download-btn')
    ]


@app.callback(Output('download-area', 'children'),
    [Input('preview-download-btn', 'n_clicks')],
    [State('files', 'value')])
def download_area(n_clicks, filename):
    if n_clicks is None:
        raise PreventUpdate

    df = pd.read_csv(os.path.join(DATASETS_PATH, filename))
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + quote(csv_string)

    return [
        dt.DataTable(
            id='download-preview-table',
            columns=[{'name': i, 'id': i} for i in df.columns],
            data=df.to_dict('records'),
            fixed_columns={'headers': True, 'data': 1},
            fixed_rows={ 'headers': True, 'data': 5},
            style_cell={'width': '150px'}
        ),
        html.A(
            'Download Dataset',
            id='download-link',
            download=filename,
            href=csv_string,
            target="_blank"
        )
    ]
