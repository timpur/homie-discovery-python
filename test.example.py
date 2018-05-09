import logging
import paho.mqtt.client as mqtt
from paho_mqtt_client_manager import MQTTWrapper
from homie import Homie

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)


client = mqtt.Client('python_client')
client_wrapper = MQTTWrapper(client)

client.username_pw_set("username", "password")
client.connect("iot.hostname.com", 1883, 60)

Homie(client_wrapper, "homie", 1)

client.loop_forever()
