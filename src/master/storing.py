import threading
from config import get as config
import logging
import redis
import json
import time
from model.user import User
from exception import RedisException


class Storing(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self._terminated = False
        try:
            self.r = redis.StrictRedis(host=config('redis.server'), port=config('redis.port'), db=config('redis.db'))
        except ConnectionError:
            self.logger.error('failed to connect to redis')
            raise RedisException

    def run(self):
        self.logger.warning('start fetch result')
        while True:
            if self._terminated:
                self.logger.warning('Terminate storage thread gracefully')
                break
            user = self.r.blpop(config('queue.result_user'), 10)
            if user:
                user_json = user[1].decode('utf-8')
                user_dict = json.loads(user_json)

                if user_dict:
                    user = User(user_dict)
                    new_task = 0
                    for task in user.get_tasks():
                        self.r.rpush(config('queue.task_user'), task['domain'].encode('utf-8'))
                        new_task += 1
                    self.logger.warning("Push %s tasks", new_task)
            else:
                time.sleep(2)

    def terminate(self):
        self._terminated = True
        self.logger.warning('Waiting for storage to terminate...')
