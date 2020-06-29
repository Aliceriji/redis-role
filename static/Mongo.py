import pymongo

class Mongo:
    file_path = r'/MONGO_BAK/'

    def __init__(self,ip='localhost',password=None,mongo_port=27017,mongo_username=None):
        '''
        :param hosts: 连接地址 默认为8001
        '''
        if password and mongo_port:
            self.hosts = 'mongodb://{u}:{p}@{ip}:{port}/'.format(u=mongo_username,p=password,ip=ip,port=mongo_port)
        else:
            self.hosts = 'mongodb://{ip}:{port}/'.format(ip=ip, port=mongo_port)
        self.mongo = pymongo.MongoClient(self.hosts)

    def __call__(self, db=None, table=None, **kwargs):
        '''
        :param db: 数据库名称
        :param table: 表单名称
        :param kwargs: 固定查询，形式为 'name' = 'ljc'
        :return: 查询的列表数据
        '''
        if db == None or table == None:
            return '缺少参数'
        return list(self.mongo[db][table].find(kwargs))

    def All_lis(self, db_name, table_name, key=None):
        '''
        :param db_name: 数据库名称
        :param table_name: 表名，类似相同的表名
        :param key: 返回指定key的列表
        :return:存在key，返回列表，不存在时，返回迭代对象
        '''
        table_names = [i for i in self.mongo[db_name].list_collection_names() if table_name in i]
        if key:
            return [
                li.get(key) for name in table_names for li in self.mongo[db_name][name].find({},projection=[key])
            ]
        else:
            return (
                li for name in table_names for li in self.mongo[db_name][name].find({})
            )

    def insert(self, db_name, table_name, data):
        '''
        :param db_name:指定数据库
        :param table_name: 指定类似表名
        :param data: 传入值，值只能单个单个传入
        :return:
        '''
        if type(data) == dict:
            pass
        elif type(data) == list:
            return '请一个一个传入'
        db_names = [i for i in self.mongo.list_database_names()]
        table_names = [i for i in self.mongo[db_name].list_collection_names() if
                       table_name in i] if db_name in db_names else []
        if data.get('_id'): data.pop('_id')
        _table_names = ['%s_%s' % (table_name, i) for i in list(range(1, len(table_names) + 1))[::-1]]
        name = table_name + '_' + '1' if len(_table_names) == 0 else table_name + '_' + str(len(_table_names))
        if len(list(self.mongo[db_name][name].find({}))) < 2000:
            table = self.mongo[db_name][name]
        else:
            table = self.mongo[db_name][table_name + '_%s' % (len(table_names) + 1)]
        table.insert_one(data)
        return table

    def table(self, db_name=None, table_name=None):
        '''
        :param db_name: 数据库名称
        :param table_name: 表单名称
        :return: 不存在参数时，返回所有数据库名称，不存在表单时，返回指定数据库所有索引表名如：user_1 返回 user
                 参数都存在时，返回索引最后的一张表对象与表名
        '''
        if db_name == None:
            return '\t'.join(self.mongo.list_database_names())
        elif table_name == None:
            names = set([i.rsplit('_', 1)[0] for i in self.mongo[db_name].list_collection_names()])
            return list(names)
        else:
            table_names = [i for i in self.mongo[db_name].list_collection_names() if table_name in i]
            names = table_name + '_%s' % len(table_names)
            return self.mongo[db_name][names], names

    def find(self, db_name, table_name, key, value):
        '''
        :param db_name:数据库名称
        :param table_name: 表单名称
        :param key: 搜索的key
        :param value: 搜索的对应value
        :return:
        '''
        tables = (i for i in self.mongo[db_name].list_collection_names() if table_name in i)
        for _table_name in tables:
            for i in self.mongo[db_name][_table_name].find({}):
                if i.get(key) and i.get(key) == value:
                    return (
                        self.mongo[db_name][_table_name],
                        i
                    )
        else:
            return None

if __name__ == '__main__':
    m = Mongo(ip='45.76.48.170',password='Password_Alice',mongo_port=8001,mongo_username='root')
    for i in m.All_lis('users','All'):
        if i.get('email'):
            title = i.get('title')
            print(title)
        break