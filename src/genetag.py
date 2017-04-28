import common

class TagFormat:
	def __init__(self):
		pass

	def deserialize(self, filePath):
		taggedSentences = []

		with open(filePath) as f:
			while True:
				key = f.readline().strip()
				value = f.readline().strip()
				if (key == '' and value == '') or (key is None and value is None):
					break

				taggedSentences.append(self.__rawToTagged(value))

		return taggedSentences

	def __rawToTagged(self, sentence):
		taggedWords = []

		pTag = None
		rawWords = sentence.split()
		for rawWord in rawWords:
			word = None
			tag = None

			if rawWord.endswith('_TAG'):
				word = rawWord[:-4]
				tag = 'O'					
			elif rawWord.endswith('_GENE1') or rawWord.endswith('_GENE2'):
				word = rawWord[:-6]
				tag = 'B'
			else:
				assert False

			if pTag in ('B', 'I') and tag == 'B':
				tag = 'I'

			pTag = tag

			taggedWords.append(common.TaggedWord(word.strip(), tag))

		return common.TaggedSentence(taggedWords)
