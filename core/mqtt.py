# author: zuohuaiyu
# date: 2024/9/26 8:47
import queue

from paho.mqtt import client
import random
import threading
from core.utils import debug

TOPIC = "lrc/vibration"
mqtt_client = None


def on_connect(client2, userdata, flags, rc):
    if rc == 0:
        debug(f"{client2._client_id.decode()} Connected to MQTT Broker!")
    else:
        debug(f"Failed to connect, return code {rc}")


# def on_publish(client2, userdata, mid):
#     debug(f"{client2._client_id.decode()}'s Message published to topic")


def on_message(client2, userdata, msg):
    debug(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")


class MqttClient:
    def __init__(self):
        self.mqtt_client = None
        self.topic = TOPIC
        self.id = f"lrc{int(random.random() * 10000)}"
        self.status = "offline"
        self.thread = None
        self.queue = queue.Queue()

    def connect(self, ip, port, user=None, password=None):
        if self.mqtt_client is None:
            try:
                self.mqtt_client = client.Client(self.id)
                if user is not None:
                    self.mqtt_client.username_pw_set(user, password)
                self.mqtt_client.connect(ip, port, 60)
                self.mqtt_client.on_connect = on_connect
                self.mqtt_client.on_message = on_message
                # self.mqtt_client.on_publish = on_publish
                self.status = "online"
            except Exception as ex:
                debug(ex)
                self.status = "offline"

    def is_online(self):
        return self.status == "online"

    def publish(self, message, topic=None):
        if self.is_online():
            if topic is None:
                topic = TOPIC
            try:
                self.mqtt_client.publish(topic, message)
                return True
            except Exception as ex:
                debug(ex)
        else:
            debug("无法发送消息，MQTT客户端未连接")
        return False

    def start_subscribe(self, topic=None, queue_max_count=100):
        if self.thread is None:
            if topic is None:
                topic = self.topic
            self.mqtt_client.subscribe(topic)

            def on_message2(client2, userdata, msg):
                if self.queue.qsize() >= queue_max_count:
                    self.queue.get(block=False)
                self.queue.put(msg.payload.decode())

            self.mqtt_client.on_message = on_message2

            self.thread = threading.Thread(target=self.mqtt_client.loop_start())
            self.thread.start()

    def stop_subscribe(self):
        if self.thread is not None:
            self.mqtt_client.unsubscribe(TOPIC)
            self.mqtt_client.loop_stop()
            self.thread.join()
            self.thread = None


if __name__ == '__main__':
    client1 = MqttClient()
    client1.connect("127.8.8.229", 1883)
    client1.start_subscribe()
    client1.publish("Hello, MQTT!")
    client1.publish("Hello, MQTT2!")
    client1.publish("Hello, MQTT3!")
    client1.stop_subscribe()
