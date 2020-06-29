import sys,os,pickle
sys.path.append(os.getcwd())
from bin.role_users_lis import role_run,role_tags
from static.pro import *
from static.Mongo import Mongo
from static.Redis import Redis
from bin.Count_xls import write_xls
import time

m = Mongo(ip=ip,password=password,mongo_port=m_port,mongo_username=m_user)
r = Redis(ip=ip,password=password,redis_port=r_port)

def log_read(file):
    with open(file,'r') as f:
        f.seek(0,2)
        while 1:
            last_pos = f.tell()
            line = f.readline()
            if line:
                print(line,end='')
            else:
                time.sleep(1)

def get_tags():
    if input('是否运行后台python文件(y/n):') == 'y':
        files = [
            os.path.join(PATH,'tags',i) for i in os.listdir(os.path.join(PATH,'tags'))
        ]
        [os.remove(i) for i in files]
        os.system('nohup python3 bin/get_tags.py &')
    log_read('tags/logs.txt')

def post_tags():
    with open(os.path.join(PATH, 'tags', 'All.tags'),'rb+') as f:
        dic = pickle.loads(f.read())
    _lis = m.All_lis('tags','All','tag')
    print('当前存在tag数量:',len(_lis))
    print('文件数量:',len(dic))
    lis = []
    for n,i in enumerate(dic.keys(),1):
        if i not in _lis:
            print('>',end='')
            lis.append(dic[i])
            _lis.append(i)
    print('需要下发任务数量:',len(lis))
    role_tags(r,'tags',lis,input('是否覆盖原先任务(y/n):'))
    print('下发任务成功')
    num = len(lis)
    for n,i in enumerate(lis,1):
        if n % 1000 == 0: print('>', end='')
        m.insert('tags', 'All', i)
    print('入库操作成功')

def post_users():
    r_lis = r.keys(db=3)
    r._db = 3
    _r_db = r.redis
    m_lis = m.All_lis('users','All','user')
    print('当前存在用户数量:',len(m_lis))
    lis = []
    for i in r_lis:
        if i not in m_lis:
            lis.append(_r_db.get(i))
            m_lis.append(i)
        else:
            r.del_All(3,i)
    print('需添加任务数量:',len(lis))
    role_run(r,'users','role_lis',r.keys(0),lis)
    print('添加任务成功')

def Save_users():
    for n,i in enumerate(r.All_lis(3,'g_type'),1):
        m.insert('users','All',i)
        print('添加至mongo数量:',n)

def xls_email():
    with open(os.path.join(PATH,'static','user.txt'),'r') as f:
        __lis = [
            i for i in f.read().strip().split('\n') if i
        ]
    lis = [
        i for i in m.All_lis('users','All') if i.get('email') and i.get('user') not in __lis
    ]
    print('筛选成功,当前数量:',len(lis))
    write_xls(lis,os.path.join(os.getcwd(),'All.xls'))

if __name__ == '__main__':
    print('1.获取最近tag数据\n2.下发tag数据任务\n3.下发用户任务\n4.保存用户至mongo数据库\n5.导出所有email用户')
    while 1:
        count = input('>>')
        if count == '1':
            get_tags()
        elif count == '2':
            post_tags()
        elif count == '3':
            post_users()
        elif count == '4':
            Save_users()
        elif count == '5':
            xls_email()
        elif count == 'exit':
            break