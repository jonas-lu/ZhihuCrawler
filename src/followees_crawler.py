from pyquery import PyQuery as pq
import json
import utils

FOLLOWEES_JSON_URL = 'https://www.zhihu.com/node/ProfileFolloweesListV2'


class FolloweesCrawler():

    def __init__(self, session, user_domain):
        self.session = session
        self.user_domain = user_domain
        self.followees = []
        self.url = 'https://www.zhihu.com/people/' + user_domain + '/followees'

    def get_user_hash(self, html):
        d = pq(html)
        return json.loads(d("script[data-name=current_people]").text())[3]

    def get_followees_page(self):
        page = self.session.get(self.url).content
        self.user_hash = self.get_user_hash(page)
        self.xsrf = utils.get_xsrf(page)

    def get_followees_json(self, offset):
        form = {
            'method': 'next',
            'params': json.dumps({'offset':offset,'order_by':'created','hash_id':self.user_hash}),
            '_xsrf': self.xsrf
        }
        response = self.session.post('https://www.zhihu.com/node/ProfileFolloweesListV2', data = form)
        html = response.json()['msg']
        return html[0] if len(html) else None

    def get_followee_hashid_from_html(self, html):
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
            self.followees.append(profile)

    def get_followees(self):
        self.get_followees_page()
        while(True):
            html = self.get_followees_json(len(self.followees))
            if html:
                self.get_followee_hashid_from_html(html)
            else:
                break
        return {
            'id': self.user_domain,
            'hashid': self.user_hash,
            'followees': self.followees
        }