from sqlalchemy.sql import select
from sqlalchemy import create_engine

import dash
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input

import plotly
import plotly.express as px
import plotly.graph_objs as go

from collections import deque


MAX_POINTS_TO_SHOW = 15

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Graph(id='live-graph',),
    dcc.Interval(
        id='graph-update',
        interval=1*5000,    
        n_intervals=0,
    )]
    ,title='custom tick labels', 
    style = {'display': 'inline-block', 'width': '48%'}
    )

@app.callback(Output('live-graph', 'figure'),
              Input('graph-update', 'n_intervals'))
def update_graph(n):
    engine = create_engine('postgresql+psycopg2://postgres:soulgun21@127.0.0.1:5432/Cryptocurrency')
    with engine.connect() as conn:
        df = pd.read_sql("select * from \"cryptocurrency\"", conn)
        # fig = go.Figure(data=go.Scatter(x=df["time"], y=df["bitcoin_php"], mode="lines+markers", name="lines+markers"))
        time = list(deque(df["time"],maxlen=20))
        php = list(deque(df["bitcoin_php"],maxlen=20))
        data = go.Scatter(x = time, y=php, name="Scatter", mode="lines+markers")
    
    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(time),max(time)]),
                                                yaxis=dict(range=[min(php),max(php)]),)}

if __name__ == '__main__':
    app.run_server(debug=True)