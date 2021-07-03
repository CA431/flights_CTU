#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv,datetime,os
import time,random,re
import collections


#对代码共享航班进行合并
def covert_csv(inc_day):
    domestic_airports = set()
    international_airpots = set()
    f = open(os.path.join(os.getcwd(), 'CTU_config', 'domestic_airports.txt'),'rU')
    csvReader = csv.reader(f)
    for row in csvReader:
        airport = row[0]
        domestic_airports.add(airport)
    f.close()
    f = open(os.path.join(os.getcwd(), 'CTU_config', 'international_airports.txt'),'rU')
    csvReader = csv.reader(f)
    for row in csvReader:
        airport = row[0]
        international_airpots.add(airport)
    f.close()

    output_path = os.path.join(os.getcwd(), 'CTU_flight_table', '%s_all_flights.csv' % (inc_day))
    fw = open(output_path,'wb')
    header = ['flightNo','sharedFightNo','from','to','via','terminal','Arr/Dep','Dom/Int','schTime','status','inc_day']
    csvWriter = csv.DictWriter(fw,fieldnames=header)
    csvWriter.writeheader()

    #国际港澳台航班
    output_path2 = os.path.join(os.getcwd(), 'CTU_flight_table', '%s_international_flights.csv' % (inc_day))
    fw2 = open(output_path2,'wb')
    csvWriter2 = csv.DictWriter(fw2,fieldnames=header)
    csvWriter2.writeheader()

    flight_count = 0#执飞航班统计
    int_flight_count = 0#国际港澳台航班统计
    for attribute in ['D','A']:
        input_path = os.path.join(os.getcwd(), 'CTU_original_data', '%s_%s.csv' % (inc_day, attribute))
        f = open(input_path,'r')
        csvReader = csv.DictReader(f)
        data_dic = collections.OrderedDict()
        unknown_airport_set= set()#未知通航城市
        dup_flightNo_chk = {}  # 重复执飞航班检查

        for row in csvReader:
            key = '%s|%s|%s|%s|%s|%s'%(row['from'],row['to'],row['via'],row['schTime'],row['terminal'],row['status'])
            if key not in data_dic.keys():
                data_dic[key] = {}
                data_dic[key]['fightNo'] = row['flightNo']#[2:]
                data_dic[key]['sharedFightNo'] = []
                data_dic[key]['Dom/Int'] = ''
                # if row['from'].decode('utf-8') == u'\u6210\u90fd':#成都
                if attribute == 'D':
                    data_dic[key]['Arr/Dep'] = 'Departure'
                    if row['to'] in domestic_airports:
                        data_dic[key]['Dom/Int'] = '国内'
                    elif row['to'] in international_airpots:
                        data_dic[key]['Dom/Int'] = '国际港澳台'
                    else:
                        unknown_airport_set.add('%s\t%s'%(row['to'],row['flightNo']))

                # elif row['to'].decode('utf-8') == u'\u6210\u90fd':
                elif attribute == 'A':
                    data_dic[key]['Arr/Dep'] = 'Arrival'
                    if row['from'] in domestic_airports:
                        data_dic[key]['Dom/Int'] = '国内'
                    elif row['from'] in international_airpots:
                        data_dic[key]['Dom/Int'] = '国际港澳台'
                    else:
                        unknown_airport_set.add('%s\t%s'%(row['from'],row['flightNo']))#[2:]

                else:
                    data_dic[key]['Arr/Dep'] = 'UNKNOWN'
            else:
                data_dic[key]['sharedFightNo'].append(row['flightNo'])#[2:]
        f.close()


        for key in data_dic.keys():
            flight_count += 1
            row['from'],row['to'],row['via'],row['schTime'],row['terminal'],row['status'] = key.split('|')
            row['Arr/Dep'] = data_dic[key]['Arr/Dep']
            row['flightNo'] = data_dic[key]['fightNo']
            row['Dom/Int'] = data_dic[key]['Dom/Int']
            row['sharedFightNo'] = '|'.join(data_dic[key]['sharedFightNo'])
            row['inc_day'] = inc_day
            # for field in row.keys():
            #     row[field] = row[field].decode('utf-8').encode('gbk')
            csvWriter.writerow(row)
            if data_dic[key]['Dom/Int'] == '国际港澳台':
                int_flight_count += 1
                csvWriter2.writerow(row)

            if data_dic[key]['fightNo'] in dup_flightNo_chk.keys():
                print '%s 重复执飞\nfrom\tto\tArr/Dep\tschTime'%data_dic[key]['fightNo']
                print '%s\t%s\t%s\t%s'%(dup_flightNo_chk[data_dic[key]['fightNo']]['from'],
                                        dup_flightNo_chk[data_dic[key]['fightNo']]['to'],
                                        dup_flightNo_chk[data_dic[key]['fightNo']]['Arr/Dep'],
                                        dup_flightNo_chk[data_dic[key]['fightNo']]['schTime'])
                print '%s\t%s\t%s\t%s\n'%(row['from'],
                                        row['to'],
                                        row['Arr/Dep'],
                                        row['schTime'])
            else:
                dup_flightNo_chk[data_dic[key]['fightNo']] = {}
                dup_flightNo_chk[data_dic[key]['fightNo']]['from'] = row['from']
                dup_flightNo_chk[data_dic[key]['fightNo']]['to'] = row['to']
                dup_flightNo_chk[data_dic[key]['fightNo']]['Arr/Dep'] = row['Arr/Dep']
                dup_flightNo_chk[data_dic[key]['fightNo']]['schTime'] = row['schTime']

        if '' in unknown_airport_set:
            unknown_airport_set.remove('')
        if len(unknown_airport_set):
            print '发现 %d 个新通航城市（%s）'%(len(unknown_airport_set),attribute)
            for city in unknown_airport_set:
                print city
    print '%s\t成都双流机场执飞航班%d个 其中国际港澳台航班%d个'%(inc_day,flight_count,int_flight_count)
    fw.close()

