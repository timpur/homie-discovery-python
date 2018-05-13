import logging

from .paho_mqtt_client_manager import (MQTTWrapper, MessageCallbackType)
from .tools import (constants, helpers, STAGE_1, STAGE_2)
from .models import (HomieDevice, HomieNode)


_LOGGER = logging.getLogger(__name__)


class Homie(object):
    def __init__(self, mqtt: MQTTWrapper, discovery_prefix: str=None, qos: int=None, STATE_UNKNOWN=None):
        super().__init__()
        self.mqtt = mqtt
        self.discovery_prefix = discovery_prefix or constants.DEFAULT_DISCOVERY_PREFIX
        self.qos = qos or constants.DEFAULT_QOS

        self._DEVICES = dict()
        self._on_device_discovery = None
        self._on_node_discovery = None
        self._on_property_discovery = None

        if STATE_UNKNOWN is not None:
            constants.set_state_unknown(STATE_UNKNOWN)

    def _subscribe(self, topic: str, msg_callback: MessageCallbackType, qos: int=None):
        self.mqtt.subscribe(topic, msg_callback, qos or self.qos)

    def _publish(self, topic: str, payload: str, retain: bool=True, qos: int=None):
        self.mqtt.publish(topic, payload, qos or self.qos, retain)

    def _discover_devices(self):
        def _on_discovery_device(topic: str, payload: str, msg_qos: int):
            supported, device_base_topic, device_id = helpers.proccess_device(topic, payload)
            if supported and device_id not in self._DEVICES:
                device = HomieDevice(device_base_topic, device_id)
                device._add_on_discovery_stage_change(self._on_device_stage_change)
                device._setup(self._subscribe, self._publish)
                self._DEVICES[device_id] = device

        self._subscribe(f'{self.discovery_prefix}/+/$homie', _on_discovery_device, self.qos)

    def _on_device_stage_change(self, device, state):
        if state == STAGE_1:
            for node in device.nodes.values():
                def _on_node_ready(node, stage):
                    if self._on_node_discovery:
                        self._on_node_discovery(node, stage)
                node._add_on_discovery_stage_change(_on_node_ready)
                _on_node_ready(node, node._stage_of_discovery)

                for property in node.properties.values():
                    def _on_property_ready(property, stage):
                        if self._on_property_discovery:
                            self._on_property_discovery(property, stage)
                    property._add_on_discovery_stage_change(_on_property_ready)
                    _on_property_ready(property, property._stage_of_discovery)

        if self._on_device_discovery:
            self._on_device_discovery(device, state)

    @property
    def devices(self):
        """Return the list of discovered device."""
        return self._DEVICES.values()

    def start(self):
        _LOGGER.info(f"Homie has started discovering devices at {self.discovery_prefix}")
        self._discover_devices()

    def on_device_discovery(self, on_device_discovery):
        """ Set Listner for when a device has been discovered"""
        self._on_device_discovery = on_device_discovery

    def on_node_discovery(self, on_node_discovery):
        """ Set Listner for when a node has been discovered"""
        self._on_node_discovery = on_node_discovery

    def on_property_discovery(self, on_property_discovery):
        """ Set Listner for when a property has been discovered"""
        self._on_property_discovery = on_property_discovery
