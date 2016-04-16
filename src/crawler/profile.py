from pyquery import PyQuery as pq
from utils import PageHelper
from manager import Session
import logging
import config


class ProfileCrawler:

    def __init__(self, session, user_domain):
        self.session = session
        self.user_domain = user_domain
        self.xsrf = ''
        self.user = {
            'followings': []
        }
        self.url = 'https://www.zhihu.com/people/' + user_domain + '/followees'
        self.page = ''

        self.logger = logging.getLogger(__name__)

    def get_followings_page(self):
        response = self.session.get(self.url)
        self.page = response.content
        self.user['hashid'] = PageHelper.get_user_hash(self.page)

    def get_profile(self):
        d = pq(self.page)
        self.user['name'] = d('.zm-profile-header-main .top .title-section .name').text()
        self.user['domain'] = self.user_domain
        d_info = d('.zm-profile-header-user-describe .info-wrap')
        self.user['location'] = d_info.find('span.location').attr('title') or ''
        self.user['business'] = d_info.find('span.business').attr('title') or ''
        self.user['employment'] = d_info.find('span.employment').attr('title') or ''
        self.user['position'] = d_info.find('span.position').attr('title') or ''
        edu = d_info.find('span.education').attr('title') or ''
        edu_ex = d_info.find('span.education-extra').attr('title') or ''
        self.user['education'] = ' ' if edu else '' + edu_ex
        d_gender = d_info.find('span.gender i')
        self.user['gender'] = 'female' if d_gender.hasClass('icon-profile-female') else 'male'

        self.user['agree'] = int(d('.zm-profile-header-user-agree strong').text())
        self.user['thanks'] = int(d('.zm-profile-header-user-thanks strong').text())
        self.user['asks'] = int(d('.profile-navbar a.item').eq(1).find('span.num').text())
        self.user['answers'] = int(d('.profile-navbar a.item').eq(2).find('span.num').text())
        self.user['posts'] = int(d('.profile-navbar a.item').eq(3).find('span.num').text())
        self.user['collections'] = int(d('.profile-navbar a.item').eq(4).find('span.num').text())
        self.user['logs'] = int(d('.profile-navbar a.item').eq(5).find('span.num').text())

        self.user['followings_num'] = int(d('.zm-profile-side-following a.item').eq(0).find('strong').text())
        self.user['followers_num'] = int(d('.zm-profile-side-following a.item').eq(1).find('strong').text())

        self.user['weibo'] = d('a.zm-profile-header-user-weibo').attr('href') or ''

    def get(self):
        self.logger.warning('Start crawling %s', self.user_domain)
        self.get_followings_page()
        self.get_profile()

        self.logger.warning('Finish crawling profile for %s,', self.user_domain)
        return self.user


if __name__ == '__main__':
    config.set_config('env', 'dev')
    logging.basicConfig(level=logging.INFO)
    s = Session.get()
    pc = ProfileCrawler(s, 'jonas-lu')
    user = pc.get()
    for p in user:
        print(p, user[p])
