import psycopg2
from pycoingecko import CoinGeckoAPI
import schedule
from datetime import datetime
from time import mktime
import time


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
        self.date_time = None
        self.date_time_database = None
        self.unix_time = None
    
    def running_datetime(self):
        self.date_time = datetime.now()
        
    def datetime_database(self):
        date = datetime.now()
        self.date_time_database = date.strftime("%Y-%m-%d %H:%M:%S")

    def convert_to_unixtime(self):
        self.unix_time = mktime(self.date_time.timetuple())
        

class DataBase(TimeControl):
    
    def __init__(self):
        super().__init__()
        self.con = psycopg2.connect(
                                    database="postgres",
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
        self.cur.execute("CREATE TABLE Cryptocurrency (id SERIAL PRIMARY KEY, Time_And_Date VARCHAR, Unix_Time INT, Bitcoin_PHP INT);")
        self.cur.close()
        self.con.commit()
        self.con.close()
        print("Succesfully created a table")
    
    def store_data(self):
        self.get_coin()
        self.running_datetime()
        self.datetime_database()
        self.convert_to_unixtime()
        self.cur.execute("INSERT INTO Cryptocurrency (Time_And_Date, Unix_Time, Bitcoin_PHP) VALUES(%s, %s, %s);", (self.date_time_database, self.unix_time, self.bitcoin['bitcoin']['php']))
        self.con.commit()
        print("Database has been updated!")
        
    def last_row(self):
        self.cur.execute("SELECT id, Time_And_Date, Unix_Time, Bitcoin_PHP FROM Cryptocurrency WHERE id=(select max(id) from Cryptocurrency)")
        rows = self.cur.fetchall()
        for row in rows:
            self.database_unx = row[2]
            self.database_btc = row[3]
            # self.database_eth = row[4]
            # self.database_xrp = row[5]
        
if __name__ == "__main__":
    
    c = CrytocurriesFetcher()
    t = TimeControl()
    db = DataBase()

    def main():
        c.get_coin()
        t.running_datetime()
        t.datetime_database()
        t.convert_to_unixtime()
        db.last_row()
        # db.create_table()
        # # db.store_data()
        # print(f"{db.database_btc} {c.bitcoin['bitcoin']['php']}")
        if (db.database_btc != c.bitcoin['bitcoin']['php']): 
            db.store_data()
        
                
        
        print(f"{t.date_time_database} {t.unix_time} Bitcoin ₱{c.bitcoin['bitcoin']['php']}")
        print(f"{t.date_time_database} {t.unix_time} Ethereum ₱{c.ethereum['ethereum']['php']}")
        print(f"{t.date_time_database} {t.unix_time} Ripple ₱{c.ripple['ripple']['php']}")
    
    schedule.every(5).seconds.do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)
        
        
        
        # if (db.bitcoin == "") and (db.ethereum == "") and (db.ripple == ""):
        #     pass
        # elif ((db.bitcoin == c.bitcoin) and (db.ethereum == c.ethereum) and (db.ripple == c.ripple)): 
        #     pass
        # else:
        #     db.store_data()