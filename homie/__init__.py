import re
from asyncio import iscoroutinefunction
from homie.adapters.mqtt.base import RxMqttBase
from homie.utils import version_supported
from homie.device import HomieDevice
from homie.node import HomieNode
from homie.property import HomieProperty

VERSION_SUPPORTED = "3.0.0"


class HomieDiscovery:
    def __init__(self, rx_client, create_task, discovery_paths):
        if not isinstance(rx_client, RxMqttBase):
            raise ValueError('rx_client must be type RxMqttBase')
        if not isinstance(discovery_paths, list):
            raise ValueError('discovery_paths must be type list')

        self._rx_client = rx_client
        self._create_task = create_task
        self._discovery_paths = discovery_paths
        self._base_path_devices = {path: {} for path in discovery_paths}

        self._on = {"device": [], "node": [], "property": []}

    def on(self, event, cb):
        self._on[event].append(cb)

    def _invoke(self, event, data):
        for cb in self._on[event]:
            if iscoroutinefunction(cb):
                self._create_task(cb(data))
            else:
                cb(data)

    async def discover(self):
        client = self._rx_client
        create_task = self._create_task

        def _parse_device(message):
            matches = re.search(r"(.+)\/(.+)\/\$homie", message.topic)
            if matches:
                base_path, device_id = matches.groups()
                supported = version_supported(VERSION_SUPPORTED, message.payload)
                if not supported:
                    print(f"'{device_id}' device at '{base_path}' is not supported. Vesion needed '{VERSION_SUPPORTED}' has '{message.payload}'")
                    return
                create_task(self.discovery_device(base_path, device_id))

        for path in self._discovery_paths:
            client.message(f"{path}/+/$homie").subscribe_(_parse_device)
            await self.sub_to_discovery_topics(path)

    async def discovery_device(self, base_path, device_id):
        client = self._rx_client
        create_task = self._create_task
        devices = self._base_path_devices[base_path]

        if device_id in devices:
            print(f"'{device_id}' device already discovered in '{base_path}'")
            return

        device = HomieDevice(client, create_task, base_path, device_id)
        devices[device_id] = device
        self._invoke("device", device)

        # device_state = await device.when_attribute("state", "ready", ttl=10)
        # if not device_state:
        #     print(f"{device.path} never reached ready state during discovery")
        #     return

        def _parse_nodes(message):
            if not message.payload:
                return
            for node_id in message.payload.split(','):
                create_task(self.discover_node(device, node_id))
        client.message(device._topic("$nodes")).subscribe_(_parse_nodes)

    async def discover_node(self, device, node_id):
        client = self._rx_client
        create_task = self._create_task
        nodes = device.nodes

        if node_id in nodes:
            print(f"'{node_id}' node already discovered in device '{device.path}'")
            return

        node = HomieNode(client, create_task, device.path, node_id)
        nodes[node_id] = node
        self._invoke("node", node)

        def _parse_properties(message):
            if not message.payload:
                return
            for property_id in message.payload.split(','):
                create_task(self.discover_node_property(device, node, property_id))
        client.message(node._topic("$properties")).subscribe_(_parse_properties)

    async def discover_node_property(self, device, node, property_id):
        client = self._rx_client
        create_task = self._create_task
        properties = node.properties

        if property_id in properties:
            print(f"'{property_id}' property already discovered in node '{node.path}'")
            return

        prop = HomieProperty(client, create_task, node.path, property_id)
        properties[property_id] = prop
        self._invoke("property", prop)

    async def sub_to_discovery_topics(self, path):
        topics = [
            "+/$homie",
            "+/$name",
            "+/$state",
            "+/$localip",
            "+/$mc",
            "+/$fw/name",
            "+/$fw/version",
            "+/$nodes",
            "+/$implementation",
            "+/$stat",
            "+/$stat/interval",
            "+/+/$name",
            "+/+/$type",
            "+/+/$properties",
            # "+/+/$array",
            "+/+/+/$name",
            "+/+/+/$settable",
            "+/+/+/$retained",
            "+/+/+/$unit",
            "+/+/+/$datatype",
            "+/+/+/$format",
            "+/+/+/$retained",
            "+/+/+/$retained",
            "$broadcast/#"
        ]
        topics = list(map(lambda x: path + '/' + x, topics))
        await self._rx_client.subscribe(topics)
