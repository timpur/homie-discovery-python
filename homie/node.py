from homie.base import HomieBase


class HomieNode(HomieBase):
    def __init__(self, rx_client, create_task, base_path, node_id):
        super().__init__(rx_client, create_task, base_path, node_id)
        self.properties = {}
