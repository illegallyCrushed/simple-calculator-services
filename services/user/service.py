from nameko.rpc import rpc
from dependencies.database import DatabaseProvider
import bcrypt


class UserService:

    name = 'user_service'
    database = DatabaseProvider()

    @rpc
    def check_username_exist(self, username):
        result = self.database.get_user(username)
        if result:
            return True
        else:
            return False

    @rpc
    def check_password_match(self, username, password):
        return bcrypt.checkpw(password.encode('UTF-8'), self.database.get_user(username)["password"].encode('UTF-8'))

    @rpc
    def register_user(self, username, password):
        username = username.lower()
        if not self.check_username_exist(username):
            self.database.register_user(username, bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt()).decode('UTF-8'))
