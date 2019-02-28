from collections import namedtuple
from rx import return_value
from rx.subjects import ReplaySubject
from rx.operators import filter, map, first, timeout
from homie.utils import topic_matches_sub

EVENT_MESSAGE = 'EVENT_MESSAGE'
TIMEOUT = 0.5

EVENT = namedtuple('Event', ['event', 'data'])
MESSAGE = namedtuple('Message', ['topic', 'payload', 'qos', 'retain'])


def _timout(duetime=TIMEOUT, value=None):
    return timeout(duetime, return_value(value))


class RxMqttBase:
    def __init__(self, default_qos=1, default_retain=True):
        self._default_qos = default_qos
        self._default_retain = default_retain
        self._events = ReplaySubject(window=TIMEOUT * 10)

    def publish(self, topic, payload, qos=None, retain=None):
        raise NotImplementedError()

    def subscribe(self, topic, qos=None):
        raise NotImplementedError()

    def message(self, topic, payload_only=False, pipes=[]):
        return self._observe(EVENT_MESSAGE).pipe(
            filter(lambda x: topic_matches_sub(topic, x.topic)),
            map(lambda x: x.payload if payload_only else x),
            *pipes
        )

    async def first_message(self, topic, payload_only=True, ttl=TIMEOUT):
        return await self.message(topic, payload_only=payload_only, pipes=[first(), _timout(ttl)])

    async def when_first_message(self, topic, payload, payload_only=True, ttl=TIMEOUT):
        return await self.message(topic, payload_only=payload_only, pipes=[
            filter(lambda x: x == payload if payload_only else x.payload == payload),
            first(),
            _timout(ttl)
        ])

    def _emit(self, event, data):
        self._events.on_next(EVENT(event=event, data=data))

    def _emit_message(self, topic, payload, qos, retain):
        self._emit(EVENT_MESSAGE, MESSAGE(topic=topic, payload=payload, qos=qos, retain=retain))

    def _observe(self, event):
        return self._events.pipe(filter(lambda x: x.event == event), map(lambda x: x.data))
