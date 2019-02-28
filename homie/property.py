from homie.base import HomieBase


class HomieProperty(HomieBase):
    def __init__(self, rx_client, create_task, base_path, property_id):
        super().__init__(rx_client, create_task, base_path, property_id)
