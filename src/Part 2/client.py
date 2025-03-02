import grpc
import random
import time
import stock_trading_pb2
import stock_trading_pb2_grpc

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = stock_trading_pb2_grpc.StockTradingStub(channel)
    stocks = ["GameStart", "RottenFishCo", "BoarCo", "MenhirCo", "InvalidStock"]

    for _ in range(20):
        stock = random.choice(stocks)
        if random.choice([True, False]):
            # Lookup
            response = stub.Lookup(stock_trading_pb2.LookupRequest(stock_name=stock))
            print(f"Lookup {stock}: Price={response.price}, Volume={response.trading_volume}")
        else:
            # Trade
            quantity = random.randint(1, 100)
            trade_type = random.choice([
                stock_trading_pb2.TradeRequest.BUY,
                stock_trading_pb2.TradeRequest.SELL
            ])
            try:
                response = stub.Trade(stock_trading_pb2.TradeRequest(
                    stock_name=stock,
                    quantity=quantity,
                    type=trade_type
                ))
                print(f"Trade {stock} x{quantity}: Status={response.status}")
            except Exception as e:
                print(f"Trade error: {e}")
        time.sleep(1)

if __name__ == '__main__':
    run()
