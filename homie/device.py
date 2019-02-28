from rx.operators import filter
from homie.base import HomieBase
from homie.node import HomieNode


def _filter_state_ready():
    return filter(lambda x: x.payload == "ready")


class HomieDevice(HomieBase):
    def __init__(self, rx_client, create_task, base_path, device_id):
        super().__init__(rx_client, create_task, base_path, device_id)
        self._nodes = {}

    @property
    def nodes(self):
        return self._nodes

    # async def discover(self):
    #     client = self._rx_client
    #     await client.subscribe(self._topic("+"))
    #     client.message(self._topic("$state"), pipes=[]).subscribe_(lambda _: self._create_task(self._on_discovery_ready()))

    # async def _on_discovery_ready(self):
    #     client = self._rx_client
    #     nodes = await client.first_message(self._topic("$nodes"))
    #     if nodes:
    #         nodes = nodes.split(',')
    #         for node_id in nodes:
    #             if node_id in self._nodes:
    #                 print(f"{node_id} device already discovered in {self._device_id}")
    #                 return
    #             node = HomieNode(self._rx_client, self._create_task, f"{self._base_path}/{self._device_id}", node_id)
    #             self._nodes[node_id] = node
    #             self._create_task(node.discover())
