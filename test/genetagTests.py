import unittest
import common
import genetag

class TestGenetagSentence(unittest.TestCase):
	def test_tokenize(self):
		s = genetag.Sentence("", "The quick brown fox.")
		actual = s.tokenize(s.text)
		expected = { 0 : "The", 4 : "quick", 10 : "brown", 16 : "fox" }

		self.assertEquals(actual, expected)

	def test_getTagged(self):
		s = genetag.Sentence("", "the quick brown fox.")
		s.addGene(genetag.Gene("", 4, 14, "quick brown"))

		actual = s.getTagged()

		expected = [
			common.TaggedWord("the", "O"),
			common.TaggedWord("quick", "B"),
			common.TaggedWord("brown", "I"),
			common.TaggedWord("fox", "O")
		]

		self.assertEquals(actual, expected)

if __name__ == "__main__":
	unittest.main() 
