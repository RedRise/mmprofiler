# USECASE [01] manual testing or taker trades. 
# Playing with console prints of orderbook and maker.

from exchange_single_maker import ExchangeSingleMaker
from makers.single_maker_zero_knowledge import SingleMakerZeroKnowledge

maker = SingleMakerZeroKnowledge(90, 110, 0.5, 1)
exchange = ExchangeSingleMaker(maker)

print(exchange.orderBook)

# taking best offer
tx = exchange.buy_at_first_rank()
print(tx)
print(exchange.orderBook)

# taking best bid
print(exchange.sell_at_first_rank())
print(exchange.orderBook)

