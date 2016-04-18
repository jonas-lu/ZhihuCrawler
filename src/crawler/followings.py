from pyquery import PyQuery as pq
import json
from utils import PageHelper
from manager import Session
import logging
import time
import random
from config import get as config

FOLLOWEES_JSON_URL = 'https://www.zhihu.com/node/ProfileFolloweesListV2'


class FollowingsCrawler:

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
        self.xsrf = PageHelper.get_xsrf(self.page)

    def get_followings_json(self, offset):
        form = {
            'method': 'next',
            'params': json.dumps({'offset': offset, 'order_by': 'created', 'hash_id': self.user['hashid']}),
            '_xsrf': self.xsrf
        }

        response = self.session.post('https://www.zhihu.com/node/ProfileFolloweesListV2', form)

        html = response.json()['msg']

        if len(html) == 1:
            d = pq(html[0])
            if not d('button'):
                return None

        return html if len(html) else None

    def get_followings_from_html(self, htmls):
        d = pq(''.join(htmls))
        people = d('.zm-profile-card')

        for person in people.items():
            try:
                hashid = person.find('button').attr('data-id')
                s_person_link = person.find('.zm-list-content-title a')
                profile = {
                    'hashid': hashid,
                    'domain': s_person_link.attr('href')[29:],
                    'name': s_person_link.text()
                }
                self.user['followings'].append(profile)
            except TypeError:
                continue

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
        while True:
            html = self.get_followings_json(len(self.user['followings']))
            if html:
                self.get_followings_from_html(html)
            else:
                break
            time.sleep(random.uniform(0.5, 2))
        self.logger.warning('Finish crawling %s, %s followings', self.user_domain, len(self.user['followings']))
        return self.user


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    s = Session.get()
    fc = FollowingsCrawler(s, 'zhang-wen-wen-17')
    print(fc.get())
