import psycopg2
from pycoingecko import CoinGeckoAPI
import schedule
from datetime import datetime
from time import mktime
import time

import json
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output



"""Crytocurrency fetcher"""
class CrytocurriesFetcher:
    
    def __init__(self):
        self.cg = CoinGeckoAPI()
        self.bitcoin = None
        self.ethereum = None
        self.ripple = None
    
    def get_coin(self):
        self.bitcoin = self.cg.get_price(ids=['bitcoin'], vs_currencies=["php"])
        self.ethereum = self.cg.get_price(ids=['ethereum'], vs_currencies=["php"])
        self.ripple = self.cg.get_price(ids=['ripple'], vs_currencies=["php"])
    
    
class TimeControl(CrytocurriesFetcher):
    
    def __init__(self):
        super().__init__()
        self.date_database = None
        self.time_database = None
    
    def datetime_database(self):
        date = datetime.now()
        self.time_database = date.strftime("%H:%M:%S")
        self.date_database = date.strftime("%Y-%m-%d")

        
class DataBase(TimeControl):
    
    def __init__(self):
        super().__init__()
        self.con = psycopg2.connect(
                                    database="Cryptocurrency",
                                    user="postgres",
                                    password='soulgun21',
                                    host='127.0.0.1',
                                    port='5432'
                                    )
        self.cur = self.con.cursor()
        self.database_unx = None
        self.database_btc = None
        # self.database_eth = None
        # self.database_xrp = None
        
    def create_table(self):
        self.cur.execute("CREATE TABLE Cryptocurrency (id SERIAL PRIMARY KEY, Date Date,Time Time, Bitcoin_PHP INT);")
        self.cur.close()
        self.con.commit()
        self.con.close()
        print("Succesfully created a table")
    
    def store_data(self):
        self.get_coin()
        self.datetime_database()
        self.cur.execute("INSERT INTO Cryptocurrency (Date, Time, Bitcoin_PHP) VALUES(%s, %s, %s);", (self.date_database, self.time_database, self.bitcoin['bitcoin']['php']))
        self.con.commit()
        print("Database has been updated!")
        
    def last_row(self):
        self.cur.execute("SELECT id, Date, Time, Bitcoin_PHP FROM Cryptocurrency WHERE id=(select max(id) from Cryptocurrency)")
        rows = self.cur.fetchall()
        for row in rows:
            self.database_unx = row[2]
            self.database_btc = row[3]
            # self.database_eth = row[4]
            # self.database_xrp = row[5]
            

"""Dash Script for visualization"""    

   

try:
    engine = create_engine('postgresql+psycopg2://postgres:soulgun21@127.0.0.1:5432/Cryptocurrency')
    connection = engine.connect()
    print("Connected to Successful!")
except RuntimeError:
    print('error')
    
df = pd.read_sql('select * from "cryptocurrency"', connection); 

fig = px.line(df, x="bitcoin_php", y="time", title="Bitcoin Line Chart", height=325)

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id="graph", figure=fig),
    html.Pre(
        id='structure',
        style={
            'border': 'thin lightgrey solid', 
            'overflowY': 'scroll',
            'height': '275px'
        }
    )
])

@app.callback(
    Output("structure", "children"), 
    [Input("graph", "figure")])
def display_structure(fig_json):
    return json.dumps(fig_json, indent=2)
            
            
            
            
            
            

        
if __name__ == "__main__":
    
    c = CrytocurriesFetcher()
    t = TimeControl()
    db = DataBase()
    

    def main():
        c.get_coin()
        t.datetime_database()
        db.last_row()
        # db.create_table()
        # db.store_data()
        print(f"{db.database_btc} {c.bitcoin['bitcoin']['php']}")
        if (db.database_btc != c.bitcoin['bitcoin']['php']): 
            db.store_data()
        app.run_server(debug=True)
        
                
        
        # print(f"{t.date_time_database} {t.unix_time} Bitcoin ₱{c.bitcoin['bitcoin']['php']}")
        # print(f"{t.date_time_database} {t.unix_time} Ethereum ₱{c.ethereum['ethereum']['php']}")
        # print(f"{t.date_time_database} {t.unix_time} Ripple ₱{c.ripple['ripple']['php']}")
    
    schedule.every(5).seconds.do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)