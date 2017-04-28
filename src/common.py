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

class TaggedFormat:
	def __init__(self):
		pass
	
	def save(self, filePath, sentences):
		with open(filePath, "w") as f:
			for sentence in sentences:
				for tagged in sentence:
					f.write("%s %s\n" % (tagged.tag, tagged.word))
				f.write("\n")

