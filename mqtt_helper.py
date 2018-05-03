# Imports
import asyncio
import attr
import logging
import socket
import time
import re
from operator import attrgetter
from itertools import groupby
import paho.mqtt.client as mqtt


# Types
from typing import Optional, Any, Union, Callable, List, cast
from paho.mqtt.client import Client as MQTTClient
PublishPayloadType = Union[str, bytes, int, float, None]
SubscribePayloadType = Union[str, bytes]  # Only bytes if encoding is None
MessageCallbackType = Callable[[str, SubscribePayloadType, int], None]

# Consts
MAX_RECONNECT_WAIT = 300  # seconds
_LOGGER = logging.getLogger(__name__)


@attr.s(slots=True, frozen=True)
class Subscription(object):
    """Class to hold data about an active subscription."""

    topic = attr.ib(type=str)
    callback = attr.ib(type=MessageCallbackType)
    qos = attr.ib(type=int, default=0)
    encoding = attr.ib(type=str, default='utf-8')


class MQTT():
    """MQTT client wrapper."""

    def __init__(self, mqtt_client: MQTTClient):
        self.client = mqtt_client  # type: MQTTClient
        self.subscriptions = []  # type: List[Subscription]
        self._lock = asyncio.Lock()

        self.client.on_connect = self._mqtt_on_connect
        self.client.on_disconnect = self._mqtt_on_disconnect
        self.client.on_message = self._mqtt_on_message

    async def async_publish(self, topic: str, payload: PublishPayloadType, qos: int, retain: bool) -> None:
        """Publish a MQTT message. This method must be run in the event loop and returns a coroutine."""

        async with self._lock:
            self.client.publish(topic, payload, qos, retain)

    async def async_subscribe(self, topic: str, msg_callback: MessageCallbackType, qos: int, encoding: str) -> Callable[[], None]:
        """Set up a subscription to a topic with the provided qos.This method is a coroutine."""

        if not isinstance(topic, str):
            raise Exception("topic needs to be a string!")

        subscription = Subscription(topic, msg_callback, qos, encoding)
        self.subscriptions.append(subscription)

        self._perform_subscription(topic, qos)

        def async_remove() -> None:
            """Remove subscription."""
            if subscription not in self.subscriptions:
                raise Exception("Can't remove subscription twice")
            self.subscriptions.remove(subscription)

            if any(other.topic == topic for other in self.subscriptions):
                # Other subscriptions on topic remaining - don't unsubscribe.
                return
            await self._async_unsubscribe(topic)

        return async_remove

    def _perform_subscription(self, topic: str, qos: int) -> None:
        """Perform a paho-mqtt subscription."""

        _LOGGER.debug(f"Subscribing to {topic}")

        with (yield from self._lock):
            result = self.client.subscribe(topic, qos)
            _raise_on_error(result)

    async def _async_unsubscribe(self, topic: str) -> None:
        """Unsubscribe from a topic. This method is a coroutine."""

        async with self._lock:
            result = self.client.unsubscribe(topic)
            _raise_on_error(result)

    def _mqtt_on_message(self, _mqttc, _userdata, msg) -> None:
        """Message received callback."""

        _LOGGER.debug("Received message on %s: %s", msg.topic, msg.payload)

        for subscription in self.subscriptions:
            if not _match_topic(subscription.topic, msg.topic):
                continue

            payload = msg.payload  # type: SubscribePayloadType
            if subscription.encoding is not None:
                try:
                    payload = msg.payload.decode(subscription.encoding)
                except (AttributeError, UnicodeDecodeError):
                    _LOGGER.warning("Can't decode payload %s on %s with encoding %s",
                                    msg.payload, msg.topic,
                                    subscription.encoding)
                    continue

            subscription.callback(msg.topic, payload, msg.qos)

    def _mqtt_on_connect(self, _mqttc, _userdata, _flags, result_code: int) -> None:
        """On connect callback. Resubscribe to all topics we were subscribed to and publish birth message."""

        import paho.mqtt.client as mqtt

        if result_code != mqtt.CONNACK_ACCEPTED:
            _LOGGER.error('Unable to connect to the MQTT broker: %s',
                          mqtt.connack_string(result_code))
            self.client.disconnect()
            return

        # Group subscriptions to only re-subscribe once for each topic.
        keyfunc = attrgetter('topic')
        for topic, subs in groupby(sorted(self.subscriptions, key=keyfunc), keyfunc):
            # Re-subscribe with the highest requested qos
            max_qos = max(subscription.qos for subscription in subs)
            self._perform_subscription(topic, max_qos)

    def _mqtt_on_disconnect(self, _mqttc, _userdata, result_code: int) -> None:
        """Disconnected callback."""
        # When disconnected because of calling disconnect()
        if result_code == 0:
            return

        tries = 0

        while True:
            try:
                if self.client.reconnect() == 0:
                    _LOGGER.info("Successfully reconnected to the MQTT server")
                    break
            except socket.error:
                pass

            wait_time = min(2**tries, MAX_RECONNECT_WAIT)
            _LOGGER.warning(
                "Disconnected from MQTT (%s). Trying to reconnect in %s s",
                result_code, wait_time)
            # It is ok to sleep here as we are in the MQTT thread.
            time.sleep(wait_time)
            tries += 1


def _raise_on_error(result_code: int) -> None:
    """Raise error if error result."""

    if result_code != 0:
        raise Exception(
            f'Error talking to MQTT: {mqtt.error_string(result_code)}')


def _match_topic(subscription: str, topic: str) -> bool:
    """Test if topic matches subscription."""

    reg_ex_parts = []  # type: List[str]
    suffix = ""
    if subscription.endswith('#'):
        subscription = subscription[:-2]
        suffix = "(.*)"
    sub_parts = subscription.split('/')
    for sub_part in sub_parts:
        if sub_part == "+":
            reg_ex_parts.append(r"([^\/]+)")
        else:
            reg_ex_parts.append(re.escape(sub_part))

    reg_ex = "^" + (r'\/'.join(reg_ex_parts)) + suffix + "$"

    reg = re.compile(reg_ex)

    return reg.match(topic) is not None
