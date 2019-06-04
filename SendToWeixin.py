#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: zhoubin
# Date: 2019/6/4
# Description:

import requests
import json
import sys


# 企业号及应用相关信息
corp_id = 'wwa755402ee703c9f7'
corp_secret = 'VWpsnfNokKVMF359U8d0ZPXBci1YNNFjYlDaGtpyxpk'
agent_id = '1000002'

# 存放 access_token
file_path = '/tmp/access_token.log'


def get_access_token_from_file():
    """ 从文件获取 access_token """
    try:
        with open(file_path, 'r') as f:
            this_access_token = f.read()
            print('get success {0}'.format(this_access_token))
            return this_access_token
    except Exception as e:
        print(e)


def get_access_token():
    """ 获取 access_token """
    get_token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={0}&corpsecret={1}'.format(corp_id, corp_secret)
    response = requests.get(get_token_url)
    result_json = response.json()
    access_token = result_json['access_token']
    print(access_token)
    try:
        with open(file_path, 'w') as f:
            f.write(access_token)
    except Exception as e:
        print(e)

    return access_token


def main():
    flag = True
    while(flag):
        access_token = get_access_token_from_file()
        try:
            to_user = "@all"
            message = sys.argv[3]
            send_message_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={0}'.format(access_token)
            message_params = {
                "touser": to_user,
                "msgtype": "text",
                "agentid": agent_id,
                "text": {
                    "content": message
                },
                "safe": 0
            }
            r = requests.post(send_message_url, data=json.dumps(message_params))
            print('post success {0}'.format(r.text))
            result_json = r.json()
            errmsg = result_json['errmsg']
            if errmsg != 'ok':
                raise OSError('发送信息失败')
            flag = False
        except Exception as e:
            print(e)
            access_token = get_access_token()


if __name__ == '__main__':
    main()
