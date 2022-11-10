from abc import ABC, abstractmethod
from models.offers_lists import OffersLists
from models.transaction import Transaction


class Maker(ABC):

    cash: float
    asset: float

    def __init__(self) -> None:
        self.cash = 0
        self.asset = 0

    def __str__(self) -> str:
        return "[{classname}] cash:{cash} asset:{asset}".format(
            classname=self.__class__.__name__, cash=self.cash, asset=self.asset
        )

    @property
    @abstractmethod
    def offers(self) -> OffersLists:
        ...

    @abstractmethod
    def buy_at_first_rank(self) -> Transaction:
        ...

    @abstractmethod
    def sell_at_first_rank(self) -> Transaction:
        ...

    @abstractmethod
    def post_hook(self, price: float, time: float):
        pass

    def swap_asset(self, quantity: float, price: float):
        self.asset += quantity
        self.cash -= quantity * price
