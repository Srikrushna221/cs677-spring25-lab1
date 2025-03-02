from concurrent import futures
import threading
import grpc
import stock_trading_pb2
import stock_trading_pb2_grpc
from stock_trading_servicer import StockTradingServicer


def serve(max_workers, max_volumes):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    stock_trading_pb2_grpc.add_StockTradingServicer_to_server(
        StockTradingServicer(max_volumes), server
    )
    server.add_insecure_port('[::]:6169')
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
