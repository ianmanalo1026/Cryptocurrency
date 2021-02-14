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


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

try:
    engine = create_engine('postgresql+psycopg2://postgres:soulgun21@127.0.0.1:5432/Cryptocurrency')
    connection = engine.connect()
    print("Connected to Successful!")
except RuntimeError:
    print('error')



app.layout = html.Div([
    dcc.Graph(id='live-graph', animate=True),
    dcc.Interval(
        id='graph-update',
        interval=1000,    
        n_intervals=0
    )
])

@app.callback(Output('live-graph', 'figure'),
              Input('graph-update', 'n_intervals'))
def update_graph(n):
    df = pd.read_sql("select * from \"cryptocurrency\"", connection)
    fig = px.line(df, x="time", y="bitcoin_php")
    
    
    return fig
    


if __name__ == '__main__':
    app.run_server(debug=True)