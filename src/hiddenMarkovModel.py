import collections
import math

import numpy

import common


class Histogram:
    def __init__(self):
        self.freq = collections.Counter()

    def observe(self, listOfStrings):
        self.freq.update(listOfStrings)

    def toDistribution(self):
        numElements = 0.0
        for word in self.freq:
            numElements += self.freq[word]
        
        dist = collections.defaultdict(float)
        for word in self.freq:
            dist[word] = self.freq[word] / numElements

        return dist
    
class CorpusStatistics:
    def __init__(self, taggedSentences, useSmoothing=True):
        uniqueTag = set()
        
        initVecFreq = Histogram()
        transFreq = {}
        wordGivenTagFreq = {}
        
        for taggedSentence in taggedSentences:
            tw = taggedSentence.taggedWords;
            
            uniqueTag.update(taggedSentence.toTagSeq())
            
            initVecFreq.observe([ tw[0].tag ])

            self.__observeLikelihood(wordGivenTagFreq, tw[0])
            
            for (cWord, pWord) in zip(tw[1:], tw):
                self.__observeTransition(transFreq, pWord.tag, cWord.tag)
                self.__observeLikelihood(wordGivenTagFreq, cWord)
                
        if useSmoothing:
            self.__laplaceSmooth(uniqueTag, transFreq, initVecFreq)
            
        self.initVec = initVecFreq.toDistribution()
        self.stateTrans = { tag: hist.toDistribution() for tag, hist in transFreq.items() }
        self.wordGivenTag = { tag: hist.toDistribution() for tag, hist in wordGivenTagFreq.items() }

        n = 1
        self.States = {}
        for tag in self.initVec:
            self.States[tag] = n
            n += 1

        self.Indices = { index : tag for tag, index in self.States.items() }

    def __laplaceSmooth(self,uniqueTag, transFreq, initVecFreq):
        initVecFreq.observe(uniqueTag)
        
        for fromPos in uniqueTag:
            for toPos in uniqueTag:
                self.__observeTransition(transFreq, fromPos, toPos)

    def __observeLikelihood(self, wordGivenTagFreq, taggedWord):
        x = taggedWord.word
        s = taggedWord.tag
        
        if s not in wordGivenTagFreq:
            wordGivenTagFreq[s] = Histogram()
        
        wordGivenTagFreq[s].observe([x])

    def __observeTransition(self, transFreq, fromPos, toPos):
        if (fromPos not in transFreq):
            transFreq[fromPos] = Histogram()
        
        transFreq[fromPos].observe([toPos]);

class TagDecoder:
    def __init__(self, corpusStats, unknownWordProb = 1e-8):
        self.unknownWordProb = unknownWordProb
        self.corpusStats = corpusStats
        
    def decode(self, sentence):
        N = len(self.corpusStats.stateTrans)
        T = len(sentence.words)

        if T <= 0:
            return common.TaggedSentence([])

        viterbi = numpy.zeros((N + 2, T))
        viterbi.fill(float("-inf"))
        
        backpointer = numpy.zeros((N + 2, T))

        # Initialization
        for tag in self.corpusStats.States:
            viterbi[self.corpusStats.States[tag], 0] = self.__safeLog(self.__safeInit(tag)) + self.__safeLog(self.__safeWordGivenTag(tag, sentence.words[0])) 
            backpointer[self.corpusStats.States[tag], 0] = 0

        # recursion
        for t in range(1, T):
            for tag in self.corpusStats.States:
                viterbi[self.corpusStats.States[tag], t] = self.__maxOverTag( lambda posPrime: viterbi[self.corpusStats.States[posPrime], t - 1] + self.__safeLog(self.__safeTrans(posPrime, tag)) + self.__safeLog(self.__safeWordGivenTag(tag, sentence.words[t])) )
                backpointer[self.corpusStats.States[tag], t] = self.corpusStats.States[self.__argMaxOverTag( lambda posPrime: viterbi[self.corpusStats.States[posPrime], t - 1] + self.__safeLog(self.__safeTrans(posPrime, tag)))]

        # termination
        # Not used so commented out.
        # v = self.__maxOverTag(lambda tag: viterbi[self.corpusStats.States[tag] + 1, T - 1])
        b = self.corpusStats.States[self.__argMaxOverTag(lambda tag:  viterbi[self.corpusStats.States[tag], T - 1])]

        tagged = common.TaggedSentence([ common.TaggedWord(sentence.words[T-1], self.corpusStats.Indices[b]) ])
        index = b
        for t in range(T-1, 0, -1):
            state = backpointer[index, t]
            if state != 0:
                tagged.taggedWords.append(common.TaggedWord(sentence.words[t-1], self.corpusStats.Indices[state]))
                index = state

        tagged.taggedWords.reverse()

        return tagged

    def __argMaxOverTag(self, f):
        maxValue = float("-inf")
        opt = None
        
        for tag in self.corpusStats.States:
            value = f(tag)
            if maxValue < value:
                maxValue = value
                opt = tag

        if opt == None:
            return sample(self.corpusStats.States, 1)[0]

        return opt
    
    def __maxOverTag(self, f):
        maxValue = float("-inf")

        for tag in self.corpusStats.States:
            value = f(tag)
            if maxValue < value:
                maxValue = value

        return maxValue

    def __safeLog(self, x):
        if x < 0:
            raise ValueError("x must be greater than 0.")
        
        if x == 0:
            return float("-inf")

        return math.log(x)

    def __safeInit(self, tag):
        x = self.corpusStats.initVec
        if tag in x:
            return x[tag]

        return 0.0
    
    def __safeTrans(self, from_, to_):
        x = self.corpusStats.stateTrans
        if from_ in x:
            if to_ in x[from_]:
                return x[from_][to_]

        return 0.0
    
    def __safeWordGivenTag(self, tag, word):
        x = self.corpusStats.wordGivenTag
        if tag in x:
            if word in x[tag]:
                return x[tag][word]

        return self.unknownWordProb
