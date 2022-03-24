import socket
from threading import Thread

class _Client:
	_threads = list()

	@staticmethod
	def _async_connect(host, port, handle=lambda conn, addr: None):
		conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		conn.connect((host, port,))
		handle(conn, (host, port,))
		conn.shutdown(2)
		conn.close()

	@staticmethod
	def async_connect(host, port, handle = lambda conn, addr: None):
		_Client._threads.append(Thread(target=_Client._async_connect, args=(host, port, handle)))
		_Client._threads[-1].start()


def async_connect(host, port, handle):
	_Client.async_connect(host, port, handle)