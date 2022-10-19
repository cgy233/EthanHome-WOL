# python3.6

import random
import os

from paho.mqtt import client as mqtt_client


broker = 'bemfa.com'
port = 9501
topic = "ethanpc002"
# 巴法平台控制台获取的私钥
client_id = ''

def mqtt_handle(data):
    if "on" in data:
        print(os.system("python wol.py EthanPC"))
    elif "off" in data:
        print(os.system('ssh Ethan@192.168.2.23 "shutdown -s -t 0"'))

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        mqtt_handle(msg.payload.decode())

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
