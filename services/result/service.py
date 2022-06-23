from nameko.rpc import rpc
from dependencies.database import DatabaseProvider


class ResultService:

    name = 'result_service'
    database = DatabaseProvider()

    @rpc
    def get_request_data(self, request_id):
        return self.database.get_request_data(request_id)
