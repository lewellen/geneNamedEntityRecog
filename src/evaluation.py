import random

import common
import hiddenMarkovModel as hmm

class Evaluator:
    def kFoldsCrossValidation(self, K, taggedSentences, smooth, prob):
        trainAcc = []
        testAcc = []
        
        for _ in range(0, K):
            train, test = self.splitTrainTest(taggedSentences, 1.0 / K)
            decoder = hmm.TagDecoder(CorpusStatistics(train, smooth), prob)
            trainAcc.append(self.accuracy(train, decoder))
            testAcc.append(self.accuracy(test, decoder))

        return (sum(trainAcc) / K, sum(testAcc) / K)

    def splitTrainTest(self, dataset, portion):
        random.shuffle(dataset)
        
        foldSize = int(len(dataset) * portion)
        train = dataset[foldSize:]
        test = dataset[:foldSize]
        
        return (train, test)

    def accuracy(self, dataset, decoder):
        count = 0.0
        numRight = 0.0
        n = 0
        
        for expected in dataset:
            actual = decoder.decode(Sentence(expected.toWordSeq()))
            
            alignment = zip(expected.toTagSeq(), actual.toTagSeq())
            count += len(alignment)
            numRight += len(filter(lambda (e,a): e == a, alignment))

            n += 1
            if n > 100:
                break

        return numRight / count

    def accuracyFromSets(self, expectedSet, actualSet):
        count = 0.0
        numRight = 0.0
        
        for (expected, actual) in zip(expectedSet, actualSet):
            alignment = zip(expected.toTagSeq(), actual.toTagSeq())
            count += len(alignment)
            numRight += len(filter(lambda (e,a): e == a, alignment))

        return numRight / count

    def accuracyFromMatrix(self, confusionMatrix):
        count = 0.0
        countRight = 0.0
        for a in confusionMatrix:
            for b in confusionMatrix[a]:
                count += confusionMatrix[a][b]
                if a == b:
                    countRight += confusionMatrix[a][b]

        return countRight / count

    def confusionMatrix(self, dataset, decoder):
        matrix = {}
        
        for expected in dataset:
            actual = decoder.decode(Sentence(expected.toWordSeq()))
            
            for (e, a) in zip(expected.taggedWords, actual.taggedWords):
                if e.tag not in matrix:
                    matrix[e.tag] = {}
                
                if a.tag not in matrix[e.tag]:
                    matrix[e.tag][a.tag] = 0
                    
                matrix[e.tag][a.tag] += 1

        return matrix

    def reportConfusionMatrix(self, corpusStats, matrix):
        print("\t"),
        for actual in corpusStats.States:
            print(actual),
        print("")
    
        for expected in corpusStats.States:
            if expected not in matrix:
                continue
            
            print(expected),
            
            for actual in corpusStats.States:
                if actual not in matrix[expected]:
                    print(0),
                else:
                    print(matrix[expected][actual]),
            
            print("")
