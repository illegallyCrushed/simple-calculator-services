from celery import Celery
from celery import Task
import os
from mysql.connector import connect


rabbit_url = f'amqp://{os.environ.get("RABBIT_USER", "guest")}:{os.environ.get("RABBIT_PASSWORD", "guest")}@{os.environ.get("RABBIT_HOST", "localhost")}:{os.environ.get("RABBIT_PORT", 5672)}/'

app = Celery(
    'tasks', broker=rabbit_url, backend=rabbit_url)


def isPrime(n):
    for i in range(2, n):
        if (n % i) == 0:
            return False
    return True


def isPalindromic(n):
    return str(n) == str(n)[::-1]


def post_result(cur, request_id, value):
    sql = f"UPDATE requests SET result = {value}, status = 1, finish_timestamp = now() WHERE id = {request_id}"
    cur.execute(sql)
    cur.close()
    print(f"Posted result {request_id}")


class BaseSQLTask(Task):
    abstract = True
    _db = None

    @property
    def db(self):
        if self._db is not None:
            return self._db
        self._db = connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            port=os.environ.get('DB_PORT', 3306),
            database=os.environ.get('DB_NAME'),
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASS', '')
        )
        return self._db

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        if self._db is not None:
            self._db.close()
            self._db = None


@app.task(name='tasks.prime', base=BaseSQLTask)
def prime(request_id, n):
    self = prime
    x = []
    j = 2
    c = 0
    print(f"Calculating prime {n}")
    while c < n:
        if isPrime(j):
            x.append(j)
            c += 1
        j = j+1
    post_result(self.db.cursor(), request_id, x[n-1])


@app.task(name='tasks.prime_palindrome', base=BaseSQLTask)
def prime_palindrome(request_id, n):
    self = prime_palindrome
    x = []
    j = 2
    c = 0
    print(f"Calculating prime palindrome {n}")
    while c < n:
        if isPalindromic(j):
            if isPrime(j):
                x.append(j)
                c += 1
        j = j+1
    post_result(self.db.cursor(), request_id, x[n-1])
