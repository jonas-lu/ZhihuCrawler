from utils import PageHelper
from manager import UserAgent, Proxy, Account
import requests
import logging
import time
from exception import NetworkException, AccountException
import config
from utils import decaptcha as dmt

logger = logging.getLogger(__name__)


def get():
    s = requests.session()
    s.headers.update({'User-Agent': UserAgent.get()})
    s.proxies = Proxy.get()
    account = Account.get()

    for i in range(6):
        try:
            page = s.get("http://www.zhihu.com").content
            captcha = decaptcha(s)

            _xsrf = PageHelper.get_xsrf(page)
            data = {
                '_xsrf': _xsrf,
                'password': account['password'],
                'remember_me': 'true'
            }
            if captcha:
                data.update({'captcha': captcha})

            if '@' in account['username']:
                data['email'] = account['username']
                login = 'http://www.zhihu.com/login/email'
            else:
                data['phone_num'] = account['username']
                login = 'http://www.zhihu.com/login/phone_num'

            response = s.post(login, data)
            res = response.json()
            if res['r'] == 0:
                logger.warning("Login Success")
                break
            else:
                if i == 5:
                    raise AccountException()
                else:
                    logger.error('Login Failed %s, Change Account, Retry', res)
                    account = Account.get(account)
        except requests.RequestException:
            if i == 5:
                raise NetworkException()
            if i % 2 == 1:
                s.proxies = Proxy.get()
                logger.error("Request Failed, Change Proxy, Retry")
            else:
                logger.error("Request Failed, Retry in 10s")
                time.sleep(10)

    return s


def decaptcha(session):
    global logger

    r = int(round(time.time(), 3) * 1000)
    url = "https://www.zhihu.com/captcha.gif?r=%s&type=login" % r
    img = session.get(url).content
    captcha_file = config.get('root') + 'cache/' + str(r) + '.gif'
    with open(captcha_file, 'wb') as f:
        f.write(img)

    logger.warning('Start cracking captcha...')
    decap = dmt.DamatuApi(config.get('dmt.username'), config.get('dmt.password'))
    captcha = decap.decode(captcha_file, 42)
    logger.warning('Cracked captcha: %s', captcha)
    return captcha


if __name__ == '__main__':
    try:
        config.set_config('env', 'dev')
        get()
    except NetworkException:
        print('network error')
