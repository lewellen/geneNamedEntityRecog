from random import shuffle, sample, Random

import argparse as ap
import numpy as np
import sys
import re
import csv
from sklearn.linear_model.logistic import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer
from numpy.core.defchararray import lower

import common 
import hiddenMarkovModel as hmm
import evaluation

class TagPredictor:
    def __init__(self, training, featurizer):
        self.vectorizer = CountVectorizer(ngram_range=(1, 3), analyzer=featurizer, binary=True)
        self.model = LogisticRegression()

        self.model.fit(
            self.vectorizer.fit_transform(self.__toSklearnX(training)), 
            list(self.__toSklearnY(training))
            )

    def predictValue(self, word):
        return self.__indexToTag(self.model.predict(self.vectorizer.transform([word]))[0])
    
    def __indexToTag(self, index):
        if(index == 0):
            return "B"
        if(index == 1):
            return "I"
        return "O"
    
    def __tagToIndex(self, tag):
        if(tag == "B"):
            return 0
        if(tag == "I"):
            return 1
        return 2

    def __toSklearnX(self, taggedSentences):
        for taggedSentence in taggedSentences:
            for taggedWord in taggedSentence.taggedWords:
                yield taggedWord.word
                
    def __toSklearnY(self, taggedSentences):
        for taggedSentence in taggedSentences:
            for taggedWord in taggedSentence.taggedWords:
                yield self.__tagToIndex(taggedWord.tag)

class Featurizer:
    def __init__(self):

        self.isPunc = re.compile("^[^\w\s]+$")
        self.containsLetter = re.compile("[A-Z]|[a-z]")
        self.containsNumber = re.compile("[0-9]")
        self.isRomanNumeral = re.compile("^[IVXLCDM]+$")
        self.greekAlphabet = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho", "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega"]

    def __call__(self, word):
        # Features that describe the contents of the string (Motivated by predict:O vs:expect: B)
        if re.search(self.containsLetter, word)  != None and re.search(self.containsNumber, word) != None:
            yield "<C3PO>"
  
        if word.upper() == word:
            yield "<Upper>"
          
        if word.lower() == lower:
            yield "<Lower>"
          
        if word[0].isupper():
            yield "<Proper>"
  
        # Features that describe what the word is (Motivated by predict:O vs expected:I)
        if re.match(self.isPunc, word):
            yield "<Punc>"

        if self.__isNumber(word):
            yield "<Number>"

        if re.match(self.isRomanNumeral, word):
            yield "<Roman>"
  
        if word.lower() in self.greekAlphabet:
            yield "<Greek>"

        # Motivated by (predict:B expected:O)
        yield "<" + str(len(word)) + ">"

        # Poor man's stemming (Baseline)
        x = max(int(0.8 * len(word)), 3)
        yield word[:x].lower()


    def __isNumber(self, x):
        try:
            float(x)
            return True
        except ValueError:
            return False

    def featurize(self, previousWord, currentWord, nextWord):
        return currentWord
            
    def featurizeSentence(self, sentence):
        output = common.Sentence([])
        
        previousWord = None

        for i, currentWord in zip(xrange(len(sentence.words)), sentence.words):
            nextWord = None
            if (i+1 < len(sentence.words)):
                nextWord = sentence.words[i+1]
            
            output.append( self.featurize(previousWord, currentWord, nextWord) )

            previousWord = currentWord

        return output

    def featurizeSentences(self, sentences):
        for sentence in sentences:
            yield self.featurizeSentence(sentence)

    def featurizeTaggedSentence(self, taggedSentence):
        output = common.TaggedSentence()
        output.taggedWords = [];
        
        previousWord = None
        
        for i, taggedWord in zip(xrange(len(taggedSentence.taggedWords)), taggedSentence.taggedWords):
            currentWord = taggedWord.word

            nextWord = None
            if (i + 1 < len(taggedSentence.taggedWords)):
                nextWord = taggedSentence.taggedWords[i + 1].word
            
            output.taggedWords.append( common.TaggedWord(self.featurize(previousWord, currentWord, nextWord), taggedWord.tag)  )

            previousWord = currentWord
            
        return output

    def featurizeTaggedSentences(self, taggedSentences):
        for taggedSentence in taggedSentences:
            yield self.featurizeTaggedSentence(taggedSentence)

def createDecoder(train):
    return hmm.TagDecoder(hmm.CorpusStatistics(train), 1e-8)

def createTrainTest(inputFilePath, trainFilePath, testFilePath):
    fileformat = common.LabeledFormat()
    evaluator = evaluation.Evaluator()
    train, test = evaluator.splitTrainTest(list(fileformat.deserialize(inputFilePath)), 1/5.0)

    fileformat.serialize(train, trainFilePath)
    fileformat.serialize(test, testFilePath)

def removeTags(inputFilePath, outputFilePath):
    inputFormat = common.LabeledFormat()
    outputFormat = common.UnlabeledFormat()
    
    outputFormat.serialize(map(lambda taggedSentence: common.Sentence(taggedSentence.toWordSeq()), inputFormat.deserialize(inputFilePath)), outputFilePath)

