import server, parser
from threading import Lock
from dataclasses import dataclass, field
from generic import Logging
from socket import socket


@dataclass
class State:
	clients: list = field(default_factory=list)
	servers: list = field(default_factory=list)
	peers: list = field(default_factory=list)
	lock: Lock = field(default_factory=Lock)


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


class _Detail:
	state = State(clients=list(), servers=list(), peers=list(), lock=Lock())


@dataclass
class Proto:
	state: State
	context: Context

	def run(self):
		Logging.info(Proto, Proto.run, "serving", self.context)


def tcp_handle(conn, addr):
	proto = Proto(state=_Detail.state, context=Context(connection=conn, address=addr))
	proto.run()

