import common

class Gene:
	def __init__(self, sentId, startIndex, endIndex, phrase):
		self.sentId = sentId
		self.startIndex = startIndex
		self.endIndex = endIndex
		self.phrase = phrase

class Sentence:
	def __init__(self, sentId, text):
		self.sentId = sentId
		self.text = text
		self.genes = []

	def addGene(self, gene):
		self.genes.append(gene)

	def getTagged(self):
		wordBoundaries = self.tokenize(self.text)

		geneBoundaries = {}
		for gene in self.genes:
			genBound = self.tokenize(gene.phrase)
			for i in genBound:
				value = 'I'
				if i == 0:
					value = 'B'

				geneBoundaries.update( { i + gene.startIndex : value } )

		tagged = []
		sortedKeys = sorted(wordBoundaries.keys())
		for i in sortedKeys:
			tag = 'O'
			if i in geneBoundaries:
				tag = geneBoundaries[i]

			tagged.append(common.TaggedWord(wordBoundaries[i], tag))
	
		return tagged

	def tokenize(self, text):
		tokens = {}
		i, j = 0, 0
		while i >= 0:
			j = i
			i = text.find(' ', j + 1)

			if text[j] == ' ':
				j += 1	

			tokens.update( { j : text[j:i] } )

		return tokens

class GeneFormat:
	def __init__(self):
		pass

	def load(self, filePath):
		genes = []

		with open(filePath) as f:
			for line in f:
				parts = line.strip().split('|')

				sentId = parts[0]			
				indexRange = parts[1].split(' ')
				phrase = parts[2]

				genes.append(Gene(
					sentId, 
					int(indexRange[0]), int(indexRange[1]), 
					phrase
				))

		return genes

class SentenceFormat:
	def __init__(self):
		pass

	def load(self, filePath):
		sentences = {}
		with open(filePath) as f:
			while True:
				key = f.readline().strip()
				value = f.readline().strip()
				if (key == '' and value == '') or (key is None and value is None):
					break

				sentences.update({ key : Sentence(key, value) })

		return sentences

