from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import random
from pyquery import PyQuery as pq
import threading
import pickle
import os

PATH = os.path.dirname(os.path.dirname(__file__))

def write_log(title):
    print(title)
    with open(os.path.join(PATH,'tags','logs.txt'),'a') as f:
        f.write(time.strftime('%Y-%m-%d|%H:%M:%S ')+title+'\n')

def write_lis(lis,file):
    with open(os.path.join(PATH,'tags',file),'wb+') as f:
        f.write(pickle.dumps(lis))
    return True

def insert_one(inp,title):
    inp.send_keys(title)
    time.sleep(1.5)

def click_one(but):
    but.click()
    time.sleep(1)

def ret_driver():
    chrome_options = Options()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_argument('--headless')
    chrome_options.add_experimental_option('prefs',prefs)
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('chromedriver', chrome_options=chrome_options)
    return driver

def login(user='bj_ljc1',pwd='boomjoo'):
    write_log('正在登录账号%s'%user)
    driver = ret_driver()
    driver.get('https://www.instagram.com')
    time.sleep(2)
    inp = driver.find_elements_by_class_name('_2hvTZ')
    inp1 = inp[0]
    inp2 = inp[-1]
    insert_one(inp1,user)
    insert_one(inp2,pwd)
    but1 = driver.find_elements_by_class_name('sqdOP')[1]
    click_one(but1)
    time.sleep(10)
    return driver

def js_run(driver):
    jsCode = "var q=document.documentElement.scrollTop=200000"
    driver.execute_script(jsCode)
    time.sleep(random.randint(3,4))

def get_tag(driver,tags,user):
    def inner():
        All = pq(driver.page_source)
        _lis = [{'tag':i('a').attr('href')[3:-1],'top':tags} for i in All('.v1Nh3').items()]
        for i in _lis:
            if i['tag'] not in lis:
                lis[i['tag']] = i
        now_num = str(len(lis))
        write_log('当前获取帖子数量:'+now_num+' 用户:'+user)
        write_lis(lis,tags+'.dic')
        js_run(driver)
        return now_num
    lis = {}
    url = 'https://www.instagram.com/explore/tags/%s/'%tags
    driver.get(url)
    inner()
    num = 0
    times = 0
    while len(lis) < 5000:
        num1 = inner()
        if num != num1:
            num = num1
            times = 0
        else:
            times += 1
            time.sleep(1.1)
        if times >= 20:
            print('tags:',tags,'user:',user)
            break

def run(user,pwd,lis):
    def inner():
        driver = login(user,pwd)
        for tags in lis:
            get_tag(driver,tags,user)
        write_log('程序结束:'+user)
    t = threading.Thread(target=inner)
    t.start()
    return t

if __name__ == '__main__':
    with open(os.path.join(PATH, 'path', 'top_file.txt'), 'r') as f:
        _txt = f.read().strip()
    lis = [i[1:] for i in _txt.split('\n')]
    write_log(str(len(lis)))
    num = len(lis) // 2 + 1
    lis1 = lis[0:num]
    lis2 = lis[num:num * 2]
    write_log(str(len(lis1)) + str(len(lis2)))
    users = ['bj_ljc1', 'bj_ljc2']
    pwd = 'boomjoo'
    _lis = []
    _lis.append(run(users[0], pwd, lis1))
    _lis.append(run(users[1], pwd, lis2))
    for i in _lis:
        i.join()
    files = [
        os.path.join(PATH, 'tags', i) for i in os.listdir(os.path.join(PATH, 'tags')) if 'dic' in i
    ]
    dic = {}
    for file in files:
        with open(file, 'rb+') as f:
            _dic = pickle.loads(f.read())
            for _d in _dic:
                dic[_d] = _dic[_d]
    write_log(str(len(dic)))
    with open(os.path.join(PATH, 'tags', 'All.tags'), 'wb+') as f:
        f.write(pickle.dumps(dic))
    write_log('写入成功:%s' % os.path.join(PATH, 'tags', 'All.tags'))