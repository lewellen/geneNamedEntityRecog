import common
import genia

if __name__ == "__main__":
	corpusFilePath = "res/genia/GENIAcorpus3.02.xml"
	labeledFilePath = "res/genia.labeled"
	unlabeledFilePath = "res/genia.unlabeled"

	inputFormat = genia.XmlFormat()

	taggedSentences = inputFormat.deserialize(corpusFilePath)
	labeledFormat = common.LabeledFormat()
	labeledFormat.serialize(taggedSentences, labeledFilePath)

	sentences = [ common.Sentence(taggedSentence.toWordSeq()) for taggedSentence in taggedSentences ]
	unlabeledFormat = common.UnlabeledFormat()
	unlabeledFormat.serialize(sentences, unlabeledFilePath)	
