# USECASE [01] manual testing or taker trades. 
# Playing with console prints of orderbook and maker.

from exchange_single_maker import ExchangeSingleMaker
from makers.maker_zero_knowledge import MakerZeroKnowledge

maker = MakerZeroKnowledge(initMidPrice=100, tickSize=0.5, numBids=10, sizeBid=0.1, numOffers=10, sizeOffer=0.1)
exchange = ExchangeSingleMaker(maker)

print(exchange.orderBook)

# taking best offer
tx = exchange.buy_at_first_rank()
print(tx)
print(exchange.orderBook)

# taking best bid
print(exchange.sell_at_first_rank())
print(exchange.orderBook)


