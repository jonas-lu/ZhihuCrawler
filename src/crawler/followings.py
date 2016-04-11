from pyquery import PyQuery as pq
import json
from utils import PageHelper
from manager import Session
import logging

FOLLOWEES_JSON_URL = 'https://www.zhihu.com/node/ProfileFolloweesListV2'


class FollowingsCrawler:

    def __init__(self, logged_session, user_domain):
        self.session = logged_session
        self.user_domain = user_domain
        self.xsrf = ''
        self.user = {
            'followings': []
        }
        self.url = 'https://www.zhihu.com/people/' + user_domain + '/followees'
        self.page = ''

    def get_followings_page(self):
        self.page = self.session.get(self.url).content
        self.user['hashid'] = PageHelper.get_user_hash(self.page)
        self.xsrf = PageHelper.get_xsrf(self.page)

    def get_followings_json(self, offset):
        form = {
            'method': 'next',
            'params': json.dumps({'offset': offset, 'order_by': 'created', 'hash_id': self.user['hashid']}),
            '_xsrf': self.xsrf
        }
        response = self.session.post('https://www.zhihu.com/node/ProfileFolloweesListV2', data=form)
        html = response.json()['msg']
        return html[0] if len(html) else None

    def get_followings_from_html(self, html):
        d = pq(html)
        people = d('.zm-profile-card')
        for person in people.items():
            hashid = person.find('button').attr('data-id')
            s_person_link = person.find('.zm-list-content-title a')
            profile = {
                'hashid': hashid,
                'id': s_person_link.attr('href')[29:],
                'name': s_person_link.text()
            }
            self.user['followings'].append(profile)

    def get_profile(self):
        d = pq(self.page)
        d_info = d('.zm-profile-header-user-describe .info-wrap')
        self.user['location'] = d_info.find('span.location').attr('title') or ''
        self.user['business'] = d_info.find('span.business').attr('title') or ''
        self.user['employment'] = d_info.find('span.employment').attr('title') or ''
        self.user['position'] = d_info.find('span.position').attr('title') or ''
        self.user['education'] = d_info.find('span.education').attr('title') + ' ' + d_info.find('span.education-extra').attr('title') or ''
        d_gender = d_info.find('span.gender i')
        self.user['gender'] = 'female' if d_gender.hasClass('icon-profile-female') else 'male'

    def get(self):
        self.get_followings_page()
        self.get_profile()
        while True:
            html = self.get_followings_json(len(self.user['followings']))
            if html:
                self.get_followings_from_html(html)
            else:
                break
        return self.user


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    s = Session.get()
    fc = FollowingsCrawler(s, 'pan-hui-qi')
    print(fc.get())
