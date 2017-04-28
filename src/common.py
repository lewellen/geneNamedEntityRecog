class TaggedWord:
	def __init__(self, word, tag):
		self.word = word.strip()
		self.tag = tag

	def __repr__(self):
		return "%s %s" % (self.tag, self.word)

	def __eq__(self, other):
		if other is None:
			return False

		return (self.word == other.word) and (self.tag == other.tag)

class GoldFormat:
	def __init__(self):
		pass
	
	def saveWithTags(self, filePath, taggedSentences):
		with open(filePath, "w") as f:
			for taggedSentence in taggedSentences:
				for tagged in taggedSentence:
					f.write("%s %s\n" % (tagged.tag, tagged.word))
				f.write("\n")

	def saveWithoutTags(slef, filePath, taggedSentences):
		with open(filePath, "w") as f:
			for taggedSentence in taggedSentences:
				for tagged in taggedSentence:
					f.write("%s\n" % (tagged.word))
				f.write("\n")
