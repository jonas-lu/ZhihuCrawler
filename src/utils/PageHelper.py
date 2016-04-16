from pyquery import PyQuery as pq
import json


def get_xsrf(html):
    d = pq(html)
    xsrf = d("input[name=_xsrf]")
    return xsrf.attr("value")


def get_user_hash(html):
    d = pq(html)
    return json.loads(d("script[data-name=current_people]").text())[3]
