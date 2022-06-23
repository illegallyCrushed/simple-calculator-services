# Simple Calculator Services
### Nicholas SV - C14190034

### In the root folder
Build all docker images:
```bash
make build
```
this will build all the images required and initiate the database

Run all docker containers:
```bash
docker-compose up
```
### Celery
- Asynchronously running task in background
- Self restarting after crash (docker)

celery
```bash
celery -A tasks worker --loglevel=INFO
```
tasks.py
```python
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
```

# User Service

## Request: Register
![POST](https://badgen.net/badge/Method/POST/yellow)<span style="padding:10px">**/register**</span>

```json
{
    "username": "username",
    "password": "password"
}
```

### Responses:
#### Register - Successful
![CREATED](https://badgen.net/badge/CREATED/201/green)
```json
{
    "action": "register",
    "action_status": "success",
    "register_status": "success",
    "username": "username",
    "message": "Registration successful"
}
```
#### Register - Already Registered
![OK](https://badgen.net/badge/OK/200/green)
```json
{
    "action": "register",
    "action_status": "success",
    "register_status": "username_registered",
    "message": "Username already registered"
}
```
#### Register - Already Logged In
![OK](https://badgen.net/badge/OK/200/green)
```json
{
    "action": "register",
    "action_status": "success",
    "register_status": "already_logged_in",
    "message": "Already logged in, please logout first before registering"
}
```
#### Register - Bad Request (Incomplete)
![BAD%20REQUEST](https://badgen.net/badge/BAD%20REQUEST/400/red)
```json
{
    "action": "register",
    "action_status": "error",
    "message": "Bad request: missing '('username', <class 'str'>)' parameter"
}
```
#### Register - Bad Request (Wrong Type)
![BAD%20REQUEST](https://badgen.net/badge/BAD%20REQUEST/400/red)
```json
{
    "action": "register",
    "action_status": "error",
    "message": "Bad request: 'username' parameter is not of type '<class 'str'>'"
}
```
#### Register - Bad Request (Non JSON)
![BAD%20REQUEST](https://badgen.net/badge/BAD%20REQUEST/400/red)
```json
{
    "action": "register",
    "action_status": "error",
    "message": "Bad request: invalid data"
}
```

<br>

## Request: Login
![POST](https://badgen.net/badge/Method/POST/yellow)<span style="padding:10px">**/login**</span>

```json
{
    "username": "username",
    "password": "password"
}
```

### Responses:
#### Login - Successful
![OK](https://badgen.net/badge/OK/200/green)
```json
{
    "action": "login",
    "action_status": "success",
    "login_status": "success",
    "username": "username",
    "message": "Login successful"
}
```
#### Login - Already Logged In
![OK](https://badgen.net/badge/OK/200/green)
```json
{
    "action": "login",
    "action_status": "success",
    "login_status": "already_logged_in",
    "message": "Already logged in, please logout first before logging back in"
}
```
#### Login - Username Not Exist
![OK](https://badgen.net/badge/OK/200/green)
```json
{
    "action": "login",
    "action_status": "success",
    "login_status": "username_not_exist",
    "message": "Username does not exist"
}
```
#### Login - Wrong Password
![OK](https://badgen.net/badge/OK/200/green)
```json
{
    "action": "login",
    "action_status": "success",
    "login_status": "password_not_match",
    "message": "Password does not match"
}
```
#### Login - Bad Request (Incomplete)
![BAD%20REQUEST](https://badgen.net/badge/BAD%20REQUEST/400/red)
```json
{
    "action": "login",
    "action_status": "error",
    "message": "Bad request: missing '('password', <class 'str'>)' parameter"
}
```
#### Login - Bad Request (Wrong Type)
![BAD%20REQUEST](https://badgen.net/badge/BAD%20REQUEST/400/red)
```json
{
    "action": "login",
    "action_status": "error",
    "message": "Bad request: 'username' parameter is not of type '<class 'str'>'"
}
```
#### Login - Bad Request (Non JSON)
![BAD%20REQUEST](https://badgen.net/badge/BAD%20REQUEST/400/red)
```json
{
    "action": "login",
    "action_status": "error",
    "message": "Bad request: invalid data"
}
```

<br>

## Request: Logout
![DELETE](https://badgen.net/badge/Method/DELETE/red)<span style="padding:10px">**/logout**</span>


### Responses:
#### Logout - Successful
![OK](https://badgen.net/badge/OK/200/green)
```json
{
    "action": "logout",
    "action_status": "success",
    "message": "Logged out successfully"
}
```

<br>


# Calculation Service

## Request: Prime
![GET](https://badgen.net/badge/Method/GET/green)<span style="padding:10px">**/prime/`<string:index>`**</span>


### Responses:
#### Prime - Successful
![OK](https://badgen.net/badge/OK/200/green)
```json
{
    "action": "get_prime",
    "action_status": "success",
    "request_id": 1,
    "message": "Prime calculation request created, fetch result from /result/1"
}
```
#### Prime - Bad Request (Index Out of Range)
![BAD%20REQUEST](https://badgen.net/badge/BAD%20REQUEST/400/red)
```json
{
    "action": "get_prime",
    "action_status": "error",
    "message": "Bad request: index must be greater than 0"
}
```
#### Prime - Not Logged In
![UNAUTHORIZED](https://badgen.net/badge/UNAUTHORIZED/401/red)
```json
{
    "action": "get_prime",
    "action_status": "error",
    "message": "Unauthorized: please login first"
}
```

<br>

## Request: Prime Palindrome
![GET](https://badgen.net/badge/Method/GET/green)<span style="padding:10px">**/prime/palindrome/`<string:index>`**</span>


### Responses:
#### Prime Palindrome - Successful
![OK](https://badgen.net/badge/OK/200/green)
```json
{
    "action": "get_prime_palindrome",
    "action_status": "success",
    "request_id": 2,
    "message": "Prime palindrome calculation request created, fetch result from /result/2"
}
```
#### Prime Palindrome - Bad Request (Index Out of Range)
![BAD%20REQUEST](https://badgen.net/badge/BAD%20REQUEST/400/red)
```json
{
    "action": "get_prime_palindrome",
    "action_status": "error",
    "message": "Bad request: index must be greater than 0"
}
```
#### Prime Palindrome - Not Logged In
![UNAUTHORIZED](https://badgen.net/badge/UNAUTHORIZED/401/red)
```json
{
    "action": "get_prime_palindrome",
    "action_status": "error",
    "message": "Unauthorized: please login first"
}
```

<br>


# Result Service

## Request: Result
![GET](https://badgen.net/badge/Method/GET/green)<span style="padding:10px">**/result/`<int:result_id>`**</span>


### Responses:
#### Result - Successful (Request Finished)
![OK](https://badgen.net/badge/OK/200/green)
```json
{
    "action": "get_result",
    "action_status": "success",
    "request_status": "finished",
    "message": "Result for request with id 1 is finished",
    "request_id": 1,
    "request_username": "username",
    "request_type": "prime",
    "request_input": 10,
    "request_start_time": "2022-06-23T20:25:44",
    "request_finish_time": "2022-06-23T20:25:44",
    "request_result": 29
}
```
#### Result - Successful (Request In Progress)
![OK](https://badgen.net/badge/OK/200/green)
```json
{
    "action": "get_result",
    "action_status": "success",
    "request_status": "pending",
    "message": "Result for request with id 1 is not finished yet",
    "request_id": 1,
    "request_username": "username",
    "request_type": "prime",
    "request_input": 69420,
    "request_start_time": "2022-06-23T20:18:30"
}
```
#### Result - Not Logged In
![UNAUTHORIZED](https://badgen.net/badge/UNAUTHORIZED/401/red)
```json
{
    "action": "get_result",
    "action_status": "error",
    "message": "Unauthorized: please login first"
}
```
#### Result - Not the Requester
![FORBIDDEN](https://badgen.net/badge/FORBIDDEN/403/red)
```json
{
    "action": "get_result",
    "action_status": "error",
    "message": "Forbidden: request with id 1 does not belong to you"
}
```
#### Result - Request ID Not Exist
![BAD%20REQUEST](https://badgen.net/badge/BAD%20REQUEST/400/red)
```json
{
    "action": "get_result",
    "action_status": "error",
    "message": "Bad request: request with id 1 does not exist"
}
```

<br>


