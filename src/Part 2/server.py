from concurrent import futures
import threading
import grpc
import stock_trading_pb2
import stock_trading_pb2_grpc

class StockTradingServicer(stock_trading_pb2_grpc.StockTradingServicer):
    def __init__(self, max_volumes):
        self.stocks = {}
        self.locks = {}
        for stock, max_vol in max_volumes.items():
            self.stocks[stock] = {
                "price": 0.0,
                "trading_volume": 0,
                "max_volume": max_vol
            }
            self.locks[stock] = threading.Lock()
        # Initialize default prices
        default_prices = {
            "GameStart": 15.99,
            "RottenFishCo": 20.50,
            "BoarCo": 30.00,
            "MenhirCo": 25.75
        }
        for stock, price in default_prices.items():
            if stock in self.stocks:
                self.stocks[stock]["price"] = price

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
            if stock["trading_volume"] >= stock["max_volume"]:
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

def serve(max_workers, max_volumes):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    stock_trading_pb2_grpc.add_StockTradingServicer_to_server(
        StockTradingServicer(max_volumes), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    print(f"Server started with max workers {max_workers}")
    server.wait_for_termination()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--max_workers', type=int, default=10,
                       help='Maximum concurrent RPCs')
    parser.add_argument('--max_volumes', type=str, required=True,
                       help='Comma-separated max volumes: GameStart=1000,RottenFishCo=800,...')
    args = parser.parse_args()

    max_volumes = {}
    for item in args.max_volumes.split(','):
        stock, vol = item.split('=')
        max_volumes[stock.strip()] = int(vol.strip())

    serve(args.max_workers, max_volumes)
