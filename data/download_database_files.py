import pandas as pd
import os
import dotenv

'''
This file may be useful in case the data sources for the PostgreSQL tables need to change
and the tables need to be replaced with new data.

It is currently not in use (2022-02-02)
'''

dotenv.load_dotenv()

download_paths = {
    "electricityProduction_TABLE.csv": os.environ('ELECTRICITY_PRODUCTION_TABLE_URL'),
    "gwr_TABLE.csv": os.environ('GWR_TABLE_URL'),
    "heatingInfo_TABLE.csv": os.environ('HEATING_INFO_TABLE_URL')
}

for key, url in download_paths.items():
    print("Downloading '%s'..." %key)
    df = pd.read_csv(url, index_col=0)
    print("Saving '%s'..." %key)
    # print(df.head())
    df.to_csv("./data/" + key)