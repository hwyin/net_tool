#!/usr/bin/python
# encoding: utf-8
# -*- coding: utf8 -*-
"""
Created by PyCharm.
File:               LinuxBashShellScriptForOps:odbp_database.py.py
User:               Yinweihai
Create Date:        2017/4/17
Create Time:        17:30
"""
import json
import Corp_Config


class WeiXinSendMsgClass(object):
    def __init__(self):
        self.access_token = ""
        self.to_user = ""
        self.to_party = ""
        self.to_tag = "1"
        self.msg_type = "text"
        self.agent_id = 1
        self.content = ""
        self.safe = 0
        self.data = {
            "touser": self.to_user,
            "toparty": self.to_party,
            "totag": self.to_tag,
            "msgtype": self.msg_type,
            "agentid": self.agent_id,
            "text": {
                "content": self.content
            },
            "safe": self.safe
        }

    def send(self, content):
        import urllib.request
        if content is not None:
            self.data['text']['content'] = content
        else:
            print
            raise RuntimeError
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.gettoken()
        jdata = json.dumps(self.data).encode('UTF-8')
        print(jdata)
        response = urllib.request.urlopen(url, jdata)

        return_content = json.loads(response.read())
        if return_content["errcode"] == 0 and return_content["errmsg"] == "ok":
            print("Send successfully! %s " % return_content)
        else:
            print("Send failed! %s " % return_content)

    def gettoken(self):
        import urllib.error
        corpid = Corp_Config.Corp_Config.CORPID
        corpsecret = Corp_Config.Corp_Config.CORPSECRET
        gettoken_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=' + corpid + '&corpsecret=' + corpsecret
        token = ""
        try:
            response = urllib.request.urlopen(gettoken_url)
            token_json = json.loads(response.read().decode("utf8"))
        except Exception  as e:
            print(e)

        return token_json["access_token"]

# if __name__ == '__main__':
#    msg = WeiXinSendMsgClass()
#    msg.send("msg_send")
