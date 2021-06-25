import dash
from flask_caching import Cache

app = dash.Dash(__name__)
# Neeeded for callbacks using dynamically generated ui components
app.config.suppress_callback_exceptions = True
# configure cache
"""cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory',
    'CACHE_THRESHOLD': '100'
}) """

CACHE_TIMEOUT_S = 120
# relative path for dataset directory
DATASETS_PATH = './datasets/'
