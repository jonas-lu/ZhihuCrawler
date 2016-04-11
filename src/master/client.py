import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)
while True:
    number = r.blpop("username", 5)
    print(int(number[1]))