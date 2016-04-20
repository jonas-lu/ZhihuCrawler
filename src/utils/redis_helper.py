from config import get as config
import redis
import logging
import json
from exception import RedisException, AccountException, NoTaskException

r = redis.StrictRedis(host=config('redis.server'), port=config('redis.port'), db=config('redis.db'))
logger = logging.getLogger(__name__)


def get_task_user():
    try:
        task_str = r.blpop(config('queue.task_user'), 120)
        if not task_str:
            logger.error('No task, quit')
            raise NoTaskException
        return task_str[1].decode('utf-8')
    except ConnectionError as e:
        logger.error(e)
        raise RedisException


def push_result_user(user):
    try:
        r.rpush(config('queue.result_user'), json.dumps(user, ensure_ascii=False).encode('utf-8'))
    except ConnectionError as e:
        logger.error(e)
        raise RedisException


def bpop_result_user(timeout):
    try:
        return r.blpop(config('queue.result_user'), timeout)
    except ConnectionError as e:
        logger.error(e)
        raise RedisException


def rpush_task_user(user_domain_list):
    try:
        r.rpush(config('queue.task_user'), *user_domain_list)
    except ConnectionError as e:
        logger.error(e)
        raise RedisException


def lpush_task_user(user_domain):
    try:
        r.lpush(config('queue.task_user'), user_domain.encode('utf-8'))
    except ConnectionError as e:
        logger.error(e)
        raise RedisException


def push_acct(acct):
    try:
        r.rpush(config('queue.admin_acct'), json.dumps(acct).encode('utf-8'))
    except ConnectionError as e:
        logger.error(e)
        raise RedisException


def get_acct():
    try:
        acct = r.blpop(config('queue.admin_acct'), 120)
        if not acct:
            logger.error('No account, quit')
            raise AccountException
        return json.loads(acct[1].decode('utf-8'))
    except ConnectionError as e:
        logger.error(e)
        raise RedisException


def del_queue(q):
    try:
        r.delete(q)
    except ConnectionError as e:
        logger.error(e)
        raise RedisException


def publish_status(status):
    try:
        r.publish(config('channel.admin_status'), json.dumps(status, ensure_ascii=False).encode('utf-8'))
    except ConnectionError as e:
        logger.error(e)
        raise RedisException


def is_user_crawled(user_domain):
    try:
        return r.sismember(config('set.crawled_user'), user_domain)
    except ConnectionError as e:
        logger.error(e)
        raise RedisException


def add_crawled_user(user_domain):
    try:
        r.sadd(config('set.crawled_user'), user_domain)
    except ConnectionError as e:
        logger.error(e)
        raise RedisException
