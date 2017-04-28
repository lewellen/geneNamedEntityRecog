import unittest
from src import common

class TestCommonTaggedWord(unittest.TestCase):
	def test_repr(self):
		tagged = common.TaggedWord("word", "tag")
		actual = repr(tagged)
		expected = "tag/word"
		self.assertEquals(actual, expected)
		self.assertEquals(str(tagged), expected)

	def test_eq(self):
		a = common.TaggedWord("foo", "bar")
		b = common.TaggedWord("foo", "bar")
		c = common.TaggedWord("bar", "foo")

		self.assertEquals(a, b)
		self.assertEquals(b, a)
		self.assertNotEquals(a, c)

class TestCommonTaggedSentence(unittest.TestCase):
	def test_toWordSeq(self):
		words = "the quick brown fox.".split()
		tags = range(0, 4)
		
		taggedSentence = common.TaggedSentence( [ 
			common.TaggedWord(word, tag) for (word, tag) in zip(words, tags) 
		] )

		actual = taggedSentence.toWordSeq()

		self.assertEqual(actual, words)

	def test_toTagSeq(self):
		words = "the quick brown fox.".split()
		tags = range(0, 4)
		
		taggedSentence = common.TaggedSentence( [ 
			common.TaggedWord(word, tag) for (word, tag) in zip(words, tags) 
		] )

		actual = taggedSentence.toTagSeq()

		self.assertEqual(actual, tags)

class TestCommonLabeledFormat(unittest.TestCase):
	def test_getGenes(self):
		words = "the quick brown fox.".split()
		tags = ["O", "B", "I", "O"]
		
		taggedSentence = common.TaggedSentence( [ 
			common.TaggedWord(word, tag) for (word, tag) in zip(words, tags) 
		] )

		lFormat = common.LabeledFormat()
		actual = lFormat.getGenes(taggedSentence)
		expected = [ "quick brown" ]

		self.assertEqual(actual, expected)

if __name__ == "__main__":
	unittest.main() 
