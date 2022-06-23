from nameko.rpc import rpc
from dependencies.database import DatabaseProvider
from celery import Celery
import os

rabbit_url = f'amqp://{os.environ.get("RABBIT_USER", "guest")}:{os.environ.get("RABBIT_PASSWORD", "guest")}@{os.environ.get("RABBIT_HOST", "localhost")}:{os.environ.get("RABBIT_PORT", 5672)}/'

celery_app = Celery(
    'tasks', broker=rabbit_url, backend=rabbit_url)


class SpawnerService:

    name = 'spawner_service'
    database = DatabaseProvider()

    @rpc
    def create_prime_request(self, request_username, request_input):
        request_id = self.database.create_request('prime', request_username, request_input)
        cached = self.database.get_cached_result('prime', request_input)
        if not cached or len(cached) == 0:
            celery_app.send_task('tasks.prime', args=[request_id, request_input])
        else:
            self.database.post_result(request_id, cached['result'])
        return request_id

    @rpc
    def create_prime_palindrome_request(self, request_username, request_input):
        request_id = self.database.create_request('prime_palindrome', request_username, request_input)
        cached = self.database.get_cached_result('prime_palindrome', request_input)
        if not cached or len(cached) == 0:
            celery_app.send_task('tasks.palindromic_prime', args=[request_id, request_input])
        else:
            self.database.post_result(request_id, cached['result'])
        return request_id
