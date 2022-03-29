from trik import Proto, Handle, PeriodTrigger, get_state as trik_get_state, Context, HULL_NUMBER
import parser
from generic import Logging


class TestProto(Proto):
	registry = list()

	def on_command(self, s: str):
		pass


def command(s: str):
	Logging.debug(__file__, 'command', s)
	s = s.strip()
	for t in TestProto.registry:
		t.on_command(s)


class TestRegisterClientProto(Proto, Handle):
	def __post_init__(self):
		Proto.__post_init__(self)
		self.timeout_sec = 30
		self.process_sequence = [self.state, self]
		self.period_trigger = PeriodTrigger(self.process_sequence, timeout_sec=self.timeout_sec)
		self.period_trigger.start()

		self.flag = False
		self.got_self = False
		self.got_connection = False

	def on_iter(self, time_delta_sec):
		if not (self.got_self and self.got_connection):
			message = f"Could not get a response in {self.timeout_sec} sec."
			Logging.error(TestRegisterClientProto, message)
			raise Exception(message)

		self.flag = True

	def on_command(self, command: str):
		if command == "register":
			self.flag = True
			Logging.info(__file__, TestRegisterClientProto, "launched")

	def on_self(self, hull_number):
		self.got_self = True
		Logging.info(__file__, TestRegisterClientProto, "self", "hull", hull_number)

	def on_connection(self, ip, port, hull_number):
		self.got_connection = True
		Logging.info(__file__, TestRegisterClientProto, "connection", "ip", ip, "port", port, "hull", hull_number)

	def run_blocking(self):
		Logging.info(__file__, TestRegisterClientProto, "started, waiting for command")

		while not self.flag:
			pass

		Logging.debug(__file__, TestRegisterClientProto, "sending")
		self.context.connection.sendall(parser.marshalling("register", self.context.get_host_port(), 777))

		self.flag = False

		while not self.flag:
			data = self.context.connection.recv(128)
			self._process_received(data)


class EchoHandler(Proto, Handle):

	def __post_init__(self):
		Proto.__post_init__(self)
		self.process_sequence = [self.state, self]

	def on_command(self, command):
		command = [s.strip() for s in command.split()]

		if not len(command) == 2:
			return

		Logging.debug(__file__, EchoHandler, "got message to send")
		if command[0] == "echo":
			self.context.connection.sendall(parser.marshalling("data", command[1]))

	def on_data(self, data: str):
		Logging.debug(__file__, EchoHandler, "got data", f'"{data}"')

	def run_blocking(self):
		self.context.connection.sendall(parser.marshalling("register", 8889, HULL_NUMBER))

		while True:
			self._process_received(self.context.connection.recv(128))


def handle_run_test_register(conn, addr):
	TestProto.registry.append(TestRegisterClientProto(trik_get_state(), Context(conn, addr)))
	TestProto.registry[-1].run_blocking()


def handle_run_test_echo(conn, addr):
	TestProto.registry.append(EchoHandler(trik_get_state(), Context(conn, addr)))
	TestProto.registry[-1].run_blocking()
