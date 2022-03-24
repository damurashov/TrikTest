import server
import trik


if __name__ == "__main__":
	server.start(trik.tcp_handle)
	while True:
		pass