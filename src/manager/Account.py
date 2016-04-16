from utils import redis_helper as rh
from config import get as config
import logging
import os

logger = logging.getLogger(__name__)
acct_file = config('root') + 'cache/account.txt'


# def get(*old):
#     global using
#
#     if config('env') == 'dev':
#         return {
#             'username': 'yazax86152@163.com',
#             'password': 'gze2772'
#         }
#
#     if old:
#         rh.push_acct(old[0])
#     else:
#         if os.path.isfile(acct_file):
#             with open(acct_file, 'r') as f:
#                 line = f.readline()
#                 if line:
#                     acct = line.strip().split(' ')
#                     logger.warning('Get new account %s from cache', acct[0])
#                     using = {
#                         'username': acct[0],
#                         'password': acct[1]
#                     }
#                     return using
#
#     new_acct = rh.get_acct()
#     with open(acct_file, 'w') as f:
#         f.write(new_acct['username'] + ' ' + new_acct['password'])
#     logger.warning('Get new account %s from master', new_acct['username'])
#
#     using = new_acct
#     return new_acct

using = {}


def get(*old):
    global using

    if config('env') == 'dev':
        return {
            'username': 'yazax86152@163.com',
            'password': 'gze2772'
        }

    if old:
        rh.push_acct(old[0])

    new_acct = rh.get_acct()
    logger.warning('Get new account %s from master', new_acct['username'])

    using = new_acct
    return new_acct


def get_using():
    return using
