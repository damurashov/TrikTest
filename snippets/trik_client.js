
var main = function() {
	mailbox.connect("192.168.4.1", 8889);

	for (var i = 0; i < 10; ++i) {
		print("sending " + i);
		mailbox.send(42, "echo " + i);

		print("receiving " + i);
		message = mailbox.receive();

		print(message);
	}
}
