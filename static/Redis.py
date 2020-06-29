import redis
import json

class Redis(object):

    def __init__(self,ip='localhost',redis_port='6379',password=None,db=0,__db=[1,2]):
        self.ip = ip
        self.redis_port = redis_port
        self.password = password
        self._db = db
        self.__dbs = __db

    @property
    def redis(self):
        return redis.StrictRedis(host=self.ip,port=self.redis_port,password=self.password,db=self._db)

    def get(self,table_name,db=None):
        if db != None:self._db = db
        return self.redis.get(table_name)

    def keys(self,db=None):
        if db != None:self._db = db
        return (i.decode('utf8') for i in self.redis.keys())

    def pop(self,table_name,db=None):
        if db != None:self._db = db
        data = self.redis.lpop(table_name)
        self._db = self.__dbs[-1]
        self.redis.incr(table_name,amount=-1)
        return data

    def role(self,table_name,lis):
        self._db = self.__dbs[0]
        __db1 = self.redis
        self._db = self.__dbs[-1]
        __db2 = self.redis
        __num = 0
        for i in lis:
            if type(i) == dict:
                if i.get('_id'):i.pop('_id')
                data = json.dumps(i)
            else:
                data = i
            __db1.rpush(table_name,data)
            __num += 1
        __db2.set(table_name,__num if __db2.get(table_name) == None else __num + int(__db2.get(table_name).decode('utf8')))
        return True

    def del_All(self,db=None,name=None):
        if db != None:self._db = db
        if not name:
            [self.redis.delete(i) for i in self.redis.keys()]
        else:
            self.redis.delete(name)
        return True

    def All_lis(self,db=None,key=None):
        if db != None:self._db = db
        __db = self.redis
        if key:
            return (
                json.loads(__db.get(i).decode('utf8')) for i in __db.keys() if key and json.loads(__db.get(i).decode('utf8')).get(key)
            )
        else:
            return (
                json.loads(__db.get(i).decode('utf8')) for i in __db.keys()
            )

if __name__ == '__main__':
    r = Redis()
    # r.role('users',r.keys(0))
    url = 'https://weixin.sogou.com/weixin?query=python&_sug_type_=&s_from=input&_sug_=y&type=2&page=2&ie=utf8'
    # print(r.keys(1))
    # print(r.pop('users',db=1))
    # print(r.get(db=2,table_name='users'))
    # r.insert_lis('users',r.keys(0),db=0)
    # print(r.pop(1,'users'))
    # r.redis(1)
    # print(r.keys())
    # r.del_All(1)