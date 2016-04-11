import redis
import json
import time
import account_mgr as AcctMgr

TASK_QUEUE = 'zh_tasks'
ACCT_QUEUE = 'zh_accounts'
RESULT_QUEUE = 'zh_results'


def start(seed):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.delete(TASK_QUEUE)
    r.rpush(TASK_QUEUE, seed.encode('utf-8'))
    r.delete(ACCT_QUEUE)
    acct_json = json.dumps(AcctMgr.get())
    print(acct_json)
    r.rpush(ACCT_QUEUE, acct_json.encode('utf-8'))

    while True:
        result = r.blpop(RESULT_QUEUE, 5)
        if result:
            user_json = result[1].decode('utf-8')
            user = json.loads(user_json)
            for followee in user['followees']:
                id = followee['id']
                print('PUSH TASK:', id)
                r.rpush(TASK_QUEUE, id.encode('utf-8'))
            with open('result.txt', 'a') as fout:
                fout.write(user_json)
        else:
            time.sleep(5)

if __name__ == '__main__':
    start('jonas-lu')