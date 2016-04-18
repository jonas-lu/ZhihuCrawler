import threading
import logging
import json
import time
from model.user import User
from utils import redis_helper as rh


class Storing(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self._terminated = False

    def run(self):
        self.logger.warning('start fetch result')
        while True:
            if self._terminated:
                self.logger.warning('Terminate storage thread gracefully')
                break
            user = rh.bpop_result_user(10)
            if user:
                user_json = user[1].decode('utf-8')
                user_dict = json.loads(user_json)

                if user_dict:
                    start_time  = time.time()
                    user = User(user_dict)
                    tasks = user.get_tasks()
                    if len(tasks) > 0:
                        rh.rpush_task_user(tasks)
                    self.logger.warning("Push %s tasks in %s secs", len(tasks), round(time.time() - start_time, 2))
            else:
                time.sleep(2)

    def terminate(self):
        self._terminated = True
        self.logger.warning('Waiting for storage to terminate...')
