from generic import Logging


def unmarshalling(s: str):
	ret = s.split(":")

	if len(ret) > 1:
		return ret[1:]
	else:
		Logging.warning(__file__, unmarshalling, "non-mailbox sequence", s)
		return None


def marshalling(*args):
	assert(len(args))
	ret = ":".join([str(a) for a in args])
	ret = str(len(ret)) + ":" + ret
	return ret
