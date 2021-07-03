#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2,json,csv,datetime,os
from bs4 import BeautifulSoup
import requests
import time,random,re
import collections

inc_day = None#要下载的昨天的数据的日期，例如20200317
attribute = None#A到港D出港
page_total = 0 #总页数

def http_request(page_num):
    global attribute,page_total
    url = 'http://www.cdairport.com/flightInfor.aspx?t=4&attribute=%s&time=-1&page=%d'%(attribute,page_num)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15"}
    request = urllib2.Request(url,headers = headers)
    response = urllib2.urlopen(request)
    rtn =  response.read()
    return rtn

def html_parse(csvWriter,html):
    global inc_day,page_total
    soup = BeautifulSoup(html, 'lxml')
    line = '%s' % soup.find(name='div', attrs={"id": "ctl00_ContentID_Pager"})
    # matchObj = re.search(r'\u5f53\u524d\u9875\uff1a[0-9]{1,2}/[0-9]{2}', line, re.M | re.I)
    matchObj = re.search(r'[0-9]{1,2}/[0-9]{2}', line, re.M | re.I)
    page_total = int(matchObj.group().split('/')[1])

    list = soup.find_all(name='table',attrs={"class": "arlineta departab"})#div class="mains"
    for tr in list[0].tbody.findAll('tr'):
        row = []
        for td in tr.findAll('td'):
            text = td.getText().replace('\n ','').replace('\n','').encode('utf-8')
            row.append(text)
        row.append(inc_day)
        csvWriter.writerow(row)




if __name__ == '__main__':

    inc_day = '%s' % (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')
    print 'Yesterday: %s' % inc_day
    for attribute in ['A','D']:

        print 'current attribute:%s'%attribute
        output_path = os.path.join(os.getcwd(), 'CTU_original_data', '%s_%s.csv' % (inc_day, attribute))
        if os.path.exists(output_path):
            raise Exception('path exits:%s'%output_path)
        fw = open(output_path,'wb')
        csvWriter = csv.writer(fw)
        row = ['flightNo','from','to','via','schTime','terminal','status','inc_day']
        csvWriter.writerow(row)
        fw.close()

        fw = open(output_path,'ab+')
        csvWriter = csv.writer(fw)
        for i in range(1,150):
            reconnect_count = 0
            while True:
                try:
                    print 'current page:%d/%d' % (i,page_total)
                    html = http_request(i)
                    break
                except Exception as e:
                    reconnect_count += 1
                    sleep_time = 600 + 300 * reconnect_count * reconnect_count
                    sleep_time = 30
                    print 'reconnect(%d times) after %d mins\nhttp_request_error_%s'%(reconnect_count,sleep_time / 60,e)
                    time.sleep(sleep_time)
            # html = http_request(i)
            html_parse(csvWriter,html)
            if i == page_total:
                print '%d pages downloaded in total!'%page_total
                break
            else:
                # time.sleep(random.randint(150,180))
                time.sleep(random.randint(5, 8))

        fw.close()

    #测试
    # f = open('html.txt','r')
    # html = f.read()
    # html_parse(None,html)
    # f.close()


