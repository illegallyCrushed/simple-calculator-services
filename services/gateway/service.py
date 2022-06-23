import http
from nameko.rpc import RpcProxy
from nameko.web.handlers import http
from dependencies.session import SessionProvider, session_start
import json


class GatewayService:
    name = 'gateway_service'
    user_rpc = RpcProxy('user_service')
    spawner_rpc = RpcProxy('spawner_service')
    result_rpc = RpcProxy('result_service')
    session_provider = SessionProvider()

    # user methods

    @http('POST', '/register')
    @session_start
    def register(self, request, session, response):
        request_body = [
            ("username", str),
            ("password", str)
        ]

        response.mimetype = "application/json"
        response.status_code = 400

        try:
            data = json.loads(request.get_data().decode("utf-8"))

        except Exception as e:
            response.set_data(json.dumps(
                {
                    "action": "register",
                    "action_status": "error",
                    "message": "Bad request: invalid data"
                }
            ))
            return response

        for key in request_body:
            if key[0] not in data or data[key[0]] == "" or data[key[0]] == None:
                response.set_data(json.dumps(
                    {
                        "action": "register",
                        "action_status": "error",
                        "message": f"Bad request: missing '{key}' parameter"
                    }
                ))
                return response
            else:
                if not isinstance(data[key[0]], key[1]):
                    response.set_data(json.dumps(
                        {
                            "action": "register",
                            "action_status": "error",
                            "message": f"Bad request: '{key[0]}' parameter is not of type '{key[1]}'"
                        }
                    ))
                    return response

        response.status_code = 200

        if session["username"]:
            response.set_data(json.dumps(
                {
                    "action": "register",
                    "action_status": "success",
                    "register_status": "already_logged_in",
                    "message": "Already logged in, please logout first before registering"
                }
            ))
            return response

        if self.user_rpc.check_username_exist(data["username"]):
            response.set_data(json.dumps(
                {
                    "action": "register",
                    "action_status": "success",
                    "register_status": "username_registered",
                    "message": "Username already registered"
                }
            ))
            return response

        self.user_rpc.register_user(data["username"], data["password"])

        response.status_code = 201
        response.set_data(json.dumps(
            {
                "action": "register",
                "action_status": "success",
                "register_status": "success",
                "username": data["username"],
                "message": "Registration successful"
            }
        ))
        return response

    @http('POST', '/login')
    @session_start
    def login(self, request, session, response):
        request_body = [
            ("username", str),
            ("password", str)
        ]

        response.mimetype = "application/json"
        response.status_code = 400

        try:
            data = json.loads(request.get_data().decode("utf-8"))

        except Exception as e:
            response.set_data(json.dumps(
                {
                    "action": "login",
                    "action_status": "error",
                    "message": "Bad request: invalid data"
                }
            ))
            return response

        for key in request_body:
            if key[0] not in data or data[key[0]] == "" or data[key[0]] == None:
                response.set_data(json.dumps(
                    {
                        "action": "login",
                        "action_status": "error",
                        "message": f"Bad request: missing '{key}' parameter"
                    }
                ))
                return response
            else:
                if not isinstance(data[key[0]], key[1]):
                    response.set_data(json.dumps(
                        {
                            "action": "login",
                            "action_status": "error",
                            "message": f"Bad request: '{key[0]}' parameter is not of type '{key[1]}'"
                        }
                    ))
                    return response

        if data["username"] == None or data["username"] == "" or data["password"] == None or data["password"] == "":
            response.set_data(json.dumps(
                {
                    "action": "login",
                    "action_status": "error",
                    "message": "Bad request: username or password is empty"
                }
            ))
            return response

        response.status_code = 200

        if session["username"]:
            response.set_data(json.dumps(
                {
                    "action": "login",
                    "action_status": "success",
                    "login_status": "already_logged_in",
                    "message": "Already logged in, please logout first before logging back in"
                }
            ))
            return response

        if not self.user_rpc.check_username_exist(data["username"]):
            response.set_data(json.dumps(
                {
                    "action": "login",
                    "action_status": "success",
                    "login_status": "username_not_exist",
                    "message": "Username does not exist"
                }
            ))
            return response

        if not self.user_rpc.check_password_match(data["username"], data["password"]):
            response.set_data(json.dumps(
                {
                    "action": "login",
                    "action_status": "success",
                    "login_status": "password_not_match",
                    "message": "Password does not match"
                }
            ))
            return response

        session["username"] = data["username"]
        response.set_data(json.dumps(
            {
                "action": "login",
                "action_status": "success",
                "login_status": "success",
                "username": data["username"],
                "message": "Login successful"
            }
        ))
        return response

    @http('DELETE', '/logout')
    @session_start
    def logout(self, request, session, response):
        session.destroy()
        response.mimetype = "application/json"
        response.status_code = 200
        response.set_data(json.dumps(
            {
                "action": "logout",
                "action_status": "success",
                "message": "Logged out successfully"
            }
        ))
        return response

    # prime and prime-palindrome request

    @http('GET', '/prime/<int:index>')
    @session_start
    def get_prime(self, request, session, response, index):
        response.mimetype = "application/json"

        if not session["username"]:
            response.status_code = 401
            response.set_data(json.dumps(
                {
                    "action": "get_prime",
                    "action_status": "error",
                    "message": "Unauthorized: please login first"
                }
            ))
            return response

        response.status_code = 400

        if index <= 0:
            response.set_data(json.dumps(
                {
                    "action": "get_prime",
                    "action_status": "error",
                    "message": "Bad request: index must be greater than 0"
                }
            ))
            return response

        request_id = self.spawner_rpc.create_prime_request(session["username"], index)

        response.status_code = 200

        response.set_data(json.dumps(
            {
                "action": "get_prime",
                "action_status": "success",
                "request_id": request_id,
                "message": f"Prime calculation request created, fetch result from /result/{request_id}"
            }
        ))

        return response

    @http('GET', '/prime/palindrome/<int:index>')
    @session_start
    def get_prime_palindrome(self, request, session, response, index):
        response.mimetype = "application/json"

        if not session["username"]:
            response.status_code = 401
            response.set_data(json.dumps(
                {
                    "action": "get_prime_palindrome",
                    "action_status": "error",
                    "message": "Unauthorized: please login first"
                }
            ))
            return response

        response.status_code = 400

        if index <= 0:
            response.set_data(json.dumps(
                {
                    "action": "get_prime_palindrome",
                    "action_status": "error",
                    "message": "Bad request: index must be greater than 0"
                }
            ))
            return response

        request_id = self.spawner_rpc.create_prime_palindrome_request(session["username"], index)

        response.status_code = 200

        response.set_data(json.dumps(
            {
                "action": "get_prime_palindrome",
                "action_status": "success",
                "request_id": request_id,
                "message": f"Prime palindrome calculation request created, fetch result from /result/{request_id}"
            }
        ))

        return response

    # result method

    @http('GET', '/result/<int:request_id>')
    @session_start
    def get_result(self, request, session, response, request_id):

        response.mimetype = "application/json"

        if not session["username"]:
            response.status_code = 401
            response.set_data(json.dumps(
                {
                    "action": "get_result",
                    "action_status": "error",
                    "message": "Unauthorized: please login first"
                }
            ))
            return response

        response.status_code = 404

        request_data = self.result_rpc.get_request_data(request_id)

        if not request_data or len(request_data) == 0:
            response.set_data(json.dumps(
                {
                    "action": "get_result",
                    "action_status": "error",
                    "message": f"Request with id {request_id} does not exist"
                }
            ))
            return response

        response.status_code = 403

        if request_data["username"] != session["username"]:
            response.set_data(json.dumps(
                {
                    "action": "get_result",
                    "action_status": "error",
                    "message": f"Forbidden: request with id {request_id} does not belong to you"
                }
            ))
            return response

        response.status_code = 200

        if request_data["status"] == 0:
            response.set_data(json.dumps(
                {
                    "action": "get_result",
                    "action_status": "success",
                    "request_status": "pending",
                    "message": f"Result for request with id {request_id} is not finished yet",
                    "request_id": request_id,
                    "request_username": request_data["username"],
                    "request_type": request_data["type"],
                    "request_input": request_data["input"],
                    "request_start_time": request_data["start_timestamp"]
                }
            ))
            return response

        response.set_data(json.dumps(
            {
                "action": "get_result",
                "action_status": "success",
                "request_status": "finished",
                "message": f"Result for request with id {request_id} is finished",
                "request_id": request_id,
                "request_username": request_data["username"],
                "request_type": request_data["type"],
                "request_input": request_data["input"],
                "request_start_time": request_data["start_timestamp"],
                "request_finish_time": request_data["finish_timestamp"],
                "request_result": request_data["result"]
            }
        ))

        return response
