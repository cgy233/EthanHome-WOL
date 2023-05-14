# python3.9

import requests, re
import os, time
import threading
import schedule
import json
import configparser
from paho.mqtt import client as mqtt_client

requests.packages.urllib3.disable_warnings()


# WOL
bemfa_broker = ''
bemfa_port = 1883
bemfa_topic = ''
bemfa_client_id = ''

cookie = ''
webhook = ''

# 收到订阅的主题消息后，进行处理：开机/关机
def mqtt_handle(data):
    if "on" in data:
        print(os.system("python3 wol.py EthanPC"))
    elif "off" in data:
		# 休眠
        # print(os.system('ssh -n Ethan@192.168.2.23 "shutdown -h" > /dev/null 2>&1 &'))
		# 关机
        print(os.system('ssh -n Ethan@192.168.2.23 "shutdown -s -t 000" > /dev/null 2>&1 &'))

# 连接巴法MQTT服务器并订阅主题
def connect_bemfa() -> mqtt_client:
	def on_message_bemfa(client, userdata, msg):
		print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
		mqtt_handle(msg.payload.decode())
	def on_connect_bemfa(client, userdata, flags, rc):
		if rc == 0:
			print("Connected to Bemfa Broker!")
		else:
			print("Failed to connect, return code %d\n", rc)
		client.subscribe(topic=bemfa_topic, qos=1)
		client.on_message = on_message_bemfa
	client = mqtt_client.Client(client_id=bemfa_client_id, clean_session=False)
	client.on_connect = on_connect_bemfa
	client.connect(bemfa_broker, bemfa_port, keepalive=120)
	return client

# 钉钉机器人消息推送
def push_dingding(result, bean_count):
    # 定时任务触发钉钉报告推送
    key_word = "京豆"

    header = {
        "Content-Type": "application/json;charset=UTF-8"
    }
    message_body = {
        "msgtype": "markdown",
        "markdown": {
            "title": f"{result}, 京豆总数：{bean_count}",
            "text":  f"{result}, 京豆总数：{bean_count}"
        },
        "at": {
            "atMobiles": [],
            "isAtAll": False
        }
    }
    send_data = json.dumps(message_body)  # 将字典类型数据转化为json格式
    ChatBot = requests.post(url=webhook, data=send_data, headers=header)
    opener = ChatBot.json()
    if opener["errmsg"] == "ok":
        print(u"%s 通知消息发送成功！" % opener)
    else:
        print(u"通知消息发送失败，原因：{}".format(opener))

"""
返回请求头
:param cookie:
:param host:
:return:
"""
def get_headers(cookie, host):
    return {
        "Cookie": cookie,
        "Host": host,
        "Referer": "https://m.jd.com",
        "User-Agent": "okhttp/3.12.1;jdmall;android;version/10.3.4;build/92451;"
    }

"""
获取用户信息
:type cookie: str
:return: bool: 是否成功, str: 用户名, str: 用户金豆数量
"""
def get_user_info(cookie):
    try:
        url = "https://me-api.jd.com/user_new/info/GetJDUserInfoUnion"
        res = requests.get(url, headers=get_headers(cookie, "me-api.jd.com"), verify=False)
        if res.status_code == 200 and res.json()["msg"] == "success":
            return True, res.json()["data"]["userInfo"]["baseInfo"]["nickname"], res.json()["data"]["assetInfo"][
                "beanNum"]
        else:
            return False, None, None
    except:
        print("ERROR", "获取用户信息错误", traceback.format_exc())
        return False, None, None

"""
进行京东签到请求
:return: 成功、失败、已签到
"""
def _check_in():
    url = "https://api.m.jd.com/client.action?functionId=signBeanAct&body=%7B%22fp%22%3A%22-1%22%2C%22shshshfp%22%3A%22-1%22%2C%22shshshfpa%22%3A%22-1%22%2C%22referUrl%22%3A%22-1%22%2C%22userAgent%22%3A%22-1%22%2C%22jda%22%3A%22-1%22%2C%22rnVersion%22%3A%223.9%22%7D&appid=ld&client=apple&clientVersion=10.0.4&networkType=wifi&osVersion=14.8.1&uuid=3acd1f6361f86fc0a1bc23971b2e7bbe6197afb6&openudid=3acd1f6361f86fc0a1bc23971b2e7bbe6197afb6&jsonp=jsonp_1645885800574_58482";
    headers  = {"Connection":'keep-alive',
                "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
                "Cache-Control": 'no-cache',
                "User-Agent": "okhttp/3.12.1;jdmall;android;version/10.3.4;build/92451;",
                "accept": "*/*",
                "connection": "Keep-Alive",
                "Accept-Encoding": "gzip,deflate",
                # you only replace pt_key after 30 day and repalace your_pt_key 
                "Cookie": cookie
                }
    response = requests.post(url=url, headers=headers)
    # print(response.text)
    matchs = re.search(r'签到成功|签到失败|今天已签到', response.text, re.DOTALL)
    # print(matchs)
    return "签到失败" if matchs == None else matchs.group(0)

def jdbean_check_in():
	res = '签到失败'
	bean_count = 0
	try:
		res = _check_in()
		user_info = get_user_info(cookie)
		bean_count = user_info[2]
	except:
		print("HTTP GET ERROR")
	# print(f'{res}, 京豆总数: {user_info[2]}')
	push_dingding(res, bean_count)

# 京东签到任务
def task_check_in():
	schedule.every().day.at(f'08:50').do(jdbean_check_in)
	# schedule.every().day.at(f'00:32').do(jdbean_check_in)
	# schedule.every(1).minutes.do(jdbean_check_in)
	print('JDBean CheckIn Start Success.')
	while(True):
		schedule.run_pending()
		time.sleep(1)

# 巴法MQTT任务
def task_bemfa_wol():
	client_bemfa = connect_bemfa()
	client_bemfa.loop_forever()

if __name__ == '__main__':


	config = configparser.ConfigParser(interpolation=None)

	# 读取INI文件
	config.read('./config.ini')
	bemfa_broker = config.get('MQTT_CONFIG', 'bemfa_broker')
	bemfa_port = int(config.get('MQTT_CONFIG', 'bemfa_port'))
	bemfa_topic = config.get('MQTT_CONFIG', 'bemfa_topic')
	bemfa_client_id = config.get('MQTT_CONFIG', 'bemfa_client_id')

	cookie = config.get('DINGDING_ROBOT_JD_BEAN', 'cookie')
	webhook = config.get('DINGDING_ROBOT_JD_BEAN', 'webhook')

	# 京东签到测试
	# jdbean_check_in()
 
	# 巴法平台MQTT任务
	task_bemfa = threading.Thread(target=task_bemfa_wol, name='Bemfa_WOL')
	task_bemfa.start()
	task_bemfa.join()

	# 每日京东任务签到任务 默认关闭，需要开启自行配置钉钉机器人和京东cookie
	# task_jdbean = threading.Thread(target=task_check_in, name='JDBean_CheckIn')
	# task_jdbean.start()
	# task_jdbean.join()
