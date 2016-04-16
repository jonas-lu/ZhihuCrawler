import sys
import os
import py2neo
import logging
import time


if __name__ == '__main__':
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(CURRENT_DIR))

    from crawler.profile import ProfileCrawler
    from config import get as config
    from model.user import User
    from utils.session_helper import SessionHelper
    from exception import NotFoundException

    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(__name__)

    py2neo.authenticate(config('neo4j.server'), config('neo4j.username'), config('neo4j.password'))
    g = py2neo.Graph()

    s = SessionHelper()

    i = 0
    for u in g.cypher.execute("match (a:USER) where exists(a.gender) and not exists(a.weibo) return a.domain as domain"):
        i += 1
        print(i, u.domain)
        try:
            pc = ProfileCrawler(s, u.domain)
            profile = pc.get()

            User(profile)
            time.sleep(0.5)
        except NotFoundException:
            continue
