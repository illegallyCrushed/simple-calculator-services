import os
from nameko.extensions import DependencyProvider
import mysql.connector
from mysql.connector import Error
import mysql.connector.pooling


class DatabaseWrapper:

    connection = None

    def __init__(self, connection):
        self.connection = connection

    def get_request_data(self, request_id):
        cursor = self.connection.cursor(dictionary=True)
        result = []
        sql = f"""SELECT * FROM requests WHERE id = "{request_id}" """
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        return result


class DatabaseProvider(DependencyProvider):

    connection_pool = None

    def setup(self):
        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="result_pool",
                pool_size=32,
                pool_reset_session=True,
                host=os.environ.get('DB_HOST', 'localhost'),
                port=os.environ.get('DB_PORT', 3306),
                database=os.environ.get('DB_NAME'),
                user=os.environ.get('DB_USER', 'root'),
                password=os.environ.get('DB_PASS', '')
            )
        except Error as e:
            print("Error while connecting to MySQL using Connection pool ", e)

    def get_dependency(self, worker_ctx):
        return DatabaseWrapper(self.connection_pool.get_connection())
