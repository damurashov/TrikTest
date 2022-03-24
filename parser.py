from generic import Logging

# Message lengths w/o "length" and "message type" fields
LENGTH_TABLE = {
	"register": 2,
	"self": 1,
	"connection": 3,
	"keepalive": 0,
	"data": 1,
}

def unmarshalling(s: str):
	ret = s.split(":")

	if not len(ret):
		Logging.warning(__file__, unmarshalling, "wrong sequence", s)
		return None

	if not str(ret[0]).isdigit():
		Logging.warning(__file__, unmarshalling, "non-digit preamble", s)
		return None

	if not ret[1] in LENGTH_TABLE.keys():
		Logging.warning(__file__, unmarshalling, "wrong message type", s)
		return None

	if len(ret) != LENGTH_TABLE[ret[1]] - 2:
		Logging.warning(__file__, unmarshalling, "wrong message length", s)

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

	return ret
