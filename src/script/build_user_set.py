import os
import sys
import py2neo
import redis


def start():
    py2neo.authenticate(config('neo4j.server'), config('neo4j.username'), config('neo4j.password'))
    g = py2neo.Graph()

    r = redis.StrictRedis(host=config('redis.server'), port=config('redis.port'), db=config('redis.db'))

    number = 0
    for node in g.cypher.execute("match (n:USER) where exists(n.gender) return n.domain as domain"):
        number += 1
        print(number, node.domain)
        r.sadd(config('set.crawled_user'), node.domain)

if __name__ == '__main__':
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(CURRENT_DIR))

    from config import get as config

    start()
