"""Change Listener Base helper"""

import types
from typing import Callable
import attr

ANY_ATTRIBUTE = "*"


@attr.s(slots=True, frozen=True)
class Subscription(object):
    """Class to hold data about an active subscription."""

    callback = attr.ib(type=Callable[[object, int], None])
    attribute_names = attr.ib(type=list)


class AttributeChangeListener(object):
    """
    Change Listener Base helper

    This class helps you observe chages too arributes of a class
    """

    def __init__(self):
        super().__init__()
        # self._listeners = list()
        setattr(self, '_attribute_subscriptions', list())

    def __setattr__(self, name: str, value: str):
        previouse_value = getattr(self, name, None)
        if previouse_value != value:
            super().__setattr__(name, value)
            self._call_subscriptions(name, previouse_value, value)

    def add_attribute_listener(self, on_attribute_change, attribute_names=ANY_ATTRIBUTE):
        """Add a listener to object attribute value changes"""

        if not isinstance(on_attribute_change, types.FunctionType) and not isinstance(on_attribute_change, types.MethodType):
            raise Exception("on_attribute_change must be a function")

        if isinstance(attribute_names, str):
            attribute_names = attribute_names.split(',')
        if not isinstance(attribute_names, list):
            raise Exception(f"attribute_names must be a string or a list: {type(attribute_names)}")

        self._attribute_subscriptions.append(Subscription(on_attribute_change, attribute_names))

    def _call_subscriptions(self, attribute_name, previouse_value, value):
        for subscription in self._attribute_subscriptions:
            if attribute_name in subscription.attribute_names or ANY_ATTRIBUTE in subscription.attribute_names:
                subscription.callback(self, attribute_name, previouse_value, value)
