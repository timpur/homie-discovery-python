class HomieBase():
    def __init__(self, rx_client, create_task, base_path, base_id):
        self._rx_client = rx_client
        self._create_task = create_task
        self._base_path = base_path
        self._base_id = base_id

    @property
    def path(self):
        return f"{self._base_path}/{self._base_id}"

    async def attribute(self, attribute, **kargs):
        return await self._rx_client.first_message(self._topic("$" + attribute), **kargs)

    async def when_attribute(self, attribute, value, **kargs):
        return await self._rx_client.when_first_message(self._topic("$" + attribute), value, **kargs)

    def _topic(self, topic):
        return f"{self.path}/{topic}"
