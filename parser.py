from generic import Logging

# Message lengths w/o "length" and "message type" fields
LENGTH_TABLE = {
	"register": 2,
	"self": 1,
	"connection": 3,
	"keepalive": 0,
	"data": 1,
}
assert type(LENGTH_TABLE["keepalive"]) is int

def unmarshalling(s):
	s = s.decode("utf-8").strip()
	ret = s.split(":")

	if len(ret) < 2:
		Logging.warning(__file__, unmarshalling, "wrong sequence", s)
		return None

	if not str(ret[0]).isdigit():
		Logging.warning(__file__, unmarshalling, "non-digit preamble", s, ":", ret[0])
		return None

	if not ret[1] in LENGTH_TABLE.keys():
		Logging.warning(__file__, unmarshalling, "wrong message type", s, ':', ret[1])
		return None

	if len(ret) != LENGTH_TABLE[ret[1]] + 2:
		Logging.warning(__file__, unmarshalling, "wrong message length", s, ":", len(ret), "expected", LENGTH_TABLE[ret[1]])
		return None

	# Logging.debug(__file__, unmarshalling, "got data", ret)

	return ret[1:]


def marshalling(*args):
	"""
	:param args: Packs a message, adds preamble and delimiters. E.g "keepalive" -> "9:keepalive"
	"""
	assert(len(args))

	if not len(args):
		Logging.warning(__file__, marshalling, "wrong number of arguments", *args)

	if args[0] not in LENGTH_TABLE.keys():
		Logging.warning(__file__, marshalling, "wrong message type", *args)

	if len(args) - 1 != LENGTH_TABLE[args[0]]:
		Logging.warning(__file__, marshalling, "wrong message length", *args)

	ret = ":".join([str(a) for a in args])
	ret = str(len(ret)) + ":" + ret

	# Logging.debug(__file__, marshalling, "payload", ret)

	return str.encode(ret)
