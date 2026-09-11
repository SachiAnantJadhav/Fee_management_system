import os
import mssql_python


def get_connection():
    connection_string = os.environ["SQL_CONNECTION_STRING"]
    return mssql_python.connect(connection_string)