# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 21:52:05 2020

@author: Pati
"""

from csgo.parser import DemoParser
import pandas as pd
import sqlite3
import sys


def main():
    
    demofile = sys.argv[1]
    
    # Create parser object
    # Set log=True above if you want to produce a logfile for the parser
    demo_parser = DemoParser(demofile = demofile, match_id = "a")
    
    # Parse the demofile, output results to dictionary with df name as key
    data = demo_parser.parse()
    
    # create SQL databank
    conn = sqlite3.connect('TmpDB.db')
    
    for key in data.keys():
        if key != "Map":
            df = pd.DataFrame.from_dict(data[key]) 
            df.to_sql(key, con=conn)
        else:
            df = pd.DataFrame({"MapName": [data["Map"]]}) 
            df.to_sql(key, con=conn)

if __name__ == "__main__":
    main()