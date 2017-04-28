import common
import genetag

if __name__ == "__main__":
	corpusFilePath = "res/genetag/genetag.tag"
	taggedFilePath = "res/genetag.tagged"
	untaggedFilePath = "res/genetag.untagged"

	inputFormat = genetag.TagFormat()
	taggedSentences = inputFormat.load(corpusFilePath)

	outputFormat = common.GoldFormat()
	outputFormat.saveWithTags(taggedFilePath, taggedSentences)
	outputFormat.saveWithoutTags(untaggedFilePath, taggedSentences)
