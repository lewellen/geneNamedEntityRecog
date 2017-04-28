import common
import genetag

if __name__ == "__main__":
	corpusFilePath = "res/genetag/genetag.tag"
	labeledFilePath = "res/genetag.labeled"
	unlabeledFilePath = "res/genetag.unlabeled"

	inputFormat = genetag.TagFormat()

	taggedSentences = inputFormat.deserialize(corpusFilePath)
	labeledFormat = common.LabeledFormat()
	labeledFormat.serialize(taggedSentences, labeledFilePath)

	sentences = [ common.Sentence(taggedSentence.toWordSeq()) for taggedSentence in taggedSentences ]
	unlabeledFormat = common.UnlabeledFormat()
	unlabeledFormat.serialize(sentences, unlabeledFilePath)	
