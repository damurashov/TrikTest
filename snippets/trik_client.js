
mailbox.connect("192.168.4.1", 8889);

for (let i = 0; i < 10; ++i) {
	print("sending " + i);
	mailbox.send(42, "echo " + i);

	print("receiving " + i);
	message = mailbox.receive();

	print(message);
}
