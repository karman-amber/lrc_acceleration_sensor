# author: zuohuaiyu
# date: 2024/10/15 9:10
import paho.mqtt.client as mqtt
import time
import paho.mqtt.client as mqtt
import random
import time

# MQTT broker settings
broker_address = "172.8.8.229"  # 替换为你的MQTT broker地址
broker_port = 1883  # 默认的MQTT端口


# 创建MQTT客户端实例
client = mqtt.Client()

# 连接到MQTT broker
client.connect(broker_address, broker_port)

try:
    while True:
        # 发布随机数到指定的主题
        client.publish("lrc/sensor/x", str(random.uniform(0, 1)))
        client.publish("lrc/sensor/y", str(random.uniform(0, 1)))
        client.publish("lrc/sensor/z", str(random.uniform(0, 1)))
        client.publish("lrc/sensor/r", str(random.uniform(0, 1)))

        # 等待10毫秒
        time.sleep(0.01)

except KeyboardInterrupt:
    print("程序被用户中断")
finally:
    # 断开与MQTT broker的连接
    client.disconnect()
    print("已断开与MQTT broker的连接")