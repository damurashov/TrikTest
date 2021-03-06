import socket
from threading import Thread
from generic import Logging


class _Client:
	_threads = list()

	@staticmethod
	def async_connect(host, port, handle = lambda conn, addr: None):
		def task():
			conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			try:
				conn.connect((host, port,))
				Logging.info(__file__, "created client connection", "peer", conn.getpeername(), "host", conn.getsockname())
				handle(conn, (host, port,))
				Logging.info(__file__, "shutting down client connection", conn.getpeername(), "host", conn.getsockname())
				conn.shutdown(2)
			except ConnectionRefusedError:
				Logging.error(__file__, "could not connect to", host, port)
			except Exception as e:
				Logging.error(__file__, "caught exception", str(e))
			finally:
				conn.close()

		_Client._threads.append(Thread(target=task))
		_Client._threads[-1].start()


def async_connect(host, port, handle):
	_Client.async_connect(host, port, handle)