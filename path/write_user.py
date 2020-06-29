# coding=utf8
import requests
import re
from pyquery import PyQuery as pq
import time,random
import json
import redis
import sys

log = 'new.txt'
file = 'users.json'
table_name = 'role_lis'
user_name = 'users'
with open(file,'w') as f:
    f.write('')

A_lis = sys.argv

ip,pwd = A_lis[1].split('+')
r_db0 = redis.StrictRedis(host=ip,port=8002,db=0,password=pwd)
r_db1 = redis.StrictRedis(host=ip,port=8002,db=1,password=pwd)
r_db2 = redis.StrictRedis(host=ip,port=8002,db=2,password=pwd)
r_db3 = redis.StrictRedis(host=ip,port=8002,db=3,password=pwd)
r_db4 = redis.StrictRedis(host=ip,port=8002,db=4,password=pwd)

__lis = []

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
}

r_db4.incr('resp',amount=1)


def write_log(title):
    print(title)
    with open(log,'a') as f:
        f.write(title+'\n')

def write_file():
    global __lis
    with open(file,'w') as f:
        f.write(json.dumps(__lis))
    write_log('写入文件成功')

def post_file():
    with open(file,'r') as f:
        title = f.read().strip()
    if not title: return None
    lis = json.loads(title)
    for li in lis:
        r_db3.set(li['user'],json.dumps(li),xx=True)
    with open(file,'w') as f:
        f.write('')
    global __lis
    __lis.clear()
    write_log('上传文件成功,清楚本地缓存成功')

def ret_headers():
    global headers,__username
    __username = r_db1.lpop(user_name).decode('utf8')
    if not __username:return None
    r_db2.incr(user_name,amount=-1)
    headers['cookie'] = r_db0.get(__username).decode('utf8')
    return True

def get_user(user,num=1):
    global headers, __lis, __username, cookie, __table_name
    url = user['url']
    resp = requests.get(url, headers=headers)
    time.sleep(random.randint(1, 3))
    if resp.status_code == 200:
        All = pq(resp.text)
        if 'Login' not in All('title').text():
            fans = re.findall('og:description.*?(\d.*?)\sFollowers', resp.text, re.S)
            try:
                title = re.search('biography...(.*?)","blocked_by_viewer', resp.text, re.S).group(1)
            except Exception as err:
                write_log('re匹配模式失败,获取用户%s,失败' % user['user'])
                __lis.append(user)
                return True
            user['title'] = title
            user['fans'] = '|'.join(fans)
            user['email'] = '|'.join(re.findall(r'\w+@\w+.[com,cn,net]{1,3}', title))
            user['num'] = '|'.join(re.findall('\d{7,}', title, re.S))
            __lis.append(user)
            write_log('获取用户%s,成功' % user['user'])
            return True
        else:
            write_log('检测到需要登录,正在切换cookie')
            if not ret_headers():
                write_log('切换账号失败')
                return None
            return get_user(user,num+1)
    elif resp.status_code == 404:
        write_log('状态码' + str(resp.status_code) + ',获取用户%s,失败' % user['user'])
        __lis.append(user)
        return True
    elif resp.status_code == 429:
        write_log('账号:%s,被限制' % __username)
        write_log('已切换次数:%s'%num)
        write_log('正在进行上传')
        post_file()
        write_log('上传成功,等待20秒')
        time.sleep(20)
        write_log('正在切换cookie')
        if not ret_headers():
            write_log('切换账号失败')
            return None
        return get_user(user,num+1)

def run():
    ret_headers()
    __num = 5
    while 1 and __num:
        data = r_db1.lpop(table_name)
        if data == None:
            __num -= 1
            write_log('未获取任务，等待2秒')
            time.sleep(2)
            continue
        else:
            __num = 5
        dic = json.loads(data)
        write_log('获取任务用户:' + dic['user'])
        if not get_user(dic): break
        write_file()
        r_db2.incr(table_name, amount=-1)
        write_log('当前剩余:' + r_db2.get(table_name).decode('utf8'))
        write_log('当前客户端进程数量:%s'%r_db4.get('resp').decode('utf8'))
    write_file()
    post_file()
    write_log('任务获取完成')
    r_db4.incr('resp', amount=-1)

if __name__ == '__main__':
    run()