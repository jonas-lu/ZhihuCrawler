import time
import logging
import random
from crawler.followings import FollowingsCrawler
from utils import redis_helper as rh
from exception import *
from utils.session_helper import SessionHelper
import socket
from manager import Account

status = {}
logger = logging.getLogger(__name__)
finished = {
    'user': 0,
    'followings': 0
}


def start(instance_id):
    global task
    global status
    task = ''

    logger.warning('Instance id: %s', instance_id)

    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    start_time = int(time.time())

    session = SessionHelper()

    status = {
        'id': hostname + '-' + str(instance_id),
        'hostname': hostname,
        'ip': ip,
        'finished': finished,
        'task': '',
        'status': 'init',
        'message': '',
        'account': Account.get_using(),
        'start_time': start_time,
        'update_time': int(time.time())
    }

    rh.publish_status(status)

    while True:
        task = ''
        try:
            task = rh.get_task_user()
            logger.warning('Get task: ' + task)

            if rh.is_user_crawled(task):
                logger.warning("User %s crawled, skip", task)
                continue

            status.update({
                'finished': finished,
                'task': task,
                'status': 'crawling',
                'account': Account.get_using(),
                'update_time': int(time.time())
            })
            rh.publish_status(status)

            fc = FollowingsCrawler(session, task)
            user = fc.get()
            logger.warning('Push result: ' + task)
            rh.push_result_user(user)

            finished['user'] += 1
            finished['followings'] += len(user['followings'])

            time.sleep(random.uniform(1, 5))
        except ResponseException:
            if task:
                rh.lpush_task_user(task)
            message = 'Crawling response error, push back task, quit'
            logger.error(message)
            status.update({
                'finished': finished,
                'task': task,
                'status': 'error',
                'message': message,
                'account': Account.get_using(),
                'update_time': int(time.time())
            })
            rh.publish_status(status)
            exit()
        except RedisException:
            logger.error('Redis connection error, quit')
            exit()
        except NetworkException:
            message = 'Network connection error, quit'
            logger.error(message)
            status.update({
                'finished': finished,
                'task': task,
                'status': 'error',
                'message': message,
                'account': Account.get_using(),
                'update_time': int(time.time())
            })
            rh.publish_status(status)
            logger.error(message)
            exit()
        except NotFoundException:
            message = "User %s not found, continue" % task
            logger.error(message)
            status.update({
                'finished': finished,
                'task': task,
                'status': 'warning',
                'message': message,
                'account': Account.get_using(),
                'update_time': int(time.time())
            })
            rh.publish_status(status)
            continue


def terminate():
    logger.error('Terminate gracefully...')

    acct = Account.get_using()
    rh.push_acct(acct)
    logger.error('return account %s', acct['username'])

    if task:
        rh.lpush_task_user(task)
        logger.error('return task %s', task)

    status.update({
        'finished': finished,
        'task': task,
        'status': 'exit',
        'message': 'Exit gracefully',
        'account': acct,
        'update_time': int(time.time())
    })
    rh.publish_status(status)

    logger.error('Exit')
    exit()
