import server, parser, time, select
from threading import Lock, Thread
from dataclasses import dataclass, field
from generic import Logging
from socket import socket


HULL_NUMBER = 888
HULL_NUMBER_CLI = 888


@dataclass
class Context:
	connection: socket
	address: tuple

	def get_host_port(self):
		return self.connection.getsockname()[1]

	def get_host_ip(self):
		return self.connection.getsockname()[0]


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
class State(Handle):

	@dataclass
	class Peer:
		address: tuple
		hull_number: int

	peers: dict = field(default_factory=dict)
	lock: Lock = field(default_factory=Lock)

	def update_peer(self, ip, port, hull_number):
		self.peers[hull_number] = State.Peer((ip, port,), hull_number)


class Cli:

	__cli = []

	@staticmethod
	def call(*args):
		for c in Cli.__cli:
			c.on_cli(*args)

	def __init__(self):
		Cli.__cli.append(self)

	def on_cli(self, *args):
		raise NotImplemented


class PeriodTrigger:

	def __init__(self, process_sequence, timeout_sec=3):
		# Timer thread
		self.process_sequence = process_sequence
		self.time_run = True
		self.time_prev = time.time()
		self.time_period_sec = timeout_sec
		self.time_thread = Thread(target=self._timer)

	def stop(self):
		self.time_run = False
		self.time_thread.join()

	def __del__(self):
		self.stop()

	def start(self):
		self.time_run = True
		self.time_thread.start()

	def _timer(self):
		while self.time_run:
			time.sleep(self.time_period_sec)
			now = time.time()
			for h in self.process_sequence:
				h.on_iter(now - self.time_prev)

			self.time_prev = now


@dataclass
class LogHandle(Handle):
	context: Context

	def __post_init__(self):
		Handle.__init__(self)

	def _log(self, *args):
		Logging.info(*args, "context", self.context.address)

	def on_register(self, port, hull):
		self._log(LogHandle, LogHandle.on_register, "port", port, "hull", hull)

	def on_self(self, hull_number):
		self._log(LogHandle, LogHandle.on_self, "hull", hull_number)

	def on_connection(self, ip, port, hull_number):
		self._log(LogHandle, LogHandle.on_connection, "ip", ip, "port", port, "hull", hull_number)

	def on_keepalive(self):
		self._log(LogHandle, LogHandle.on_keepalive)

	def on_data(self, data: str):
		self._log(LogHandle, LogHandle.on_data, f'"{data}"')


@dataclass
class RegisterHandle(Handle):
	state: State
	context: Context

	def on_register(self, port, hull_number):
		Logging.info(__file__, RegisterHandle, "new client", "ip", self.context.address[0], "port", port, "hull",
			hull_number)
		self.state.update_peer(self.context.address[0], port, hull_number)
		self.context.connection.sendall(parser.marshalling("self", HULL_NUMBER))

		for peer in self.state.peers.values():
			if peer.address == self.context.address:
				continue

			Logging.info(__file__, RegisterHandle, "sending connection", "address", peer.address, "hull", peer.hull_number)
			self.context.connection.sendall(parser.marshalling("connection", *peer.address, peer.hull_number))


@dataclass
class FakeConnHandle(Handle):
	state: State
	context: Context

	def on_register(self, port, hull_number):
		Logging.info(__file__, FakeConnHandle, "new client", "ip", self.context.address[0], "port", port, "hull", hull_number)
		self.state.update_peer(self.context.address[0], port, hull_number)
		self.context.connection.sendall(parser.marshalling("self", HULL_NUMBER))

		for i in range(1, 9):
			time.sleep(.2)
			hull = int(str(i) * 3)  # 1 -> 111, 2 -> 222...
			Logging.info(__file__, FakeConnHandle, "sending fake connection", "hull", hull)
			self.context.connection.sendall(parser.marshalling("connection", *self.context.address, hull))


@dataclass
class RegisterCli(Cli):
	context: Context

	def __post_init__(self):
		Cli.__init__(self)

	def on_cli(self, *args):
		if args[0] == "register":
			Logging.info(__file__, RegisterCli, "sending regsiter")
			self.context.connection.sendall(parser.marshalling("register", 8889, HULL_NUMBER_CLI))


@dataclass
class EchoCli(Cli):
	context: Context

	def __post_init__(self):
		Cli.__init__(self)

	def on_cli(self, *args):
		if args[0] == "echo" and len(args) > 1:
			Logging.info(__file__, EchoCli, "sending echo", args)
			self.context.connection.sendall(parser.marshalling("data", " ".join(args[1:])))


@dataclass
class Proto:
	state: State
	context: Context

	def __post_init__(self):
		self.process_sequence = [
			self.state,
			LogHandle(self.context),
			RegisterHandle(self.state, self.context),
		]
		self.cli = [
			EchoCli(self.context),
			RegisterCli(self.context),
		]

	def _process_received(self, data):
		assert(len(data))
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

	def _iter(self):
		data = self.context.connection.recv(128)

		if not len(data):
			return False

		self._process_received(data)

		return True

	def run(self):
		Logging.info(Proto, Proto.run, "serving", self.context)

		while self._iter():
			pass

		Logging.info(Proto, Proto.run, "finished serving", self.context)


class _Detail:
	state = State()


def tcp_handle(conn, addr):
	proto = Proto(state=_Detail.state, context=Context(connection=conn, address=addr))
	proto.run()


def cli(*args):
	Cli.call(*args)
