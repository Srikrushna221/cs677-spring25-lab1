from concurrent import futures
import threading
import grpc
import stock_trading_pb2
import stock_trading_pb2_grpc


class StockTradingServicer(stock_trading_pb2_grpc.StockTradingServicer):
    def __init__(self, max_volumes):
        self.stocks = {
          "GameStart": {
            "price": 15.99,
            "trading_volume": 0,
            "max_volume": 0
          },
          "RottenFishCo": {
            "price": 20.5,
            "trading_volume": 0,
            "max_volume": 0
          },
          "BoarCo": {
            "price": 30,
            "trading_volume": 0,
            "max_volume": 0
          },
          "MenhirCo": {
            "price": 25.75,
            "trading_volume": 0,
            "max_volume": 0
          }
        }
        self.locks = {}
        for stock, max_vol in max_volumes.items():
            if stock in self.stocks.keys():
                self.stocks[stock]['max_volume'] = max_vol
                self.locks[stock] = threading.Lock()

    def Lookup(self, request, context):
        stock_name = request.stock_name
        if stock_name not in self.stocks:
            return stock_trading_pb2.LookupResponse(price=-1.0, trading_volume=0)
        with self.locks[stock_name]:
            stock = self.stocks[stock_name]
            return stock_trading_pb2.LookupResponse(
                price=stock["price"],
                trading_volume=stock["trading_volume"]
            )

    def Trade(self, request, context):
        stock_name = request.stock_name
        quantity = request.quantity
        if stock_name not in self.stocks:
            return stock_trading_pb2.TradeResponse(status=-1)
        with self.locks[stock_name]:
            stock = self.stocks[stock_name]
            if (stock["trading_volume"] + quantity) > stock["max_volume"]:
                return stock_trading_pb2.TradeResponse(status=0)
            stock["trading_volume"] += quantity
            return stock_trading_pb2.TradeResponse(status=1)

    def Update(self, request, context):
        stock_name = request.stock_name
        new_price = request.new_price
        if stock_name not in self.stocks:
            return stock_trading_pb2.UpdateResponse(status=-1)
        if new_price < 0:
            return stock_trading_pb2.UpdateResponse(status=-2)
        with self.locks[stock_name]:
            self.stocks[stock_name]["price"] = new_price
        return stock_trading_pb2.UpdateResponse(status=1)