def flightsCount():
    date = datetime.datetime(year=2020,month=3,day=19)
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    while True:

        ctu_count = 0
        pek_count = 0
        date = date + datetime.timedelta(days=1)
        if date > yesterday:
            break
        inc_day = date.strftime('%Y%m%d')
        try:
            ctu_path = os.path.join(os.getcwd(), 'CTU_flight_table', '%s_international_flights.csv' % (inc_day))
            f = open(ctu_path,'r')
            csvReader = csv.DictReader(f)
            for row in csvReader:
                ctu_count += 1
            f.close()

            pek_path_a = os.path.join(os.getcwd(), 'PEK_original_data', '%s_yesterday_fight_1.csv' % (inc_day))
            f = open(pek_path_a,'r')
            csvReader = csv.DictReader(f)
            for row in csvReader:
                pek_count += 1
            f.close()

            pek_path_d = os.path.join(os.getcwd(), 'PEK_original_data', '%s_yesterday_fight_0.csv' % (inc_day))
            f = open(pek_path_d,'r')
            csvReader = csv.DictReader(f)
            for row in csvReader:
                pek_count += 1
            f.close()

            print '%s\t成都双流机场执行航班%d个\t北京首都机场执行航班%d个\t %d'%(inc_day,ctu_count,pek_count,ctu_count - pek_count)
        except Exception as e:
            print '%s\t数据异常%s' % (inc_day, e)
    # output_path = os.path.join(os.getcwd(), 'CTU_flight_table', '%s_all_flights.csv' % (inc_day))


if __name__ == '__main__':
    inc_day = '%s' % (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')
    print 'Converting: %s' % inc_day
    covert_csv(inc_day)
    #
    # #货运航班判断：航班号白名单（控制台打印起讫点时间），航空公司白名单，航点白名单，国际经停国际，无代码共享。
    # flightsCount()