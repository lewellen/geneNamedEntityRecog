class TaggedWord:
	def __init__(self, word, tag):
		self.word = word.strip()
		self.tag = tag

	def __repr__(self):
		return "%s/%s" % (self.tag, self.word)

	def __eq__(self, other):
		if other is None:
			return False

		return (self.word == other.word) and (self.tag == other.tag)

class TaggedSentence:
    def __init__(self, taggedWords = []):
        self.taggedWords = taggedWords

    def toWordSeq(self):
        return map(lambda x: x.word, self.taggedWords)

    def toTagSeq(self):
        return map(lambda x: x.tag, self.taggedWords)

    def __repr__(self):
        return " ".join(map(str, self.taggedWords))

class Sentence:
    def __init__(self, words):
        self.words = words

    def __repr__(self):
        return " ".join(self.words)

class LabeledFormat:
    def deserialize(self, filePath):
        taggedSentence = TaggedSentence([])
        with open(filePath, 'rb') as f:
            for line in f:
                line = line.strip('\n')
                if len(line) == 0:
                    if len(taggedSentence.taggedWords) > 0:
                        yield taggedSentence
                    taggedSentence = TaggedSentence([])
                else:
                    parts = line.split('\t')                      
                    taggedSentence.taggedWords.append(common.TaggedWord(parts[1], parts[0]))
            
            if len(taggedSentence.taggedWords) > 0:
                yield taggedSentence
                    
    def getGenes(self, taggedSentence):
	# Put this here instead of TaggedSentence since the tags for a gene are 
	# specific to this format.
        genes = []
        
        gene = ""
        for curr in taggedSentence.taggedWords:
            if curr.tag == 'B':
                gene = curr.word
            elif curr.tag == 'I':
                gene = gene + " " + curr.word
            elif curr.tag == 'O':
                if len(gene) > 0:
                    genes.append(gene)
                    gene = ""
        
        if len(gene) > 0:
            genes.append(gene)
        
        return genes

    def serialize(self, taggedSentences, filepath):
        with open(filepath, 'wb') as f:
            for taggedSentence in taggedSentences:
                for taggedWord in taggedSentence.taggedWords:
                    f.write(taggedWord.tag + "\t" + taggedWord.word)
                    f.write("\n")
                f.write("\n")

class UnlabeledFormat:
    def deserialize(self, filePath):
        sentence = Sentence([])
        with open(filePath, 'rb') as f:
            for line in f:
                line = line.strip('\n')
                if len(line) == 0:
                    if len(sentence.words) > 0:
                        yield sentence
                    sentence = Sentence([])
                else:
                    sentence.words.append(line)

            if len(sentence.words) > 0:
                yield sentence
                
    def serialize(self, sentences, filepath):
        with open(filepath, 'wb') as f:
            for sentence in sentences:
                for word in sentence.words:
                    f.write(word)
                    f.write("\n")
                f.write("\n")
