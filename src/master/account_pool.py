from config import get as config
from utils import redis_helper as rh
import json
import logging
import os


all_acct_file = config('root') + 'resource/zhihu_acct.txt'
free_acct_file = config('root') + 'resource/free_acct.txt'
free_acct_dict = {}

logger = logging.getLogger(__name__)


def init():
    logger.warning('Init accounts pool...')
    rh.del_queue(config('queue.admin_acct'))

    with open(all_acct_file, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            else:
                acct = line.strip().split(' ')
                acct_dict = {
                    'username': acct[0],
                    'password': acct[1]
                }
                rh.push_acct(acct_dict)

    # try:
    #     load()
    # except ValueError:
    #     construct_file()
    #     load()
    #
    # for acct in free_acct_dict:
    #     acct_dict = {
    #         'username': acct,
    #         'password': free_acct_dict[acct]
    #     }
    #     rh.push_acct(acct_dict)


def remove(username):
    if username in free_acct_dict:
        del free_acct_dict[username]
        save()
        logger.warning('Removed %s from account pool', username)


def save():
    with open(free_acct_file, 'w') as f:
        f.write(json.dumps(free_acct_dict))


def load():
    global free_acct_dict
    logger.warning('Load free accounts file...')
    if not os.path.isfile(free_acct_file):
        construct_file()
    with open(free_acct_file, 'r') as f:
        content = f.read()
        if not content:
            construct_file()
        else:
            free_acct_dict = json.loads(content)


def construct_file():
    logger.warning('Construct free accounts file...')
    with open(all_acct_file, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            else:
                acct = line.strip().split(' ')
                free_acct_dict[acct[0]] = acct[1]

        save()
