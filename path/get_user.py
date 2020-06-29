# coding=utf8
import random
import sys
import requests
import time
import re
import redis
import json

A_lis = sys.argv

ip,pwd = A_lis[1].split('+')
r_db1 = redis.StrictRedis(host=ip,port=8002,db=1,password=pwd)
r_db2 = redis.StrictRedis(host=ip,port=8002,db=2,password=pwd)
r_db3 = redis.StrictRedis(host=ip,port=8002,db=3,password=pwd)

file = 'file.json'
log = 'log.txt'
with open(file,'w') as f:
    f.write('')

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
}

__lis = []

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
        lis = json.loads(f.read())
    for li in lis:
        if not li.get('user'):continue
        r_db3.set(li['user'],json.dumps(li),nx=True)
    with open(file,'w') as f:
        f.write('')
    global __lis
    __lis.clear()
    write_log('上传文件成功,清楚本地缓存成功')

def get_tag(tag,num=1):
    global __lis
    if num > 20: return None
    com = re.compile('id...(.*?)".*?username...(.*?)"')
    _url = 'https://www.instagram.com/graphql/query/?query_hash=6ff3f5c474a240353993056428fb851e&variables=%7B%22shortcode%22%3A%22' + \
           tag['tag'] + '"%2C"include_reel"%3Atrue%2C"include_logged_out"%3Afalse%7D'
    resp = requests.get(_url, headers=headers)
    time.sleep(random.randint(1,3))
    if resp.status_code == 200:
        try:
            id, user = com.search(resp.text).groups()
            tag['id'] = id
            tag['user'] = user
            tag['url'] = 'https://www.instagram.com/' + user + '/'
            tag['g_type'] = 'true'
            write_log('获取用户:%s,成功' % user)
            __lis.append(tag)
        except Exception:
            write_log(_url)
            write_log('https://www.instagram.com/p/' + tag['tag'] + ' 判定不存在')
        return True
    elif resp.status_code == 429:
        write_log('当前检测到跳转，自动等待30秒')
        time.sleep(30)
        post_file()
        __lis.clear()
        write_file()
        return get_tag(tag, num + 1)
    else:
        write_log('当前状态码:%s' % resp.status_code)
        return True

def run():
    while 1:
        data = r_db1.lpop('tags')
        if data == None:break
        dic = json.loads(data)
        write_log('获取任务tag:'+dic['tag'])
        if not get_tag(dic):break
        write_file()
        r_db2.incr('tags',amount=-1)
        write_log('当前剩余:'+r_db2.get('tags').decode('utf8'))
    write_file()
    post_file()
    write_log('任务获取完成')

if __name__ == '__main__':
    run()