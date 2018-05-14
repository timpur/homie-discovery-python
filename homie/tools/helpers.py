"""Homie hHelper module"""

from .constants import (
    DISCOVER_DEVICE_FROM_TOPIC,
    DISCOVER_NODES_FROM_PAYLOAD,
    DISCOVER_PROPERTIES_FROM_PAYLOAD,
    HOMIE_SUPPORTED_VERSION,
    STATE_ON,
    STATE_OFF
)


# Global Helper Functions


def string_to_bool(val: str):
    """Convert a homie string bool to a python bool"""
    return val == STATE_ON


def bool_to_string(val: bool):
    """Convert a python bool to a homie string bool"""
    return STATE_ON if val else STATE_OFF


def string_to_int(value, dp=0):
    """Converts a homie string to a python bool"""
    try:
        return round(int(value), dp)
    except ValueError:
        return 0


def int_to_string(value, dp=0):
    """Converts a python int to a homie string"""
    return str(round(value, dp))


def check_node_has_prop(platform: str, node, homie_property_id: str):
    """Check a homie node has a homie property"""
    if not node.has_property(homie_property_id):
        raise MissingPropertyError(platform, node.entity_id, homie_property_id)


def proccess_device(device_topic, device_payload):
    """
    Parses device discover topic into a homie device discovery result

    Returns: `(supported, device_base_topic, device_id)`
    """
    device_match = DISCOVER_DEVICE_FROM_TOPIC.match(device_topic)
    if device_match and device_payload == HOMIE_SUPPORTED_VERSION:
        device_base_topic = device_match.group('prefix_topic')
        device_id = device_match.group('device_id')
        return (True, device_base_topic, device_id)
    return (False, None, None)


def proccess_nodes(nodes_msg):
    """
    Parses `$nodes` payload into a list of node discovery results

    Returns: `list[node_id]`
    """
    return [_proccess_node_match(node_match) for node_match in DISCOVER_NODES_FROM_PAYLOAD.finditer(nodes_msg)]


def _proccess_node_match(node_match):
    return node_match.group('node_id')


def proccess_properties(properties_msg):
    """
    Parses `$properties` into a list of property discovery results

    Returns: `list[(property_id, settable, range)]`
    """
    return [_proccess_property_match(property_match) for property_match in DISCOVER_PROPERTIES_FROM_PAYLOAD.finditer(properties_msg)]


def _proccess_property_match(property_match):
    property_id = property_match.group('property_id')
    property_settable = True if property_match.group('settable') is not None else False
    property_range = (property_match.group('range_start'), property_match.group('range_end'))
    return (
        property_id,
        property_settable,
        property_range if property_match.group('range_start') is not None else ()
    )


def can_advance_stage(target_stage, children):
    """Helper to know if all children are at lest at a target stage of discovery"""
    can_advance = True
    for child in children.values():
        if child.stage_of_discovery < target_stage:
            can_advance = False

    return can_advance


class MissingPropertyError(Exception):
    """Missing Property of a Node Exception"""

    def __init__(self, platform_type, entity_id, property_id):
        self.platform_type = platform_type
        self.entity_id = entity_id
        self.property_id = property_id
        super().__init__(
            f"Homie {platform_type} {entity_id} doesnt have a {property_id} property")
