import socket
import PySS


def client(target_server_address, message):

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.connect(target_server_address)
        sock.sendall(bytes(message, 'ascii'))
        response = str(sock.recv(1024), 'ascii')
        print("Received: {}".format(response))


def helloworld():
    for i in range(1, 10):
        client(PySS.SERVER_ADDRESS, "Hello from iter {}".format(str(i)))


def main():
    helloworld()


if __name__ == "__main__":
    main()