import os
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from app import DATASETS_PATH


# Serve page layout
def serve_layout():
    return html.Div(id='root', children=[
        dcc.Store(id='session', storage_type='local'),

                html.Div(id='header', children=[
                html.H1("GDAT - Global Data Analysis Tool")]
            ),
            html.Div(id='csstest', children=[
            html.Span(id='main-span', children=[
                html.Div(id='sidebar', children=[
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select File to upload')
                        ]),
                        # Do NOT Allow SIMULTANEOUS uploads by the user
                        multiple=False
                    ),
                    # List all .csv  files hosted on the server
                    html.Div(id='file-list',
                        children=[dcc.Dropdown(id='files', options=[
                            {'label': filename,'value': filename} for filename in
                            sorted(os.listdir(DATASETS_PATH))],
                            placeholder="Select Dataset"),
                        ]),
                    html.Button('Populate menu', id='show-dashboard-opts'),
                    html.Div(id='dashboard-creation-area')
                ]),
                html.Div(id='body', children=[
                    html.Div(id='choropleth-output-area'),
                ]),
                ]),
                html.Div(id='stats-container', children=[
                html.Div(id='stats'),
                html.Div(id='covar-corr')]),
                html.Div(id='graph-creation-area'),
                html.Div(id='download-area'),
                html.Div(id='footer'),
                html.Iframe(id='video1', src="https://www.youtube.com/embed/InRh52wdsQk")
    ]),
])



