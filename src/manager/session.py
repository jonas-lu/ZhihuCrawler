from utils import PageHelper
from manager import UserAgent, Proxy, Account
import requests
import logging
import time
from exception import NetworkException, AccountException


def get():
    s = requests.session()
    s.headers.update({'User-Agent': UserAgent.get()})
    s.proxies = Proxy.get()
    account = Account.get()
    logger = logging.getLogger(__name__)

    for i in range(6):
        try:
            _xsrf = PageHelper.get_xsrf(s.get("http://www.zhihu.com").content)
            data = {
                '_xsrf': _xsrf,
                'email': account['username'],
                'password': account['password'],
                'remember_me': 'true'
            }

            response = s.post("http://www.zhihu.com/login/email", data)
            res = response.json()
            if res['r'] == 0:
                logger.info("Login Success")
                break
            else:
                if i == 5:
                    raise AccountException()
                else:
                    logger.warning('Login Failed %s, Change Account, Retry', res)
                    account = Account.get()
        except requests.RequestException:
            if i == 5:
                raise NetworkException()
            if i % 2 == 1:
                s.proxies = Proxy.get()
                logger.warning("Request Failed, Change Proxy, Retry")
            else:
                logger.warning("Request Failed, Retry in 10s")
                time.sleep(10)

    return s


if __name__ == '__main__':
    try:
        get()
    except NetworkException:
        print('network error')
