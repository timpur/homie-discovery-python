import logging
from .homie_discovery_base import (HomieDiscoveryBase, STAGE_0, STAGE_1, STAGE_2)
from .constants import STATE_UNKNOWN
from . import helpers
from .homie_node import HomieNode

_LOGGER = logging.getLogger(__name__)


class HomieDevice(HomieDiscoveryBase):
    # A definition of a Homie Device
    def __init__(self, base_topic: str, device_id: str):
        super().__init__()
        _LOGGER.info(f"Homie Device Discovered. ID: {device_id}")
        self._base_topic = base_topic
        self._device_id = device_id
        self._prefix_topic = f'{base_topic}/{device_id}'

        self._nodes = dict()

        self._convention_version = STATE_UNKNOWN
        self._online = STATE_UNKNOWN
        self._name = STATE_UNKNOWN
        self._ip = STATE_UNKNOWN
        self._mac = STATE_UNKNOWN
        self._uptime = STATE_UNKNOWN
        self._signal = STATE_UNKNOWN
        self._stats_interval = STATE_UNKNOWN
        self._fw_name = STATE_UNKNOWN
        self._fw_version = STATE_UNKNOWN
        self._fw_checksum = STATE_UNKNOWN
        self._implementation = STATE_UNKNOWN

    def _setup(self, subscribe, publish):
        self._discover_nodes(subscribe, publish)

        def on_discovery_stage_1(device, stage):
            subscribe(f'{self._prefix_topic}/#', self._update)
        self._add_on_discovery_stage_change(on_discovery_stage_1, STAGE_1)

    def _discover_nodes(self, subscribe, publish):
        def on_discovery_nodes(topic: str, payload: str, msg_qos: int):
            for node_id in helpers.proccess_nodes(payload):
                if node_id not in self._nodes:
                    node = HomieNode(self, self._prefix_topic, node_id)
                    node._add_on_discovery_stage_change(self._check_discovery_done)
                    node._setup(subscribe, publish)
                    self._nodes[node_id] = node

        subscribe(f'{self._prefix_topic}/$nodes', on_discovery_nodes)

    def _check_discovery_done(self, property=None, stage=None):
        current_stage = self._stage_of_discovery
        if current_stage == STAGE_0:
            if helpers.can_advance_stage(STAGE_1, self._nodes):
                self._set_discovery_stage(STAGE_1)
        if current_stage == STAGE_1:
            if helpers.can_advance_stage(STAGE_2, self._nodes) and self._online is not STATE_UNKNOWN:
                self._set_discovery_stage(STAGE_2)

    def _update(self, topic: str, payload: str, qos: int):
        if self._prefix_topic not in topic:
            return None

        for node in self._nodes.values():
            node._update(topic, payload, qos)

        topic = topic.replace(self._prefix_topic, '')

        # Load Device Properties
        if topic == '/$homie':
            self._convention_version = payload
        if topic == '/$online':
            self._online = payload
        if topic == '/$name':
            self._name = payload
        if topic == '/$localip':
            self._ip = payload
        if topic == '/$mac':
            self._mac = payload

        # Load Device Stats Properties
        if topic == '/$stats/uptime':
            self._uptime = payload
        if topic == '/$stats/signal':
            self._signal = payload
        if topic == '/$stats/interval':
            self._stats_interval = payload

        # Load Firmware Properties
        if topic == '/$fw/name':
            self._fw_name = payload
        if topic == '/$fw/version':
            self._fw_version = payload
        if topic == '/$fw/checksum':
            self._fw_checksum = payload

        # Load Implementation Properties
        if topic == '/$implementation':
            self._implementation = payload

        # Ready
        if topic == '/$online':
            self._check_discovery_done()

    @property
    def base_topic(self):
        """Return the Base Topic of the device."""
        return self._base_topic

    @property
    def device_id(self):
        """Return the Device ID of the device."""
        return self._device_id

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def homie_version(self):
        """Return the Homie Framework Version of the device."""
        return self._convention_version

    @property
    def online(self) -> bool:
        """Return true if the device is online."""
        return helpers.string_to_bool(self._online)

    @property
    def ip(self):
        """Return the IP of the device."""
        return self._ip

    @property
    def mac(self):
        """Return the MAC of the device."""
        return self._mac

    @property
    def uptime(self):
        """Return the Uptime of the device."""
        return self._uptime

    @property
    def signal(self):
        """Return the Signal of the device."""
        return self._signal

    @property
    def stats_interval(self):
        """Return the Stats Interval of the device."""
        return self._stats_interval

    @property
    def firmware_name(self):
        """Return the Firmware Name of the device."""
        return self._fw_name

    @property
    def firmware_version(self):
        """Return the Firmware Version of the device."""
        return self._fw_version

    @property
    def firmware_checksum(self):
        """Return the Firmware Checksum of the device."""
        return self._fw_checksum

    @property
    def is_setup(self):
        """Return True if the Device has been setup as a component"""
        return self._is_setup

    @property
    def nodes(self):
        """Return a Dict of Nodes for the device."""
        return self._nodes

    def node(self, node_id):
        """Return a specific Node for the device."""
        return self._nodes[node_id]

    @property
    def entity_id(self):
        """Return the ID of the entity."""
        return self.device_id
