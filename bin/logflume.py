import pickle
import logging
import logging.handlers
import socketserver
import struct
import os

LOG_SERVER_ADDRESS = './Log.Sock'
LOGGER_NAME = 'PyShytLogger'
LOG_FILE_NAME = '../log/' + LOGGER_NAME + '.log'

BASE_LOG_LEVEL = logging.DEBUG
USER_LOG_LEVEL = logging.WARNING
FLUSH_LOG_LEVEL = logging.ERROR

MEM_BUF = 256 # Max records buffered
MAX_LOG_SIZE = 2 * 1024 * 1024 # Size in bytes
BACKUP_COUNT = 5 # No of files

MESSAGE_FORMAT_DETAIL = '%(asctime)-20s | %(levelname)-10s | %(name)-6s | %(message)s'
MESSAGE_FORMAT_VALUE_ONLY = '{Time:%(asctime)-12s, Value:%(message)s}'
MESSAGE_FORMAT_OVERRIDE = '%(message)s'
DATE_FORMAT_UTC_SECONDS = '%s'
DATE_FORMAT_FULL = '%Y-%m-%d %H:%M:%S'


class LogRecordStreamHandler(socketserver.StreamRequestHandler):

    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            record = logging.makeLogRecord(obj)
            self.handleLogRecord(record)

    def unPickle(self, data):
        return pickle.loads(data)

    def handleLogRecord(self, record):
        # if a name is specified, we use the named logger rather than the one
        # implied by the record.
        if self.server.logname is not None:
            name = self.server.logname
        else:
            name = record.name
        logger = logging.getLogger(name)
        logger.handle(record)


class LogRecordUDSReceiver(socketserver.ThreadingUnixStreamServer):
    """
    Simple Unix socket-based logging receiver suitable for testing.
    """
    try:
        os.unlink(LOG_SERVER_ADDRESS)
    except OSError:
        if os.path.exists(LOG_SERVER_ADDRESS):
            raise

    def __init__(self, address=LOG_SERVER_ADDRESS, handler=LogRecordStreamHandler):
        socketserver.ThreadingUnixStreamServer.__init__(self, address, handler)
        self.abort = 0
        self.timeout = 1
        self.logname = None

    def serve_until_stopped(self):
        import select
        abort = 0
        while not abort:
            rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort


def configure_logging():
    # Create logger and handlers
    logger = logging.getLogger()
    # Console handler provides real-time feedback
    ch = logging.StreamHandler()
    rfh = logging.handlers.RotatingFileHandler(LOG_FILE_NAME, mode='w', maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT)
    # MemoryHandler provides buffer to handle writes to rotating file
    mh = logging.handlers.MemoryHandler(capacity=MEM_BUF, flushLevel=FLUSH_LOG_LEVEL, target=rfh)

    # Set the log level for each of the handlers
    logger.setLevel(BASE_LOG_LEVEL)
    rfh.setLevel(BASE_LOG_LEVEL)
    mh.setLevel(BASE_LOG_LEVEL)
    ch.setLevel(USER_LOG_LEVEL)

    # Create formatter
    formatter = logging.Formatter(MESSAGE_FORMAT_DETAIL, datefmt=DATE_FORMAT_FULL)

    # Set formatter to handlers
    ch.setFormatter(formatter)
    rfh.setFormatter(formatter)
    mh.setFormatter(formatter)

    # Add handlers to the target logger (file handler used indirectly through memory handler)
    if verbose:
        logger.addHandler(ch)
    logger.addHandler(mh)


def main():
    configure_logging()
    udsserver = LogRecordUDSReceiver()
    print('Starting log server on {}'.format(LOG_SERVER_ADDRESS))
    udsserver.serve_until_stopped()

if __name__ == '__main__':
    verbose = True
    main()