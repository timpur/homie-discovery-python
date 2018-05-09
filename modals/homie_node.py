import logging
from .homie_discovery_base import (HomieDiscoveryBase, STAGE_0, STAGE_1, STAGE_2)
from .constants import STATE_UNKNOWN
from . import helpers
# from .homie_device import HomieDevice
from .homie_property import HomieProperty

_LOGGER = logging.getLogger(__name__)


class HomieNode(HomieDiscoveryBase):
    # A definition of a Homie Node
    def __init__(self, device, base_topic: str, node_id: str):
        super().__init__()
        _LOGGER.info(f"Homie Node Discovered. ID: {node_id}")
        self._device = device
        self._base_topic = base_topic
        self._node_id = node_id
        self._prefix_topic = f'{base_topic}/{node_id}'

        self._properties = dict()

        self._type = STATE_UNKNOWN

    def _setup(self, subscribe, publish):
        self._discover_properties(subscribe, publish)

    def _discover_properties(self, subscribe, publish):
        def on_discovery_properties(topic: str, payload: str, msg_qos: int):
            for property_id, property_settable, property_range in helpers.proccess_properties(payload):
                if property_id not in self._properties:
                    property = HomieProperty(self, self._prefix_topic, property_id, property_settable, property_range)
                    property._add_on_discovery_stage_change(self._check_discovery_done)
                    property._setup(subscribe, publish)
                    self._properties[property_id] = property

        subscribe(f'{self._prefix_topic}/$properties', on_discovery_properties)

    def _check_discovery_done(self, property=None, stage=None):
        current_stage = self._stage_of_discovery
        if current_stage == STAGE_0:
            if helpers.can_advance_stage(STAGE_1, self._properties):
                self._set_discovery_stage(STAGE_1)
        if current_stage == STAGE_1:
            if helpers.can_advance_stage(STAGE_2, self._properties) and self._type is not STATE_UNKNOWN:
                self._set_discovery_stage(STAGE_2)

    def _update(self, topic: str, payload: str, qos: int):
        if self._prefix_topic not in topic:
            return None

        for property in self._properties.values():
            property._update(topic, payload, qos)

        topic = topic.replace(self._prefix_topic, '')

        if topic == '/$type':
            self._type = payload

        # Ready
        if topic == '/$type':
            self._check_discovery_done()

    @property
    def base_topic(self):
        """Return the Base Topic of the node."""
        return self._base_topic

    @property
    def node_id(self):
        """Return the Node Id of the node."""
        return self._node_id

    @property
    def type(self):
        """Return the Type of the node."""
        return self._type

    @property
    def is_setup(self):
        """Return True if the Node has been setup as a component"""
        return self._is_setup

    @property
    def properties(self):
        """Return a Dict of properties for the node."""
        return self._properties

    def has_property(self, property_name: str):
        """Return a specific Property for the node."""
        return property_name in self._properties

    def get_property(self, property_name: str):
        """Return a specific Property for the node."""
        return self._properties[property_name]

    @property
    def device(self):
        """Return the Parent Device of the node."""
        return self._device

    @property
    def entity_id(self):
        """Return the ID of the entity."""
        return f"{self.device.entity_id}_{self.node_id}"
