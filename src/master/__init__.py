import redis
from config import get as config
import logging
from .storing import Storing
from . import account_pool as ah
import json

storage = Storing()
logger = logging.getLogger(__name__)


def start(seed):
    status = {}

    r = redis.StrictRedis(host=config('redis.server'), port=config('redis.port'), db=config('redis.db'))
    ah.init()

    if int(r.llen(config('queue.task_user')) == 0):
        r.rpush(config('queue.task_user'), seed)
        logger.warning('Push seed task')

    storage.start()

    pubsub = r.pubsub()
    pubsub.subscribe([config('channel.admin_status')])
    for item in pubsub.listen():
        if item['type'] == 'message':
            message = item['data']
            update = json.loads(message.decode('utf-8'))
            logger.warning('New message from %s, status: %s', update['id'], update['status'])
            ah.remove(update['account']['username'])

            status[update['id']] = update
            r.set(config('keys.system_info'), status)

    storage.join()


def terminate():
    storage.terminate()
    storage.join()
    logger.warning('Quit')
    exit()


if __name__ == '__main__':
    start('jonas-lu')
