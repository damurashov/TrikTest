import socket
from threading import Thread, Lock
from generic import Logging


class Server:

	def __init__(self):
		self.handlers = list()
		self.lock = Lock()
		self.threads = list()
		self.handler = None

	def set_handler(self, cb=lambda conn, addr: None):
		self.lock.acquire()
		self.handler = cb
		self.lock.release()

	def _handle(self, conn, addr):
		self.lock.acquire()

		if self.handler:
			Logging.info(Server, Server._handle, "running handler")
			self.handler(conn, addr)
		else:
			Logging.warning(Server, Server.accept, "no handlers were found")

		self.lock.release()

	def accept(self):
		IP = "127.0.0.1"
		PORT = 8889

		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
			s.bind((IP, PORT))
			s.listen()
			while True:
				conn, addr = s.accept()
				Logging.info(Server, Server.accept, "connected", str(addr))
				self._handle(conn, addr)


class _Detail:
	server = None
	thread = None


def _echo_handler(conn, addr):
	Logging.debug(__file__, _echo_handler, "echo, serving", str(addr))
	for i in range(5):
		data = conn.recv(1024)
		conn.sendall(data)


def start(handler=_echo_handler):
	if _Detail.server is None:
		_Detail.server = Server()
		_Detail.server.set_handler(handler)
		_Detail.thread = Thread(target=_Detail.server.accept)
		_Detail.thread.start()


if __name__ == "__main__":
	start()
	while True:
		pass