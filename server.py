import socket
from threading import Thread, Lock
from generic import Logging


class Server:

	def __init__(self, port=8889):
		self.handlers = list()
		self.threads = list()
		self.handler = None
		self.port = port

	def set_handler(self, cb=lambda conn, addr: None):
		self.handler = cb

	def _handle(self, conn, addr):

		if self.handler:
			Logging.info(Server, Server._handle, "running handler")
			self.handler(conn, addr)
			conn.shutdown(2)
			conn.close()
		else:
			Logging.warning(Server, Server.accept, "no handlers were found")


	def accept(self):
		IP = "0.0.0.0"
		PORT = self.port
		Logging.info(__file__, Server, "trying to open connection", "IP", IP, "port", PORT)

		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
			s.bind((IP, PORT))
			s.listen()
			while True:
				conn, addr = s.accept()
				Logging.info(Server, Server.accept, "connected", str(addr))
				self.threads.append(Thread(target=self._handle, args=(conn, addr,)))
				self.threads[-1].start()


class _Detail:
	server = None
	thread = None


def _echo_handler(conn, addr):
	Logging.debug(__file__, _echo_handler, "echo, serving", str(addr))
	for i in range(5):
		data = conn.recv(1024)
		conn.sendall(data)


def start(handler=_echo_handler, port=8889):
	if _Detail.server is None:
		_Detail.server = Server(port=port)
		_Detail.server.set_handler(handler)
		_Detail.thread = Thread(target=_Detail.server.accept)
		_Detail.thread.start()


if __name__ == "__main__":
	start()
	while True:
		pass