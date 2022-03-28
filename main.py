import server, trik, client, trik_test


if __name__ == "__main__":
	server.start(trik.tcp_handle)
	# client.async_connect("192.168.4.1", 8889, trik_test.handle)
	client.async_connect("192.168.4.1", 8889, trik_test.handle_run_test_register)
	while True:
		command = input("> ")
		trik_test.command(command)