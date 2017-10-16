#coding:utf8

import os
import sys
import re
import subprocess
import time
import json
import urllib2
import socket


def run_cmd(cmd):
    '''
    执行 CMD 命令
    '''
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,env=os.environ.copy())
    pos = p.communicate()
    result = pos[0].decode('cp936').encode('utf-8')
    return result

'''
 1. 字符串不能包含“-”
 2. tags 中的 value 不能包含引号
'''
def predata(endpoint,metric,value,timestamp,step,vtype,tags=''):
    if endpoint == "":
        endpoint = socket.gethostname()
    i = {
        'Metric' : metric,
        'Endpoint': endpoint,
        'Timestamp': timestamp,
        'Step': step,
        'value': value,
        'CounterType': vtype,
        'TAGS': tags
        }
    return i


def postdata(pdata):
    # 上报
    url = "http://127.0.0.1:1988/v1/push"
    method = "POST"
    handler = urllib2.HTTPHandler()
    opener = urllib2.build_opener(handler)
    request = urllib2.Request(url, data=json.dumps(pdata))
    request.add_header('Content-Type','application/json')
    request.get_method = lambda: method
    try:
        connection = opener.open(request)
    except urllib2.HTTPError,e:
        connection = e

    if connection.code == 200:
        return 0,connection.read()
    else:
        return 1,'{"msg":"%s"}'%connection
