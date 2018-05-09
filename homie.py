import logging
from paho_mqtt_client_manager import (MQTTWrapper, MessageCallbackType)
# from modals.constants import (DISCOVER_DEVICE_FROM_TOPIC, HOMIE_SUPPORTED_VERSION)
from modals import helpers
from modals.homie_device import HomieDevice
from modals.homie_node import HomieNode
from modals.homie_discovery_base import (STAGE_0, STAGE_1, STAGE_2)


_LOGGER = logging.getLogger(__name__)


class Homie():
    def __init__(self, mqtt: MQTTWrapper, discovery_prefix: str, qos: int):
        DOMAIN = "Homie"
        _DEVICES = dict()

        def start():
            _LOGGER.info(f"Component - {DOMAIN} - Start. Discovery Topic: {discovery_prefix}/")
            discover_devices()

        def subscribe(topic: str, msg_callback: MessageCallbackType, qos: int=qos):
            mqtt.subscribe(topic, msg_callback, qos)

        def publish(topic: str, payload: str, retain: bool=True, qos: int=qos):
            mqtt.publish(topic, payload, qos, retain)

        def discover_devices():
            def on_discovery_device(topic: str, payload: str, msg_qos: int):
                supported, device_base_topic, device_id = helpers.proccess_device(topic, payload)
                if supported and device_id not in _DEVICES:
                    device = HomieDevice(device_base_topic, device_id)
                    device._add_on_discovery_stage_change(on_device_discovery)
                    device._setup(subscribe, publish)
                    _DEVICES[device_id] = device

            mqtt.subscribe(f'{discovery_prefix}/+/$homie', on_discovery_device, qos)

        def on_device_discovery(device, state):
            if state == STAGE_1:
                def on_node_ready(node, stage):
                    component_ready(node)
                for node in device.nodes.values():
                    node._add_on_discovery_stage_change(on_node_ready, STAGE_2)

            if state == STAGE_2:
                component_ready(device)

        def component_ready(component):
            if type(component) is HomieDevice:
                _LOGGER.debug(f"Device Name: {component.device_id}")
                # await async_setup_device(component)
            if type(component) is HomieNode:
                _LOGGER.debug(f"Node Name: {component.node_id}")
                # await async_setup_node(component)

                # async def async_setup_device(device: HomieDevice):
                #     pass

                # async def async_setup_node(node: HomieNode):
                #     if node.type.startswith(TYPE_SENSOR):
                #         await setup_device_node_as_platform(node, 'sensor')
                #     elif node.type.startswith(TYPE_SWITCH):
                #         await setup_device_node_as_platform(node, 'switch')
                #     elif node.type.startswith(TYPE_LIGHT):
                #         await setup_device_node_as_platform(node, 'light')

                # async def setup_device_node_as_platform(node: HomieNode, platform: str):
                #     hass.data[KEY_HOMIE_ALREADY_DISCOVERED][node.entity_id] = node
                #     discovery_info = {KEY_HOMIE_ENTITY_NAME: node.entity_id}
                #     await async_load_platform(hass, platform, DOMAIN, discovery_info)

        start()
