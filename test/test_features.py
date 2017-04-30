import unittest

from src import features

class PositiveNegativeFeatureTest:
	def test_positive(self):
		feature = self.getFeature()
		candidates = self.getPositiveExamples()
		for candidate in candidates:
			wasMatch, matchedWith = feature.hasFeature(candidate)
			if not wasMatch:
				print(
					"%s should accept \"%s\", matched with \"%s\"" % 
					(feature.getName(), str(candidate), str(matchedWith)) 
				)

			self.assertTrue(wasMatch)

	def test_negative(self):
		feature = self.getFeature()
		candidates = self.getNegativeExamples()
		for candidate in candidates:
			wasMatch, matchedWith = feature.hasFeature(candidate)
			if wasMatch:
				print(
					"%s should not accept \"%s\", matched with \"%s\"" % 
					(feature.getName(), str(candidate), str(matchedWith)) 
				)

			self.assertFalse(wasMatch)

class AllLowerLettersFeatureTest(unittest.TestCase, PositiveNegativeFeatureTest):
	def getFeature(self):
		return features.AllLowerLettersFeature()

	def getPositiveExamples(self):
		return [ "a", "be", "cee" ]

	def getNegativeExamples(self):
		return [ "", "Ab", "cD", "efG", "a03", "FOO" ]

class AllUpperLettersFeatureTest(unittest.TestCase, PositiveNegativeFeatureTest):
	def getFeature(self):
		return features.AllUpperLettersFeature()

	def getPositiveExamples(self):
		return [ "A", "BE", "CEE" ]

	def getNegativeExamples(self):
		return [ "", "Ab", "cD", "efG", "a03", "foo" ]

class AlphaNumericFeatureTest(unittest.TestCase, PositiveNegativeFeatureTest):
	def getFeature(self):
		return features.AlphaNumericFeature()

	def getPositiveExamples(self):
		return [ "a0", "B1", "1de2Ed" ]

	def getNegativeExamples(self):
		return [ "", "a", "0" ]

class CapitalizedFeatureTest(unittest.TestCase, PositiveNegativeFeatureTest):
	def getFeature(self):
		return features.CapitalizedFeature()

	def getPositiveExamples(self):
		return [ "A", "All" ]

	def getNegativeExamples(self):
		return [ "", "0", "0.1", "ALL", "C3P0" ]

class PositiveIntegerFeatureTest(unittest.TestCase, PositiveNegativeFeatureTest):
	def getFeature(self):
		return features.PositiveIntegerFeature()

	def getPositiveExamples(self):
		return [ "1", "+2", "3", "+45", "67", "+8910" ]

	def getNegativeExamples(self):
		return [ "", "0.1", "-1", "foo", "inf", "one", "" ]

class PuncFeatureTest(unittest.TestCase, PositiveNegativeFeatureTest):
	def getFeature(self):
		return features.PuncFeature()

	def getPositiveExamples(self):
		return [ ".", "[", "," ]

	def getNegativeExamples(self):
		return [ "", "a", "0" ]

class RomanNumFeatureTest(unittest.TestCase, PositiveNegativeFeatureTest):
	def getFeature(self):
		return features.RomanNumFeature()

	def getPositiveExamples(self):
		return [ "I", "II", "III", "IVXV", "VIXVIII", "MMMMMMMMCMX" ]

	def getNegativeExamples(self):
		return [ "", "0.1", "-1", "foo", "inf", "one", "" ]

class EnglishSuffixFeatureTest(unittest.TestCase, PositiveNegativeFeatureTest):
	def getFeature(self):
		return features.EnglishSuffixFeature()

	def getPositiveExamples(self):
		return [ "watergate", "freeform", "biology", "freezing" ]

	def getNegativeExamples(self):
		return []

class LatinSuffixFeatureTest(unittest.TestCase, PositiveNegativeFeatureTest):
	def getFeature(self):
		return features.LatinSuffixFeature()

	def getPositiveExamples(self):
		return [ "dolor", "amet" ]

	def getNegativeExamples(self):
		return [ "Lorem" ]

class LatinPrefixFeatureTest(unittest.TestCase, PositiveNegativeFeatureTest):
	def getFeature(self):
		return features.LatinPrefixFeature()

	def getPositiveExamples(self):
		return [ "abnormal", "circumvent", "extrovert" ]

	def getNegativeExamples(self):
		return [ "xor", "metric", "", "foo" ]

class GreekLetterFeatureTest(unittest.TestCase, PositiveNegativeFeatureTest):
	def getFeature(self):
		return features.GreekLetterFeature()

	def getPositiveExamples(self):
		return [ "alpha", "mu", "gamma" ]

	def getNegativeExamples(self):
		return [ "xor", "metric", "", "foo" ]

class DeterminerFeatureTest(unittest.TestCase, PositiveNegativeFeatureTest):
	def getFeature(self):
		return features.DeterminerFeature()

	def getPositiveExamples(self):
		return [ "the", "this", "that" ]

	def getNegativeExamples(self):
		return [ "xor", "metric", "", "foo" ]

class PrepositionFeatureTest(unittest.TestCase, PositiveNegativeFeatureTest):
	def getFeature(self):
		return features.PrepositionFeature()

	def getPositiveExamples(self):
		return [ "of", "about", "by" ]

	def getNegativeExamples(self):
		return [ "xor", "metric", "", "foo" ]

if __name__ == "__main__":
	unittest.main()
