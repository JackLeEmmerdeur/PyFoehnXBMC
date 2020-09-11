# from os.path import isfile  # , expanduser as opexpanduser, join as opjoin, dirname as opdirname
# from six import string_types, text_type
# from re import findall
# from sys import exc_info
# from traceback import format_exception
from traceback import format_exception
from sys import exc_info
from re import findall
from subprocess import Popen, PIPE


def is_string(var):
	return isinstance(var, str)


def is_boolean(var):
	return isinstance(var, bool)


def is_integer(var):
	return isinstance(var, int)


def are_integerishs(*numbers):
	if is_empty_sequence(numbers):
		return False
	else:
		length = len(numbers)
		t = True
		for i in range(0, length):
			if not is_integerish(numbers[i]):
				t = False
				break
		return t


def is_integerish(var):
	"""stackoverflow.com/questions/1265665/python-check-if-a-string-represents-an-int-without-using-try-except"""
	i = str(var)
	return i == '0' or (i if i.find('..') > -1 else i.lstrip('-+').rstrip('0').rstrip('.')).isdigit()


def is_empty_sequence(sequencevar):
	return not is_sequence(sequencevar) or len(sequencevar) == 0


def is_sequence(var):
	"""
	Tests if var is a sequenzish instance (list or tuple)
	:param var: The possible sequence instance
	:return: True if var is a sequence instance
	"""
	return (
		not hasattr(var, "strip") and
		hasattr(var, "__getitem__") or
		hasattr(var, "__iter__")
	)


def string_is_empty(
		thetext,
		preserve_whitespace=False,
		check_strip_availability=False
):
	"""
	Checks if `thetext` is emtpy and returns True if so.

	Example:
	>>> string_is_empty("  ")
	True
	>>> string_is_empty("  ", True)
	False
	>>> string_is_empty("  ", False)
	True

	:param thetext: The string to check for emptiness
	:param preserve_whitespace: If True, blankspaces will not count as empty
	:param check_strip_availability: Checks if `thetext is a string-type via availability of strip-method (esotheric)
	:return: True if `thetext` is empty
	:rtype: bool
	"""
	if thetext is None:
		return True
	isstring = False
	if check_strip_availability:
		isstring = hasattr(thetext, "strip")
	elif is_string(thetext):
		isstring = True
	if isstring or isinstance(thetext, bytes):
		return len(thetext if preserve_whitespace else thetext.strip()) < 1
	else:
		return True


def check_int_range(obj, low, high):
	i = None
	if is_string(obj):
		if is_integerish(obj):
			i = int(obj)
	elif is_integer(obj):
		i = obj
	if i is None:
		return False
	return i < low or i > high


def check_int_ranges(numbers, ranges, names=None):
	if not is_sequence(numbers) or not is_sequence(ranges):
		raise Exception("numbers- or ranges parameter is not a sequence")
	length = len(numbers)
	if length != len(ranges):
		raise Exception("numbers- and ranges-sequences don't match length")
	k = None
	use_names = is_sequence(names) and len(names) == length
	for j in range(0, length):
		r = ranges[j]
		n = numbers[j]
		if not is_integer(n):
			if not is_integerish(n):
				raise Exception("Number {} is not acceptable".format(n))
			n = int(n)

		if not is_sequence(r) or len(r) != 2 or \
			not is_integer(r[0]) or not is_integer(r[1]) or r[0] > r[1]:
			raise Exception("Range {} is not acceptable".format(r))

		if not(r[0] <= n <= r[1]):
			if use_names is True:
				k = names[j]
			else:
				k = j
			break
	return k


def get_reformatted_exception(msg, e):
	tb = ""
	excfmtlist = format_exception(type(e), e, exc_info()[2])
	for (index, excfmtitem) in enumerate(excfmtlist):
		if index > 0:
			tb += "\n"
		tb += "\t" + excfmtitem
	return "{}\n{}".format(msg, tb)


def parse_multi_dim_sequence_str(multi_dim_sequence, mapfunc):
	seq = []
	subseqstrs = findall('\[\d*,\s?\d*\]', multi_dim_sequence)
	for subseqstr in subseqstrs:
		subseq = findall('\d+', subseqstr)
		if mapfunc is not None:
			seq.append(mapfunc(subseq))
		else:
			seq.append(subseq)
	return seq


def parse_sequence_str(seqstr, mapfunc=None):
	seqs = findall('\d+', seqstr)
	if mapfunc is not None:
		seqs = list(map(lambda x: mapfunc(x), seqs))
	return seqs


def get_soctemp(is_pi=True):
	if is_pi is True:
		p = Popen(["cat", "/sys/class/thermal/thermal_zone0/temp"], stdout=PIPE, stderr=PIPE)
		output, err = p.communicate()
		if p.returncode == 0:
			return round(float(output) / 1000, 2)
		else:
			raise Exception(err)
	else:
		from codecs import decode
		p1 = Popen(["sensors"], stdout=PIPE)
		p2 = Popen(["grep", "temp2", "-m1"], stdin=p1.stdout, stdout=PIPE)
		p1.stdout.close()
		p3 = Popen(["cut", "-c16-19"], stdin=p2.stdout, stdout=PIPE)
		p2.stdout.close()
		return float(decode(p3.communicate()[0]))
