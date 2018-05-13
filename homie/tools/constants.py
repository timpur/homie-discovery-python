import re


# REGEX
DISCOVER_DEVICE_FROM_TOPIC = re.compile(r'(?P<prefix_topic>\w[-/\w]*\w)/(?P<device_id>\w[-\w]*\w)/\$homie')
DISCOVER_NODES_FROM_PAYLOAD = re.compile(r'(?P<node_id>\w[-/\w]*\w)')
DISCOVER_PROPERTIES_FROM_PAYLOAD = re.compile(r'(?P<property_id>\w[-/\w]*\w)(\[(?P<range_start>[0-9])-(?P<range_end>[0-9]+)\])?(?P<settable>:settable)?')

# Global
HOMIE_SUPPORTED_VERSION = '2.0.1'
DEFAULT_DISCOVERY_PREFIX = 'homie'
DEFAULT_QOS = 0

# Types
TYPE_SENSOR = "sensor"
TYPE_SWITCH = "switch"
TYPE_LIGHT = "light"
TYPE_LIGHT_RGB = "light_rgb"

# Props
PROP_VALUE = 'value'
PROP_UNIT = 'unit'
PROP_ON = 'on'
PROP_BRIGHTNESS = 'brightness'
PROP_RGB = 'rgb'

# Values
STATE_UNKNOWN = 'unknown'
STATE_ON = 'true'
STATE_OFF = 'false'

# Functions


def set_state_unknown(value):
    global STATE_UNKNOWN
    STATE_UNKNOWN = value
