from pyquery import PyQuery as pq
from account_manager import AccountManager
import utils


class SessionFactory(object):
    account = None

    @classmethod
    def __init__(cls, account):
        cls.account = account

    @classmethod
    def login_zhihu(cls):
        session = utils.get_session()

        _xsrf = utils.get_xsrf(utils.download_page("http://www.zhihu.com"))
        data = {
            '_xsrf': _xsrf,
            'email': cls.account['username'],
            'password': cls.account['password'],
            'remember_me': 'true'
        }

        response = session.post("http://www.zhihu.com/login/email", data)
        res = response.json()
        # res = json.loads(response.decode('utf8'), 'utf8')
        print(res['msg'])

        return session

    @classmethod
    def get_login_session(cls):
        return cls.login_zhihu()

if __name__ == '__main__':
    account = AccountManager.get_account()
    session_factory = SessionFactory(account)
    session_factory.get_login_session()
