import socket
import struct

def main():
    stocks = ["GameStart", "RottenFishCo", "InvalidStock"]
    for stock in stocks:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 6169))
            message = f"Lookup:{stock}"
            s.sendall(message.encode())
            data = s.recv(4)
            if len(data) == 4:
                price = struct.unpack('!f', data)[0]
                print(f"Price for {stock}: {price}")
            else:
                print(f"Invalid response for {stock}")

if __name__ == "__main__":
    main()
