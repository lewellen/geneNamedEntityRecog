import genetag

if __name__ == "__main__":
	corpusFilePath = "res/genetag/genetag.sent"
	groundTruthFilePath = "res/genetag/Correct.data"
	outputFilePath = "res/genetag.iob"

	sentFormat = genetag.SentenceFormat()
	sentences = sentFormat.load(corpusFilePath)

	geneFormat = genetag.GeneFormat()
	genes = geneFormat.load(groundTruthFilePath)

	for gene in genes:
		sentences[gene.sentId].addGene(gene)

	taggedSentences = [ sentences[sentId].getTagged() for sentId in sentences ]

	taggedFormat = genetag.TaggedFormat()
	taggedFormat.save(outputFilePath, taggedSentences)
