from paho.mqtt.client import MQTT_ERR_SUCCESS
from rx import return_value
from rx.operators import first, timeout
from homie.adapters.mqtt.base import RxMqttBase, EVENT, EVENT_MESSAGE, TIMEOUT
from homie.utils import data_down, data_up


EVENT_ACK_PUBLISH = 'EVENT_ACK_PUBLISH'
EVENT_ACK_SUBSCRIBE = 'EVENT_ACK_SUBSCRIBE'


class RxPaho(RxMqttBase):
    def __init__(self, client, **kargs):
        super().__init__(**kargs)
        self._client = client
        client.on_publish = self._on_publish
        client.on_subscribe = self._on_subscribe
        client.on_message = self._on_message

    async def publish(self, topic, payload, qos=None, retain=None):
        qos = qos if qos is not None else self._default_qos
        retain = retain if retain is not None else self._default_retain
        payload = data_down(payload)
        res = self._client.publish(topic, payload, qos, retain)
        if res.rc == MQTT_ERR_SUCCESS:
            return await self.ack_publish(res.mid)
        return False

    async def subscribe(self, topic, qos=None):
        qos = qos if qos is not None else self._default_qos
        if isinstance(topic, list):
            topic = list(map(lambda x: (x, qos), topic))
        res, mid = self._client.subscribe(topic, qos)
        if res == MQTT_ERR_SUCCESS:
            return await self.ack_subscription(mid)
        return False

    async def ack_publish(self, mid):
        res = await self._observe(EVENT_ACK_PUBLISH).pipe(
            first(lambda x: x == mid),
            timeout(TIMEOUT, return_value(None))
        )
        return True if res else False

    async def ack_subscription(self, mid):
        res = await self._observe(EVENT_ACK_SUBSCRIBE).pipe(
            first(lambda x: x == mid),
            timeout(TIMEOUT, return_value(None))
        )
        return True if res else False

    def _on_message(self, _, __, mes):
        # print("On Message", mes.topic)
        self._emit_message(mes.topic, data_up(mes.payload), mes.qos, mes.retain)

    def _on_publish(self, _, __, mid):
        # print("ack", mid)
        self._emit(EVENT_ACK_PUBLISH, mid)

    def _on_subscribe(self, _, __, mid, ___):
        # print("ack", mid)
        self._emit(EVENT_ACK_SUBSCRIBE, mid)
