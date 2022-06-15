
function sleep(millis)
{
    var date = new Date();
    var curDate = null;
    do { curDate = new Date(); }
    while(curDate-date < millis);
}

var sendReceive = function(hull, message, millis)
{
	print("sending " + message);
	mailbox.send(hull, message);
	print(mailbox.receive());
	sleep(millis);
}

var main = function() {
	mailbox.connect("192.168.4.1", 8889);
	sleep(300);

	sendReceive(42, "arm", 1000);
	sendReceive(42, "takeoff", 12000);
	sendReceive(42, "forward", 8000);
	sendReceive(42, "land", 8000);
	sendReceive(42, "done", 1);
}
