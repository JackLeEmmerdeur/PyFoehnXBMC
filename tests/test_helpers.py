import unittest
from resources.lib.helpers import check_int_ranges, are_integerishs


class HelpersTest(unittest.TestCase):
	def test_are_integerishs(self):
		self.assertEqual(are_integerishs("19", 42, -1, 1.1, "2.2"), True, "first seq not numberish")
		self.assertEqual(are_integerishs("a", 0), False, "second seq numberish")

	def test_check_int_ranges(self):
		numbers = [10, 2, 5]
		names = ["a", "b", "c"]
		try:
			x = check_int_ranges(
				numbers,
				[[1, 11], [3, 7], [6, 10]],
				names
			)
			self.assertEqual(x, "b", "Wrong name of number, should be b")
			x = check_int_ranges(
				numbers,
				[[1, 11], [2, 9], [1, 4]]
			)
			self.assertEqual(x, 2)
			try:
				x = check_int_ranges(
					numbers,
					[[1, 11]],
					names
				)
			except:
				pass
			else:
				self.assertEqual(0, 1, "No exception was thrown")
		except Exception as e:
			self.assertEqual(0, 1, e)
