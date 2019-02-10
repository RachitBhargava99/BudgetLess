import os


class Config:
    SECRET_KEY = '0917b13a9091915d54b6336f45909539cce452b3661b21f386418a257883b30a'
    ENDPOINT_ROUTE = ''
    CURRENT_URL = 'https://finbuddy.thinger.appspot.com/'
    PROJECT_ID = 'thinger'
    DATA_BACKEND = 'cloudsql'
    CLOUDSQL_USER = 'root'
    CLOUDSQL_PASSWORD = ''
    CLOUDSQL_DATABASE = 'fb_sql'
    CLOUDSQL_CONNECTION_NAME = 'thinger:us-east1:finbuddy'
    SQLALCHEMY_DATABASE_URI = (
        'mysql+pymysql://{user}:{password}@localhost/{database}?unix_socket=/cloudsql/{connection_name}').format(
        user=CLOUDSQL_USER, password=CLOUDSQL_PASSWORD, database=CLOUDSQL_DATABASE,
        connection_name=CLOUDSQL_CONNECTION_NAME)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
