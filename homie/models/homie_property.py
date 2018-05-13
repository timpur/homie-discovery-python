import logging

from ..tools import (constants, helpers, HomieDiscoveryBase, STAGE_1, STAGE_2)

_LOGGER = logging.getLogger(__name__)


class HomieProperty(HomieDiscoveryBase):
    # A definition of a Homie Property
    def __init__(self, node, base_topic: str, property_id: str, settable: bool, ranges: tuple):
        super().__init__()
        _LOGGER.info(f"Homie Property Discovered. ID: {property_id}")
        self._node = node
        self._base_topic = base_topic
        self._property_id = property_id
        self._settable = settable
        self._range = ranges
        self._prefix_topic = f'{base_topic}/{property_id}'

        self._state = constants.STATE_UNKNOWN

    def _setup(self, subscribe, publish):
        self._publish = publish
        self._set_discovery_stage(STAGE_2)

    def _update(self, topic: str, payload: str, qos: int):
        if self._prefix_topic not in topic:
            return None

        topic = topic.replace(self._prefix_topic, '')

        if topic == '':
            self._state = payload

    @property
    def property_id(self):
        """Return the Property Id of the Property."""
        return self._property_id

    @property
    def state(self):
        """Return the state of the Property."""
        return self._state

    def set_state(self, value: str):
        """Set the state of the Property."""
        if self.settable:
            self._publish(f"{self._prefix_topic}/set", value)

    @property
    def settable(self):
        """Return if the Property is settable."""
        return self._settable

    @property
    def node(self):
        """Return the Parent Node of the Property."""
        return self._node

    @property
    def entity_id(self):
        """Return the ID of the entity."""
        return f"{self.node.entity_id}_{self.property_id}"

    # @property
    # def name(self):
    #     """Return the Name of the Property."""
    #     return self._name

    # @property
    # def unit(self):
    #     """Return the Unit for the Property."""
    #     return self._unit

    # @property
    # def dataType(self):
    #     """Return the Data Type for the Property."""
    #     return self._datatype

    # @property
    # def format(self):
    #     """Return the Format for the Property."""
    #     return self._format
