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
    return val == STATE_ON


def bool_to_string(val: bool):
    return STATE_ON if val else STATE_OFF


def check_node_has_prop(platform: str, node, prop: str):
    if not node.has_property(prop):
        raise MissingNodeError(platform, node.entity_id, prop)


def proccess_device(device_topic, device_payload):
    device_match = DISCOVER_DEVICE_FROM_TOPIC.match(device_topic)
    if device_match and device_payload == HOMIE_SUPPORTED_VERSION:
        device_base_topic = device_match.group('prefix_topic')
        device_id = device_match.group('device_id')
        return (True, device_base_topic, device_id)
    return (False, None, None)


def proccess_nodes(nodes_msg):
    return [_proccess_node_match(node_match) for node_match in DISCOVER_NODES_FROM_PAYLOAD.finditer(nodes_msg)]


def _proccess_node_match(node_match):
    return node_match.group('node_id')


def proccess_properties(properties_msg):
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
    can_advance = True
    for child in children.values():
        if child._stage_of_discovery < target_stage:
            can_advance = False

    return can_advance


class MissingNodeError(Exception):
    def __init__(self, platform_type, entity_id, property_id):
        self.platform_type = platform_type
        self.entity_id = entity_id
        self.property_id = property_id
        super().__init__(
            f"Homie {platform_type} {entity_id} doesnt have a {property_id} property")
