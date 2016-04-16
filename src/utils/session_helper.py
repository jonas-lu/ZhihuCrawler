from exception import NotFoundException, ResponseException, NetworkException
import logging
import time
import random
from manager import Session
import requests


class SessionHelper:
    def __init__(self):
        self.session = Session.get()
        self.logger = logging.getLogger(__name__)

    def get(self, url):
        for i in range(10):
            try:
                response = self.session.get(url)
                code = response.status_code
                if code == 200:
                    return response
                elif code == 404:
                    raise NotFoundException
                else:
                    self.logger.error("Bad response: %s, retry", response.status_code)
                    time.sleep(i + random.uniform(0.5, 1.5))
            except requests.ConnectionError:
                self.logger.error("Connection error, retry")
                time.sleep(2 + 2*i)
                if i == 9:
                    raise NetworkException

        raise ResponseException

    def post(self, url, form):
        for i in range(10):
            try:
                response = self.session.post(url, data=form)
                code = response.status_code
                if code == 200:
                    return response
                elif code == 404:
                    raise NotFoundException
                else:
                    self.logger.error("Bad response: %s, retry", response.status_code)
                    time.sleep(i + random.uniform(0.5, 1.5))
            except requests.ConnectionError:
                self.logger.error("Connection error, retry")
                time.sleep(2 + 2*i)
                if i == 9:
                    raise NetworkException

        raise ResponseException
