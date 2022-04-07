import server, trik, client
from generic import Logging
import sys


if __name__ == "__main__":
	if sys.argv[1] == "server":
		server.start(trik.tcp_handle, 8889)
	elif sys.argv[1] == "client":
		client.async_connect("192.168.4.1", 8889, trik.tcp_handle)
	else:
		print("wrong args")
		exit(0)

	while True:
		command = input("> ")
		command = command.split(" ")
		command = [c.strip() for c in command]
		Logging.debug(__file__, "command", command)
		trik.cli(*command)
