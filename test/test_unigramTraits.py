import unittest

from src import unigramTraits

class PositiveNegativeUnigramTraitTest:
	def test_positive(self):
		unigramTrait = self.getUnigramTrait()
		candidates = self.getPositiveExamples()
		for candidate in candidates:
			wasMatch, matchedWith = unigramTrait.isAMatch(candidate)
			if not wasMatch:
				print(
					"%s should accept \"%s\", matched with \"%s\"" % 
					(unigramTrait.getName(), str(candidate), str(matchedWith)) 
				)

			self.assertTrue(wasMatch)

	def test_negative(self):
		unigramTrait = self.getUnigramTrait()
		candidates = self.getNegativeExamples()
		for candidate in candidates:
			wasMatch, matchedWith = unigramTrait.isAMatch(candidate)
			if wasMatch:
				print(
					"%s should not accept \"%s\", matched with \"%s\"" % 
					(unigramTrait.getName(), str(candidate), str(matchedWith)) 
				)

			self.assertFalse(wasMatch)

class AllLowerLettersUnigramTraitTest(unittest.TestCase, PositiveNegativeUnigramTraitTest):
	def getUnigramTrait(self):
		return unigramTraits.AllLowerLettersUnigramTrait()

	def getPositiveExamples(self):
		return [ "a", "be", "cee" ]

	def getNegativeExamples(self):
		return [ "", "Ab", "cD", "efG", "a03", "FOO" ]

class AllUpperLettersUnigramTraitTest(unittest.TestCase, PositiveNegativeUnigramTraitTest):
	def getUnigramTrait(self):
		return unigramTraits.AllUpperLettersUnigramTrait()

	def getPositiveExamples(self):
		return [ "A", "BE", "CEE" ]

	def getNegativeExamples(self):
		return [ "", "Ab", "cD", "efG", "a03", "foo" ]

class AlphaNumericUnigramTraitTest(unittest.TestCase, PositiveNegativeUnigramTraitTest):
	def getUnigramTrait(self):
		return unigramTraits.AlphaNumericUnigramTrait()

	def getPositiveExamples(self):
		return [ "a0", "B1", "1de2Ed" ]

	def getNegativeExamples(self):
		return [ "", "a", "0" ]

class CapitalizedUnigramTraitTest(unittest.TestCase, PositiveNegativeUnigramTraitTest):
	def getUnigramTrait(self):
		return unigramTraits.CapitalizedUnigramTrait()

	def getPositiveExamples(self):
		return [ "A", "All" ]

	def getNegativeExamples(self):
		return [ "", "0", "0.1", "ALL", "C3P0" ]

class PositiveIntegerUnigramTraitTest(unittest.TestCase, PositiveNegativeUnigramTraitTest):
	def getUnigramTrait(self):
		return unigramTraits.PositiveIntegerUnigramTrait()

	def getPositiveExamples(self):
		return [ "1", "+2", "3", "+45", "67", "+8910" ]

	def getNegativeExamples(self):
		return [ "", "0.1", "-1", "foo", "inf", "one", "" ]

class PositiveRealUnigramTraitTest(unittest.TestCase, PositiveNegativeUnigramTraitTest):
	def getUnigramTrait(self):
		return unigramTraits.PositiveRealUnigramTrait()

	def getPositiveExamples(self):
		return [ "0.12", "3.4", "+5.67", "891.0"]

	def getNegativeExamples(self):
		return [ "", "0", "-1", "foo", "inf", "one" ]

class PuncUnigramTraitTest(unittest.TestCase, PositiveNegativeUnigramTraitTest):
	def getUnigramTrait(self):
		return unigramTraits.PuncUnigramTrait()

	def getPositiveExamples(self):
		return [ ".", "[", "," ]

	def getNegativeExamples(self):
		return [ "", "a", "0" ]

class RomanNumUnigramTraitTest(unittest.TestCase, PositiveNegativeUnigramTraitTest):
	def getUnigramTrait(self):
		return unigramTraits.RomanNumUnigramTrait()

	def getPositiveExamples(self):
		return [ "I", "II", "III", "IVXV", "VIXVIII", "MMMMMMMMCMX" ]

	def getNegativeExamples(self):
		return [ "", "0.1", "-1", "foo", "inf", "one", "" ]

class EnglishSuffixUnigramTraitTest(unittest.TestCase, PositiveNegativeUnigramTraitTest):
	def getUnigramTrait(self):
		return unigramTraits.EnglishSuffixUnigramTrait()

	def getPositiveExamples(self):
		return [ "watergate", "freeform", "biology", "freezing" ]

	def getNegativeExamples(self):
		return []

class LatinSuffixUnigramTraitTest(unittest.TestCase, PositiveNegativeUnigramTraitTest):
	def getUnigramTrait(self):
		return unigramTraits.LatinSuffixUnigramTrait()

	def getPositiveExamples(self):
		return [ "dolor", "amet" ]

	def getNegativeExamples(self):
		return [ "Lorem" ]

class LatinPrefixUnigramTraitTest(unittest.TestCase, PositiveNegativeUnigramTraitTest):
	def getUnigramTrait(self):
		return unigramTraits.LatinPrefixUnigramTrait()

	def getPositiveExamples(self):
		return [ "abnormal", "circumvent", "extrovert" ]

	def getNegativeExamples(self):
		return [ "xor", "metric", "", "foo" ]

class GreekLetterUnigramTraitTest(unittest.TestCase, PositiveNegativeUnigramTraitTest):
	def getUnigramTrait(self):
		return unigramTraits.GreekLetterUnigramTrait()

	def getPositiveExamples(self):
		return [ "alpha", "mu", "gamma" ]

	def getNegativeExamples(self):
		return [ "xor", "metric", "", "foo" ]

class DeterminerUnigramTraitTest(unittest.TestCase, PositiveNegativeUnigramTraitTest):
	def getUnigramTrait(self):
		return unigramTraits.DeterminerUnigramTrait()

	def getPositiveExamples(self):
		return [ "the", "this", "that" ]

	def getNegativeExamples(self):
		return [ "xor", "metric", "", "foo" ]

class PrepositionUnigramTraitTest(unittest.TestCase, PositiveNegativeUnigramTraitTest):
	def getUnigramTrait(self):
		return unigramTraits.PrepositionUnigramTrait()

	def getPositiveExamples(self):
		return [ "of", "about", "by" ]

	def getNegativeExamples(self):
		return [ "xor", "metric", "", "foo" ]

class ConjunctionUnigramTraitTest(unittest.TestCase, PositiveNegativeUnigramTraitTest):
	def getUnigramTrait(self):
		return unigramTraits.ConjunctionUnigramTrait()

	def getPositiveExamples(self):
		return [ "and", "or", "but" ]

	def getNegativeExamples(self):
		return [ "xor", "metric", "", "foo" ]

if __name__ == "__main__":
	unittest.main()
