import os
from nameko.extensions import DependencyProvider
import mysql.connector
from mysql.connector import Error
import mysql.connector.pooling


class DatabaseWrapper:

    connection = None

    def __init__(self, connection):
        self.connection = connection

    def create_request(self, request_type, request_username, request_input):
        cursor = self.connection.cursor(dictionary=True)
        result = []
        sql = f"""INSERT INTO requests (type, username, input) VALUES ("{request_type}", "{request_username}", "{request_input}") """
        cursor.execute(sql)
        last_id = cursor.lastrowid
        self.connection.close()
        return last_id

    def get_cached_result(self, type, request_input):
        cursor = self.connection.cursor(dictionary=True)
        result = []
        sql = f"""SELECT result FROM requests WHERE input = "{request_input}" and status = 1 and type = "{type}" """
        cursor.execute(sql)
        result = cursor.fetchone()
        self.connection.close()
        return result

    def post_result(self, request_id, result):
        cursor = self.connection.cursor(dictionary=True)
        sql = f"UPDATE requests SET result = {result}, status = 1, finish_timestamp = now() WHERE id = {request_id}"
        cursor.execute(sql)
        self.connection.close()


class DatabaseProvider(DependencyProvider):

    connection_pool = None

    def setup(self):
        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="spawner_pool",
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
