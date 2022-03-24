import server, parser
from threading import Lock
from dataclasses import dataclass, field
from generic import Logging
from socket import socket


@dataclass
class Context:
	connection: socket
	address: tuple


class Handle:

	def on_iter(self, delta):
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
		Logging.debug(*args, "context", self.context)

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

	def __post_init__(self):
		self.process_sequence = [self.state, Log(self.context)]

	def run(self):
		Logging.info(Proto, Proto.run, "serving", self.context)


def tcp_handle(conn, addr):
	proto = Proto(state=_Detail.state, context=Context(connection=conn, address=addr))
	proto.run()

