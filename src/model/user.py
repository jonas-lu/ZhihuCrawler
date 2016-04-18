import logging
import py2neo
import json
from config import get as config
from utils import redis_helper as rh


class User:
    def __init__(self, user):
        logger = logging.getLogger(__name__)
        logger.warning("Storing %s(%s), %s followings", user['name'], user['domain'], len(user['followings']))

        rh.add_crawled_user(user['domain'])

        self.followings = user['followings']
        del user['followings']
        self.user = user

        py2neo.authenticate(config('neo4j.server'), config('neo4j.username'), config('neo4j.password'))
        self.g = py2neo.Graph()

        self.src_node = self.merge_node(user)

    def user_exists(self):
        return True if self.g.find_one('USER', 'hashid', self.user['hashid']) else False

    def followings_exists(self, hashid):
        user = self.g.find_one('USER', 'hashid', hashid)
        if not user:
            return False
        else:
            return True if self.g.match_one(user, 'FOLLOWS') else False

    def merge_node(self, node_dict):
        node = self.g.merge_one('USER', 'hashid', node_dict['hashid'])
        for p in node_dict:
            if not node.properties[p]:
                node.properties[p] = node_dict[p]

        node.push()
        return node

    def get_tasks(self):
        tasks = []
        # relationships = []
        for f in self.followings:
            if f['hashid']:
                dst_node = self.merge_node(f)
                follows = py2neo.Relationship(self.src_node, 'FOLLOWS', dst_node)
                # relationships.append(follows)
                self.g.create_unique(follows)

                if not rh.is_user_crawled(f['domain']):
                    tasks.append(f['domain'].encode('utf-8'))

        # if len(relationships) > 0:
        #     self.g.create_unique(*relationships)

        return tasks


if __name__ == '__main__':
    with open('1.json', 'r') as fin:
        while True:
            line = fin.readline()
            if not line:
                break
            user = User(json.loads(line.strip()))
            for t in user.get_tasks():
                print(t)
            print()
