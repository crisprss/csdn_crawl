#coding=utf-8
import re
import requests
import pymysql
from bs4 import BeautifulSoup
from lxml import etree
import time


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
}


def get_data(url):
    res = requests.get(url,headers=headers)
    html_csdn = res.text
    # to crawl csdn data including these:
    read_num = str(etree.HTML(html_csdn).xpath('//*[@id="asideProfile"]/div[2]/dl[5]/dt/span/text()')[0])
    fans_num = str(etree.HTML(html_csdn).xpath('//*[@id="fan"]/text()')[0])
    likes_num = str(etree.HTML(html_csdn).xpath('//*[@id="asideProfile"]/div[2]/dl[3]/dt/span/text()')[0])
    author = str(etree.HTML(html_csdn).xpath('//*[@id="uid"]/span/@username')[0]).replace(" ","").replace("\n","")
    comment_num = str(etree.HTML(html_csdn).xpath('//*[@id="asideProfile"]/div[2]/dl[4]/dt/span/text()')[0])
    return {"userID":author,"read_num":read_num,"fans_num":fans_num,"likes_num":likes_num,"comment_num":comment_num,"url":url}





def connect():
    #connect database
    conn = pymysql.connect(
        host = 'localhost',
        port = 3306,
        user = 'root',
        password = 'root',
        database = 'data',
        charset = 'utf8mb4'
    )
    #Get a cursor object that can execute SQL statements
    cursor = conn.cursor()
    return {"conn":conn,"cursor":cursor}

connection = connect()
conn = connection['conn']
cursor = connection['cursor']

#insert data into database
def sqlinsert():
    sql_insert = "insert into CSDN(userID,read_num,fans_num,likes_num,comment_num) values ('{userID}','{read_num}','{fans_num}','{likes_num}','{comment_num}');".format(**data)
    cursor.execute(sql_insert)
    conn.commit()

# judge if url is valid and not repeated
def continue_crawl(url_list,max_steps=5):
    if(len(url_list) > max_steps):
        print("already crawl so many~")
        return False
    elif(url_list[-1] in url_list[:-1]):
        print("already crawl it!")
        return False
    else:
        return True

all_url = []

# get next url and put it in list
def get_url(url):
    res = requests.get(url,headers=headers)
    html = res.text
    all_url = re.findall('<.*?href="(https://blog.csdn.net.*?)".*?',html)
    return all_url[-4]

# all you need change is here ,change the first url in url_list
url_list = ['https://blog.csdn.net/crisprx/article/details/107048541']


while continue_crawl(url_list,20):
    data = get_data(url_list[-1])
    sqlinsert()
    next_url = get_url(url_list[-1])
    url_list.append(next_url)
    print(url_list[-1])
    time.sleep(2)

cursor.close()
conn.close()
