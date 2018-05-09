import attr
from .change_listner import ChangeListener
from typing import Callable

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
    def __init__(self):
        super().__init__()

        self._stage_of_discovery = STAGE_0
        self._on_discovery_done = list()

    def _add_on_discovery_stage_change(self, on_discovery_done, stage=STAGE_ALL):
        self._on_discovery_done.append(Subscription(on_discovery_done, stage))

    def _set_discovery_stage(self, stage):
        self._stage_of_discovery = stage
        for subscription in self._on_discovery_done:
            if subscription.stage == stage or subscription.stage == STAGE_ALL:
                subscription.callback(self, stage)