def decode(trainFilePath, testFilePath, outputFilePath):   
    # Load the training data
    trainFormat = common.LabeledFormat()
    train = list(trainFormat.deserialize(trainFilePath))

    # Create a decoder that operates over (B I O) values AND tags
    A = [common.TaggedSentence( [ common.TaggedWord(w.tag, w.tag) for w in t.taggedWords] ) for t in train]
    decoder = createDecoder(A)

    # Load up the test data
    testFormat = common.UnlabeledFormat()
    test = list(testFormat.deserialize(testFilePath))

    # For each word in a test sentence, predict its tag
    featurizer = Featurizer()
    classifier = TagPredictor(train, featurizer)
    B = [ common.Sentence( [ classifier.predictValue(w) for w in s.words] ) for s in test]


    # Decode the sentences, and then reassign the actual words to the results
    D = map(lambda x: decoder.decode(x), B)
    for (d, t) in zip(D, test):
        for i in xrange(0, len(t.words)):
            d.taggedWords[i].word = t.words[i]

    # Save to disk
    outputFormat = trainFormat
    outputFormat.serialize(D, outputFilePath)

def evaluate(testFilePath, decodedFilePath): 
    fileFormat = common.LabeledFormat()
    test = list(fileFormat.deserialize(testFilePath))

    decoded = list(fileFormat.deserialize(decodedFilePath))

    numCorrect = 0.0
    numFound = 0.0

    numExpected = 0.0;

    for (t, d) in zip(test, decoded):
        dGenes = fileFormat.getGenes(d)
        dCount = len(dGenes)
        numFound += dCount
        
        tGenes = fileFormat.getGenes(t)
        tCount = len(tGenes)
        numExpected += tCount
        
        #numCorrect += min(dCount, tCount)
        #numCorrect += len(filter(lambda (x,y): x == y, zip(dGenes, tGenes)))
        numCorrect += len(set(dGenes).intersection(set(tGenes)))

    if numFound == 0:
        print("numFound = %d, numCorrect = %d, numExpected = %d" % (numFound, numCorrect, numExpected))
        return
    
    # precision is the ratio of correctly identified genes identified by the 
    # system to the total number of genes your system found.
    precision = numCorrect / numFound

    if numExpected == 0:
        print("numFound = %d, numCorrect = %d, numExpected = %d" % (numFound, numCorrect, numExpected))
        return

    # recall is the ratio of correctly identified genes to the total that you 
    # should have found.
    recall = numCorrect / numExpected

    if precision + recall == 0:
        print("numFound = %d, numExpected = %d" % (numFound, numExpected))
        print("precision = %f, recall = %f" % (precision, recall))
        return

    # The F1 measure given in the book is just the harmonic mean of these two. 
    f1 = 2.0 * precision * recall / (precision + recall)

    print("precision: %f" % precision)
    print("recall: %f" % recall)
    print("f1: %f" % f1)

def automateTrainEval(inputFilePath):
    trainFilePath = "train.labeled.txt"
    testFilePath = "test.labeled.txt"
    unlabeledFilePath = "test.unlabeled.txt"
    decodedFilePath = "test.decoded.txt"

    createTrainTest(inputFilePath, trainFilePath, testFilePath)
    removeTags(testFilePath, unlabeledFilePath)
    decode(trainFilePath, unlabeledFilePath, decodedFilePath)
    evaluate(testFilePath, decodedFilePath)

def automateTestEval(trainFilePath, testFilePath):
    unlabeledFilePath = "unlabeled.txt"
    decodedFilePath = "decoded.txt"
    
    removeTags(testFilePath, unlabeledFilePath)
    decode(trainFilePath, unlabeledFilePath, decodedFilePath)
    evaluate(testFilePath, decodedFilePath)

if __name__ == '__main__':
    parser = ap.ArgumentParser(description="Part of speech tagger options")
     
    subparsers = parser.add_subparsers(dest='name')
 
    splitParser = subparsers.add_parser('split')
    splitParser.add_argument('inputFilePath')
    splitParser.add_argument('trainFilePath')
    splitParser.add_argument('testFilePath')
 
    stripParser = subparsers.add_parser('strip')
    stripParser.add_argument('inputFilePath')
    stripParser.add_argument('outputFilePath')
 
    decodeParser = subparsers.add_parser('decode')
    decodeParser.add_argument('trainFilePath')
    decodeParser.add_argument('testFilePath')
    decodeParser.add_argument('outFilePath')
 
    evalParser = subparsers.add_parser('eval')
    evalParser.add_argument('testFilePath')
    evalParser.add_argument('decodeFilePath')
 
    automateTrainParser = subparsers.add_parser('autotrain')
    automateTrainParser.add_argument('trainFilePath')

    automateTestParser = subparsers.add_parser("autotest")
    automateTestParser.add_argument('trainFilePath')
    automateTestParser.add_argument('testFilePath')
 
    args = parser.parse_args()
         
    if args.name == 'split':
        createTrainTest(args.inputFilePath, args.trainFilePath, args.testFilePath)
         
    elif args.name == 'strip':
        removeTags(args.inputFilePath, args.outputFilePath)
 
    elif args.name == 'decode':
        decode(args.trainFilePath, args.testFilePath, args.outFilePath)
 
    elif args.name == 'eval':
        evaluate(args.testFilePath, args.decodeFilePath)
         
    elif args.name == 'autotrain':
        automateTrainEval(args.trainFilePath)
        
    elif args.name == "autotest":
        automateTestEval(args.trainFilePath, args.testFilePath)