"""Homie Discovery Base helper"""

from typing import Callable
import attr
from .change_listner import ChangeListener

STAGE_ALL = -1
STAGE_0 = 0
STAGE_1 = 1
STAGE_2 = 2


@attr.s(slots=True, frozen=True)
class Subscription(object):
    """Class to hold data about an active subscription."""

    callback = attr.ib(type=Callable[[object, int], None])
    stage = attr.ib(type=int, default=-1)


class HomieDiscoveryBase(ChangeListener):
    """Homie Discovery Base heper"""

    def __init__(self):
        super().__init__()

        self._stage_of_discovery = STAGE_0
        self._on_discovery_subscriptions = list()

    def add_on_discovery_stage_change(self, on_discovery_done, stage=STAGE_ALL):
        """Add a on discovery change subscription"""

        if on_discovery_done is None:
            raise Exception("")
        self._on_discovery_subscriptions.append(Subscription(on_discovery_done, stage))

    @property
    def stage_of_discovery(self):
        """Get stage of discovery"""

        return self._stage_of_discovery

    def _set_discovery_stage(self, stage):
        self._stage_of_discovery = stage
        for subscription in self._on_discovery_subscriptions:
            if subscription is None:
                Exception()
            if subscription.stage == stage or subscription.stage == STAGE_ALL:
                subscription.callback(self, stage)
