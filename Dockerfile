FROM python:3.10


ENV DIRPATH /usr/src/app
WORKDIR $DIRPATH


RUN apt-get upgrade

# source files
COPY ./src ./src
COPY ./data/create_sql_tables.py ./data/create_sql_tables.py
COPY ./data/download_database_files.py ./data/download_database_files.py
COPY .env ./
COPY requirements.txt ./



# Python packages
RUN pip install -r ./requirements.txt
RUN pip install pandas
RUN pip install sqlalchemy

# run with -it flag
CMD "/bin/bash"