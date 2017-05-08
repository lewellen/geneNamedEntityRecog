import re
import xml.dom.minidom

import common

class XmlFormat:
	def __init__(self):
		self.puncAndSpace = re.compile("[^A-Za-z0-9]+")
		pass

	def deserialize(self, filePath):
		tree = xml.dom.minidom.parse(filePath)
		return [ self.__XmlSentenceToTaggedSentence(sentenceElem) for sentenceElem in tree.getElementsByTagName("sentence") ]

	def __XmlSentenceToTaggedSentence(self, sentenceElem):
		return common.TaggedSentence( [ taggedWord for child in sentenceElem.childNodes for taggedWord in self.__XmlSentenceChildToTaggedWords(child) ] )

	def __XmlSentenceChildToTaggedWords(self, child):
		text = ""
		textType = None
		if child.nodeType == child.TEXT_NODE:
			text = child.nodeValue
			textType = "text"
		elif child.nodeType == child.ELEMENT_NODE:
			if child.nodeName == "cons":
				text = child.getAttribute("lex")
				textType = "gene"
			else:
				assert False

		taggedWords = []
		tokens = self.puncAndSpace.split(text)
		if textType == "text":
			taggedWords += map(lambda word: common.TaggedWord(word, "O"), tokens)
		else:
			taggedWords += [ common.TaggedWord(tokens[0], "I") ]
			taggedWords += map(lambda word: common.TaggedWord(word, "I"), tokens[1:])
	
		return filter(lambda taggedWord: len(taggedWord.word) > 0, taggedWords)
