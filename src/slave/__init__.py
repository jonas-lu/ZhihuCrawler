import time
import logging
import random
from crawler.followings import FollowingsCrawler
from utils import redis_helper as rh
from exception import *
from utils.session_helper import SessionHelper
import socket
from manager import Account
import traceback
import sys

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

    try:
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

            try:
                fc = FollowingsCrawler(session, task)
                user = fc.get()
                logger.warning('Push result: ' + task)
                rh.push_result_user(user)

                finished['user'] += 1
                finished['followings'] += len(user['followings'])

                time.sleep(random.uniform(1, 5))
            except NotFoundException:
                message = "User %s not found, continue" % task
                logger.error(message)
                continue
    except ResponseException:
        message = 'Crawling response error, push back task, quit'
        terminate(message)
    except RedisException:
        logger.error('Redis connection error, quit')
        sys.exit('Redis Error!')
    except NetworkException:
        message = 'Network connection error, quit'
        terminate(message)
    except Exception as e:
        print(traceback.format_exc())
        terminate(e)


def terminate(*msg):
    if msg:
        logger.error(msg[0])
        status.update({
            'status': 'error',
            'message': str(msg[0])
        })
    else:
        status.update({
            'status': 'exit',
            'message': 'Exit gracefully',
        })

    logger.error('Terminate gracefully...')

    acct = Account.get_using()
    if 'username' in acct:
        rh.push_acct(acct)
        logger.error('return account %s', acct['username'])

    if task:
        rh.lpush_task_user(task)
        logger.error('return task %s', task)

    status.update({
        'finished': finished,
        'task': task,
        'account': acct,
        'update_time': int(time.time())
    })
    rh.publish_status(status)

    logger.error('Exit')
    if msg:
        sys.exit(msg[0])
    else:
        sys.exit(0)
