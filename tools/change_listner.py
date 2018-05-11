
class ChangeListener(object):
    def __init__(self):
        super().__init__()
        # self._listeners = list()
        setattr(self, '_listeners', list())

    def __setattr__(self, name: str, value: str):
        previouse_value = getattr(self, name, None)
        if previouse_value != value:
            super().__setattr__(name, value)
            for action in self._listeners:
                action(name, previouse_value, value)

    def add_listener(self, action):
        self._listeners.append(action)
