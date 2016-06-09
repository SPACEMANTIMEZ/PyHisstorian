import socketserver
import threading
import os
import time
import client.PySSer_Basic
# Enable Logging
import logging, logging.handlers
import bin.logflume

BIN_DIRECTORY = './bin/'
SERVER_ADDRESS = './PySS.Sock'
LOG_SERVER_ADDRESS = BIN_DIRECTORY + bin.logflume.LOG_SERVER_ADDRESS.lstrip('./')

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
log_socket_handler = logging.handlers.SocketHandler(LOG_SERVER_ADDRESS, None)
root_logger.addHandler(log_socket_handler)


class ThreadedUDSHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = str(self.request.recv(1024), 'ascii')
        current_thread = threading.current_thread()
        response = bytes("Current thread: {}, Data: {}".format(current_thread.name, data), 'ascii')
        self.request.sendall(response)


class ThreadedUDSServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    pass


def server_start():
    root_logger.debug("Starting server on {}".format(SERVER_ADDRESS))
    # Make sure that the file doesn't exist before we create the UDS socket
    root_logger.debug("Checking for existing socket.")
    try:
        os.unlink(SERVER_ADDRESS)
    except OSError:
        if os.path.exists(SERVER_ADDRESS):
            raise

    # Create the server
    server = ThreadedUDSServer(SERVER_ADDRESS, ThreadedUDSHandler)

    # Set up and start the main worker thread
    root_logger.debug("Starting main thread.")
    server_main_thread = threading.Thread(target=server.serve_forever)
    server_main_thread.daemon = True
    server_main_thread.start()

    print("Server main worker thread: {}".format(server_main_thread.name))
    return server, server_main_thread


def server_stop(server):
    root_logger.info("Shutting down the server.")
    server.shutdown()
    root_logger.info("Closing out the server.")
    server.server_close()


def process_loop(server_main_thread):
    client.PySSer_Basic.helloworld()
    while True:
        try:
            root_logger.debug("Thread: {}, Running: {}".format(server_main_thread.name, server_main_thread.isAlive))
            time.sleep(15)
        except KeyboardInterrupt:
            root_logger.error("Interrupt detected.")
            break


def main():
    server, server_main_thread = server_start()
    process_loop(server_main_thread)
    server_stop(server)


if __name__ == "__main__":
    main()
