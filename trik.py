import server, parser, time, select
from threading import Lock, Thread
from dataclasses import dataclass, field
from generic import Logging
from socket import socket


@dataclass
class Context:
	connection: socket
	address: tuple


class Handle:

	def on_iter(self, time_delta_sec):
		pass

	def on_register(self, port, hull_number):
		pass

	def on_self(self, hull_number):
		pass

	def on_connection(self, ip, port, hull_number):
		pass

	def on_keepalive(self):
		pass

	def on_data(self, data: str):
		pass


@dataclass
class Log(Handle):
	context: Context

	def _log(self, *args):
		Logging.debug(*args, "context", self.context.address)

	def on_register(self, port, hull):
		self._log(Log, Log.on_register, "port", port, "hull", hull)

	def on_self(self, hull_number):
		self._log(Log, Log.on_self, "hull", hull_number)

	def on_connection(self, ip, port, hull_number):
		self._log(Log, Log.on_connection, "ip", ip, "port", port, "hull", hull_number)

	def on_keepalive(self):
		self._log(Log, Log.on_keepalive)

	def on_data(self, data: str):
		self._log(Log, Log.on_data, data)


@dataclass
class State(Handle):
	clients: list = field(default_factory=list)
	servers: list = field(default_factory=list)
	peers: list = field(default_factory=list)
	lock: Lock = field(default_factory=Lock)


class _Detail:
	state = State(clients=list(), servers=list(), peers=list(), lock=Lock())


@dataclass
class Proto:
	state: State
	context: Context

	def _timer(self):
		while self.time_run:
			now = time.time()
			for h in self.process_sequence:
				h.on_iter(now - self.time_prev)

			self.time_prev = now
			time.sleep(self.time_period_sec)

	def __post_init__(self):
		self.process_sequence = [self.state, Log(self.context)]
		# Timer thread
		self.time_run = True
		self.time_prev = time.time()
		self.time_period_sec = 3
		self.time_thread = Thread(target=self._timer)
		self.time_thread.start()

	def _iter(self):
		data = self.context.connection.recv(128)

		if not len(data):
			return False

		parsed = parser.unmarshalling(data)

		if parsed is not None:
			for h in self.process_sequence:
				{
					"register": h.on_register,
					"self": h.on_self,
					"connection": h.on_connection,
					"keepalive": h.on_keepalive,
					"data": h.on_data,
				}[parsed[0]](*parsed[1:])

		return True

	def run(self):
		Logging.info(Proto, Proto.run, "serving", self.context)

		while self._iter():
			pass

		Logging.info(Proto, Proto.run, "finished serving", self.context)

	def __del__(self):
		self.stop_flag = True
		self.time_thread.join()


def tcp_handle(conn, addr):
	proto = Proto(state=_Detail.state, context=Context(connection=conn, address=addr))
	proto.run()

