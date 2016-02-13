from pyquery import PyQuery as pq
import json

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
        user_hash = self.get_user_hash(page)
        d = pq(page)
        people = d('#zh-profile-follows-list .zm-profile-card')
        for person in people.items():
            hashid = person.find('button.zg-btn-follow').attr('data-id')
            s_person_link = person.find('.zm-list-content-title a')
            profile = {
                'hashid': hashid,
                'id': s_person_link.attr('href')[29:],
                'name': s_person_link.text()
            }
            print(profile)
            break
