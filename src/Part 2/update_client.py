import grpc
import random
import time
import stock_trading_pb2
import stock_trading_pb2_grpc

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = stock_trading_pb2_grpc.StockTradingStub(channel)
    stocks = ["GameStart", "RottenFishCo", "BoarCo", "MenhirCo"]

    while True:
        stock = random.choice(stocks)
        new_price = round(random.uniform(10.0, 100.0), 2)
        try:
            response = stub.Update(stock_trading_pb2.UpdateRequest(
                stock_name=stock,
                new_price=new_price
            ))
            print(f"Updated {stock} to {new_price}: Status={response.status}")
        except Exception as e:
            print(f"Update error: {e}")
        time.sleep(random.randint(2, 5))

if __name__ == '__main__':
    run()
