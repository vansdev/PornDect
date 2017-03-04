# -*- coding: UTF-8 -*-
# python 版本 3.4
# 多线程百度图片下载器  将图片下载到pics文件夹下 供PornDect处理
# 用concurrent模块实现
# 先多线程获取所有页面的图片url 再多线程下载所有图片
# 缺少伪装机制 下多了被百度封

import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor , as_completed
import requests
import re
from multiprocessing import Manager

import time
from PIL import Image
from io import BytesIO
pic_url_set = set()
pattern = re.compile(r'\"objURL\":\"(.*?)\",')
MAX_THREADS = 8

def get_pic_urls(page_url):
    global pic_url_set
    try:
        r = requests.get(page_url)
    except requests.ConnectionError:
        return None
    src = r.text
    pic_url_list = re.findall(pattern, src)
    for url in pic_url_list:
        pic_url_set.add(url)

def multi_thread_controller1(keyword, total_page_num):
    global pic_url_set
    page_urls = []
    for i in range(total_page_num):
        # use keyword and page_num to construct page_url
        page_str = str(i * 2)
        page_url = 'https://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word=' \
                   + keyword + '&pn=' \
                   + page_str + '0&gsm=3c'
        page_urls.append(page_url)

    print('length of page_urls is {}.'.format(len(page_urls)))
    # for page_url in page_urls:
    #     print(page_url)
    futures = set()
    with ThreadPoolExecutor(os.cpu_count()) as executor:
        for page_url in page_urls:
            future = executor.submit(get_pic_urls, page_url)
            futures.add(future)

    try:
        for future in as_completed(futures):
            err = future.exception()
            if err is not None:
                raise err
    except KeyboardInterrupt:
        print("stopped by hand")

def t_download(pic_url):
    try:
        pr = requests.get(pic_url, timeout=60)
        pic = Image.open(BytesIO(pr.content))
        pic.save('./pics/' + str(hash(pr.content)) + '.jpg')
    except Exception:
        return None



def multi_thread_controller2():
    global pic_url_set
    futures = set()
    with ThreadPoolExecutor(MAX_THREADS) as executor:
        for pic_url in pic_url_set:
            future = executor.submit(t_download, pic_url)
            futures.add(future)
    try:
        for future in as_completed(futures):
            err = future.exception()
            if err is not None:
                raise err
    except KeyboardInterrupt:
        print("stopped by hand")


def main():

    keyword = input('input pic search keyword: ')
    total_page_num = int(input('input total number of pages to download: '))

    start = time.clock()
    multi_thread_controller1(keyword, total_page_num)
    print('size of pic_url_set is {}.'.format(len(pic_url_set)))
    multi_thread_controller2()
    finish = time.clock()
    print('total execute time: {}'.format(finish - start))


if __name__ == '__main__':
    main()