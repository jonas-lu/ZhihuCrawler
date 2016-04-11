from account_manager import AccountManager
from session_factory import SessionFactory
from followees_crawler import FolloweesCrawler
import redis
import json
import time


def main():
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    acct_str = r.blpop('zh_accounts', 30)
    if not acct_str:
        print("NO ACCT")
        exit()
    acct = json.loads(acct_str[1].decode('utf-8'))
    print('GET ACCT:', acct)

    session_factory = SessionFactory(acct)
    session = session_factory.get_login_session()

    while True:
        task_str = r.blpop('zh_tasks', 30)
        if not task_str:
            print('NO TASK')
            exit()
        task = task_str[1].decode('utf-8')
        print('GET TASK:', task)

        fc = FolloweesCrawler(session, task)
        user = fc.get_followees()
        r.rpush('zh_results', json.dumps(user).encode('utf-8'))
        time.sleep(5)


if __name__ == '__main__':
    main()