#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import json
import requests
import sys
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")

http_proxy  = "http://127.0.0.1:8080"
https_proxy = "http://127.0.0.1:8080"
ftp_proxy   = "ftp://10.10.1.10:3128"
proxyDict = { 
              "http"  : http_proxy, 
              "https" : https_proxy, 
              "ftp"   : ftp_proxy
            }

API_MSDN_INDEX = 'https://msdn.itellyou.cn/'

API_INDEX = 'https://msdn.itellyou.cn/Index/GetCategory'

API_GET_LANG = 'https://msdn.itellyou.cn/Index/GetLang'

API_GET_LIST = 'https://msdn.itellyou.cn/Index/GetList'

API_GET_PRODUCT = 'https://msdn.itellyou.cn/Index/GetProduct'

class headers:
    headers = {
        'Referer':'https://msdn.itellyou.cn/',
        'Origin':'https://msdn.itellyou.cn'
        }

RESULT = {'data':[]} 
def get_product(id):
    r = requests.post(API_GET_PRODUCT, headers=headers.headers, data={'id':id},proxies=proxyDict,verify=False)
    updateDcookie(r)
    if r.status_code == 200:
            item = r.json().get('result')
            print('FileName:%s' % item.get('filename'))
            print('PostDate:%s' % item.get('postdatestring'))
            print('SHA1:%s' % item.get('sha1'))
            print('size:%s' % item.get('size'))
            print('Download:%s' % item.get('download'))
            return item


def get_list(id, lang_id):
    r = requests.post(API_GET_LIST, headers=headers.headers, data={'id':id, 'lang':lang_id, 'filter':'true'},proxies=proxyDict,verify=False)
    updateDcookie(r)
    if r.status_code == 200:
        product_list = []
        for item in r.json().get('result'):
            product_info = get_product(item.get('id'))
            product_list.append(product_info)
        return product_list

def get_lang(id):
    #id='a65ac350-170b-41b1-937d-08dda76cc4bf'
    r = requests.post(API_GET_LANG, headers=headers.headers, data={'id':id},proxies=proxyDict,verify=False)
    updateDcookie(r)
    if r.status_code == 200:
            lang_list = []
            for lang in r.json().get('result'):
                print(lang.get('lang'))
                info = {'lang':lang.get('lang'), 'product_list':get_list(id,lang.get('id'))}
                lang_list.append(info)
            return lang_list


def get_download_list(category_id):
    r = requests.post(API_INDEX, headers=headers.headers, data={'id':category_id},proxies=proxyDict,verify=False)
    updateDcookie(r)
    if r.status_code == 200:
            for item in r.json():
                print('System Name: %s'% item.get('name'))
                system_info = get_lang(item.get('id'))
                system_info = {'name':item.get('name'), 'lang_list':system_info}
                RESULT['data'].append(system_info)
            print('finishied!!!')
            return RESULT

def updateDcookie(r):
    a=r.content.decode()
    a=re.findall('(data-token=.*?)>',a)
    #print(headers.headers)
    #print(a)
    try:
        _,v=a[0].split('=')
        if v:
            print('d_cookie is :::',v)
            headers.headers['X-CSRF-TOKEN']=v
    #        print(headers.headers)
    except:pass


if __name__ == '__main__':
    requests=requests.session()
    r=requests.get(API_MSDN_INDEX)
    updateDcookie(r)
    json_buffer = get_download_list('7AB5F0CB-7607-4BBE-9E88-50716DC43DE6')
    with open('./msdn.json','w') as f:
        json.dump(json_buffer,f)
