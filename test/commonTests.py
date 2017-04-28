import unittest
import common

class TestCommonTaggedWord(unittest.TestCase):
	def test_repr(self):
		tagged = common.TaggedWord("foo", "bar")
		actual = repr(tagged)
		expected = "bar foo"
		self.assertEquals(actual, expected)
		self.assertEquals(str(tagged), expected)

	def test_eq(self):
		a = common.TaggedWord("foo", "bar")
		b = common.TaggedWord("foo", "bar")
		c = common.TaggedWord("bar", "foo")

		self.assertEquals(a, b)
		self.assertEquals(b, a)
		self.assertNotEquals(a, c)

if __name__ == "__main__":
	unittest.main() 
