import socket
import threading
import struct
import argparse

# Stock catalog
stocks = {
    "GameStart": {"price": 15.99, "trading_volume": 0, "suspended": False},
    "RottenFishCo": {"price": 20.50, "trading_volume": 0, "suspended": False}
}

# Thread pool components
request_queue = []
queue_lock = threading.Lock()
queue_semaphore = threading.Semaphore(0)

def lookup(stock_name):
    stock = stocks.get(stock_name)
    if stock is None:
        return -1.0
    if stock["suspended"]:
        return 0.0
    else:
        return stock["price"]

def handle_client(client_socket):
    try:
        data = client_socket.recv(1024)
        if not data:
            return
        parts = data.decode().split(':', 1)
        if len(parts) != 2:
            response = struct.pack('!f', -1.0)
        else:
            method, stock_name = parts
            if method == "Lookup":
                price = lookup(stock_name)
                response = struct.pack('!f', price)
            else:
                response = struct.pack('!f', -1.0)
        client_socket.sendall(response)
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

def worker():
    while True:
        queue_semaphore.acquire()
        with queue_lock:
            task = request_queue.pop(0)
        func, args = task
        func(*args)

def main(thread_pool_size):
    # Start worker threads
    for _ in range(thread_pool_size):
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    # Setup server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 6169))
    server_socket.listen(5)
    print(f"Server listening on port 8888 with thread pool size {thread_pool_size}...")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            task = (handle_client, (client_socket,))
            with queue_lock:
                request_queue.append(task)
            queue_semaphore.release()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start the server with a configurable thread pool size.')
    parser.add_argument('thread_pool_size', type=int, help='Number of threads in the thread pool')
    args = parser.parse_args()
    main(args.thread_pool_size)
