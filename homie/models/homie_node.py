"""Homie Node module"""

import logging

from ..tools import (constants, helpers, HomieDiscoveryBase, STAGE_0, STAGE_1, STAGE_2)
from .homie_property import HomieProperty

_LOGGER = logging.getLogger(__name__)


class HomieNode(HomieDiscoveryBase):
    """A definition of a Homie Node"""

    def __init__(self, device, base_topic: str, node_id: str):
        super().__init__()
        _LOGGER.info(f"Homie Node Discovered. ID: {node_id}")
        self._device = device
        self._base_topic = base_topic
        self._node_id = node_id
        self._prefix_topic = f'{base_topic}/{node_id}'

        self._properties = dict()

        self._type = constants.STATE_UNKNOWN

    def setup(self, subscribe, publish):
        """
        Setup the device node

        This start the discovery proccess of properties
        """
        self._discover_properties(subscribe, publish)

    def _discover_properties(self, subscribe, publish):
        def _on_discovery_properties(topic: str, payload: str, msg_qos: int):
            for property_id, property_settable, property_range in helpers.proccess_properties(payload):
                if property_id not in self._properties:
                    homie_property = HomieProperty(self, self._prefix_topic, property_id, property_settable, property_range)
                    homie_property.add_on_discovery_stage_change(self._check_discovery_done)
                    homie_property.setup(subscribe, publish)
                    self._properties[property_id] = homie_property

        subscribe(f'{self._prefix_topic}/$properties', _on_discovery_properties)

    def _check_discovery_done(self, homie_property=None, stage=None):
        current_stage = self._stage_of_discovery
        if current_stage == STAGE_0:
            if helpers.can_advance_stage(STAGE_1, self._properties):
                self._set_discovery_stage(STAGE_1)
        if current_stage == STAGE_1:
            if helpers.can_advance_stage(STAGE_2, self._properties) and self._type is not constants.STATE_UNKNOWN:
                self._set_discovery_stage(STAGE_2)

    def _update(self, topic: str, payload: str, qos: int):
        if self._prefix_topic not in topic:
            return None

        for homie_property in self._properties.values():
            homie_property._update(topic, payload, qos)

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
        return self.stage_of_discovery >= STAGE_2

    @property
    def properties(self):
        """Return a List of properties for the node."""
        return self._properties.values()

    def has_property(self, property_id: str):
        """Return a specific Property for the node."""
        return property_id in self._properties

    def get_property(self, property_id: str):
        """Return a specific Property for the node."""
        return self._properties[property_id]

    @property
    def device(self):
        """Return the Parent Device of the node."""
        return self._device

    @property
    def entity_id(self):
        """Return the ID of the entity."""
        return f"{self.device.entity_id}_{self.node_id}"
