import pandas as pd
import sqlalchemy
import dotenv
import os

'''
This file is meant to be run when the PostgreSQL instance for the API is instantiated.

.csv files which are to be loaded into the database are downloaded from URLs and
PostgreSQL tables are generated from them.
'''


dotenv.load_dotenv()


host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
username = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
database = os.getenv("DATABASE")

DATABASE_URL_SQLALCHEMY = "postgresql://" + username +":" + password + "@" + host + ":" + port + "/" + database



# engine = sqlalchemy.create_engine(DATABASE_URL_SQLALCHEMY, execution_options=dict(stream_results=True))
engine = sqlalchemy.create_engine(DATABASE_URL_SQLALCHEMY)



download_paths = {
    "electricityProduction_TABLE.csv": os.getenv('ELECTRICITY_PRODUCTION_TABLE_URL'),
    "gwr_TABLE.csv": os.getenv('GWR_TABLE_URL'),
    "heatingInfo_TABLE.csv": os.getenv('HEATING_INFO_TABLE_URL')
}

filenames = {"electricityProduction_TABLE.csv":"electricity_production", "gwr_TABLE.csv":"gwr", "heatingInfo_TABLE.csv":"heating_info"}
# filenames = {"heatingInfo_TABLE.csv":"heating_info"}


for filename, table_name in filenames.items():

    # check whether database exists already:
    if sqlalchemy.inspect(engine).has_table(table_name) == True:
        print("Table %s already exists and is therefore skipped." %table_name)
        continue

    print("Downloading '%s'..." %filename)
    chunks = pd.read_csv(download_paths[filename], index_col=0, chunksize=10000)
    print("Writing to table %s..." %table_name)
    counter = 0
    for df in chunks:
        try:
            df.to_sql(table_name, engine, if_exists="fail", chunksize=5000)
            print("Writing chunk %s" %counter)
            counter += 1

        except ValueError as e:
            if str(e) == "Table '%s' already exists." %table_name and counter==0:

                # on own server/ local machine
                while True:
                    answer = input("Table '%s' already exists. Do wou want to overwrite it (o) or skip it (s)?" %table_name)
                    if answer=="o" or answer=="O":
                        print("Writing chunk %s" %counter)
                        df.to_sql(table_name, engine, if_exists="replace")
                        counter += 1
                        break
                    elif answer=="s" or answer=="S":
                        break
                    else:
                        continue
                pass

            elif str(e) == "Table '%s' already exists." %table_name and counter>0:
                # append:
                print("Writing chunk %s" %counter)
                df.to_sql(table_name, engine, if_exists="append")
                counter += 1

            else:
                raise e

print("(Re-)Filling database complete.")