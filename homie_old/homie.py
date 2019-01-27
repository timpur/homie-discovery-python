""" Homie Discovery module """

import logging

from .paho_mqtt_client_manager import (MQTTWrapper, MessageCallbackType)
from .tools import (constants, helpers, STAGE_1)
from .models import (HomieDevice)


_LOGGER = logging.getLogger(__name__)


class Homie(object):
    """
    Homie Discovery controller class

    Use `start` to start the discovery proccess
    """

    def __init__(self, mqtt: MQTTWrapper, discovery_prefix: str=None, qos: int=None, STATE_UNKNOWN=None):
        super().__init__()
        self.mqtt = mqtt
        self.discovery_prefix = discovery_prefix or constants.DEFAULT_DISCOVERY_PREFIX
        self.qos = qos or constants.DEFAULT_QOS

        self._homie_devices = dict()
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
            if supported and device_id not in self._homie_devices:
                homie_device = HomieDevice(device_base_topic, device_id)
                homie_device.add_on_discovery_stage_change(self._on_device_stage_change)
                homie_device.setup(self._subscribe, self._publish)
                self._homie_devices[device_id] = homie_device

        self._subscribe(f'{self.discovery_prefix}/+/$homie', _on_discovery_device, self.qos)

    def _on_device_stage_change(self, homie_device, state):
        if state == STAGE_1:
            for homie_node in homie_device.nodes:
                def _on_node_ready(homie_node, stage):
                    if self._on_node_discovery:
                        self._on_node_discovery(homie_node, stage)
                homie_node.add_on_discovery_stage_change(_on_node_ready)
                _on_node_ready(homie_node, homie_node.stage_of_discovery)

                for homie_property in homie_node.properties:
                    def _on_property_ready(homie_property, stage):
                        if self._on_property_discovery:
                            self._on_property_discovery(homie_property, stage)
                    homie_property.add_on_discovery_stage_change(_on_property_ready)
                    _on_property_ready(homie_property, homie_property.stage_of_discovery)

        if self._on_device_discovery:
            self._on_device_discovery(homie_device, state)

    @property
    def devices(self):
        """Return the list of discovered device."""
        return self._homie_devices.values()

    def get_device(self, device_id: str):
        """Return the list of discovered device."""
        return self._homie_devices[device_id]

    def has_device(self, device_id: str):
        """Return True if specific Device exists in the Homie Network."""
        return device_id in self._homie_devices

    def start(self):
        """Start the discovery proccess of a homie network"""
        _LOGGER.info(f"Homie has started discovering devices at {self.discovery_prefix}")
        self._discover_devices()

    def set_on_device_discovery(self, on_device_discovery):
        """ Set Listner for when a device has been discovered"""
        self._on_device_discovery = on_device_discovery

    def set_on_node_discovery(self, on_node_discovery):
        """ Set Listner for when a node has been discovered"""
        self._on_node_discovery = on_node_discovery

    def set_on_property_discovery(self, on_property_discovery):
        """ Set Listner for when a property has been discovered"""
        self._on_property_discovery = on_property_discovery
