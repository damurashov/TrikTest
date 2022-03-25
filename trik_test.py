from trik import Proto, Handle, PeriodTrigger, get_state as trik_get_state, Context
import parser
from generic import Logging
import unittest


class TestProto(Proto):
	registry = list()

	def on_command(self, s: str):
		pass


def command(s: str):
	Logging.debug(__file__, 'command')
	s = s.strip()
	for t in TestProto.registry:
		t.on_command(s)


class TestRegisterClientProto(Proto, Handle, unittest.TestCase):
	def __post_init__(self):
		TestProto.__post_init__(self)
		self.process_sequence = [self.state, self]
		self.period_trigger = PeriodTrigger(self.process_sequence, timeout_sec=10)
		self.period_trigger.start()

		self.flag = False
		self.got_self = False
		self.got_connection = False

	def on_iter(self, time_delta_sec):
		self.assertTrue(self.got_self and self.got_connection)
		self.flag = True

	def on_command(self, command: str):
		if command == "register":
			self.flag = True
			Logging.info(__file__, TestRegisterClientProto, "launched")

	def on_self(self, hull_number):
		self.got_self = True
		Logging.info(__file__, TestRegisterClientProto, "self")

	def on_connection(self, ip, port, hull_number):
		self.got_connection = True
		Logging.info(__file__, TestRegisterClientProto, "connection")

	def run_blocking(self):
		Logging.info(__file__, TestRegisterClientProto, "started, waiting for command")

		while not self.flag:
			pass

		Logging.debug(__file__, TestRegisterClientProto, "sending")
		self.context.connection.sendall(parser.marshalling("register", self.context.get_host_port(), 4))

		self.flag = False

		while not self.flag:
			data = self.context.connection.recv(128)
			self._process_received(data)


def handle_run_test_register(conn, addr):
	TestProto.registry.append(TestRegisterClientProto(trik_get_state(), Context(conn, addr)))
	TestProto.registry[-1].run_blocking()