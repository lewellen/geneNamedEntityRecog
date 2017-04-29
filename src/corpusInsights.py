import collections
import itertools
import re

import common
import hiddenMarkovModel as hmm

import numpy
import matplotlib.pyplot as plot

def histTokenLenBySemanticLabel(labeledFilePath):
	wordsByTag = { "Gene" : [], "NotGene" : [] }
	lFormat = common.LabeledFormat()
	for taggedSentence in lFormat.deserialize(labeledFilePath):
		for taggedWord in taggedSentence.taggedWords:
			tag = "Gene"
			if taggedWord.tag == "O":
				tag = "NotGene"

			wordsByTag[tag].append(taggedWord.word)

	for tag in wordsByTag:
		xs = map(lambda x : len(x), wordsByTag[tag])
		plot.hist(xs, bins = 50, alpha = 0.5, label = tag)

	plot.ylabel("Frequency")
	plot.xlabel("Token length")
	plot.yscale("log")
	plot.xscale("log")
	plot.legend(loc = "upper right") 
	plot.show()

def histSymbolByTag(labeledFilePath):
	tags = [ "I", "O", "B" ]

	symbolsByTag = { tag : { chr(i) : 0 for i in xrange(33, 127) } for tag in tags }

	labeledFilePath = "res/genetag.labeled"
	lFormat = common.LabeledFormat()
	for taggedSentence in lFormat.deserialize(labeledFilePath):
		for taggedWord in taggedSentence.taggedWords:
			for letter in taggedWord.word:
				symbolsByTag[taggedWord.tag][letter] += 1

	for i in xrange(33, 127):
		s = 0.0
		for tag in symbolsByTag:
			s += symbolsByTag[tag][chr(i)]

		if s > 0:
			for tag in symbolsByTag:
				symbolsByTag[tag][chr(i)] /= s

	prev = numpy.array( [ 0 for x in xrange(33, 127) ] )
	for tag in symbolsByTag:
		S = symbolsByTag[tag]
		sortedKeys = sorted(S.keys())
		sortedValuesByKeys = [ S[k] for k in sortedKeys ]
		
		columns = range(len(sortedKeys))
		plot.bar(columns, sortedValuesByKeys, label=tag, bottom=prev, width=1)
		plot.xticks(columns, sortedKeys)

		prev = numpy.add(prev, sortedValuesByKeys)

	plot.ylabel("P(char | tag)")
	plot.xlabel("Symbol")
	plot.legend(loc = "upper right") 
	plot.show()

def isNumber(x):
	try:
		float(x)
		return True
	except ValueError:
		return False

def featuresByTag(labeledFilePath):
	lFormat = common.LabeledFormat()

        isPunc = re.compile("^[^\w\s]+$")
        containsLetter = re.compile("[A-Z]|[a-z]")
        containsNumber = re.compile("[0-9]")
        isRomanNumeral = re.compile("^[IVXLCDM]+$")
        greekAlphabet = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho", "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega"]
	determiners = ["the", "a", "an", "this", "that", "these", "those"] # obviously more
	prepositions = ["of", "to", "in", "for", "on", "by", "about", "like"] # obviously more

	# Source: en.wikitionary.org
	latinSuffixes = ["a", "abilis", "aceus", "acis", "acium", "acius", "ago", "algia", "alia", "alis", "aneus", "antia", "anus", "archa", "arches", "archia", "aria", "aris", "arium", "arius", "aster", "astrum", "aticus", "atim", "atio", "atum", "atus", "ax", "bam", "bas", "bat", "bilis", "bo", "bra", "brum", "bula", "bulum", "bundus", "c", "ce", "cen", "ceps", "cida", "cidium", "cipes", "clus", "cola", "culum", "culus", "cum", "cumque", "cus", "decim", "dem", "e", "edo", "eius", "ela", "ellus", "ensis", "entia", "entus", "eo", "es", "esco", "esso", "etum", "eus", "fer", "fex", "ficatio", "fico", "ficus", "formis", "genus", "gnus", "graphia", "graphus", "ia", "ianus", "ibilis", "icus", "idus", "ies", "ifer", "ificus", "iger", "igo", "ilentus", "ilis", "illo", "illus", "inus", "io", "ior", "is", "iscus", "isma", "ismus", "issimus", "ista", "itas", "iter", "ites", "itia", "itis", "ito", "ittus", "ium", "ius", "ivius", "ivus", "legus", "logia", "loquium", "lus", "men", "mentum", "met", "metria", "monia", "monium", "nam", "nomia", "nus", "o", "olentus", "olum", "olus", "or", "osus", "phila", "polis", "por", "pte", "que", "rnus", "sco", "sor", "sorius", "sura", "sus", "tas", "ter", "theca", "ticus", "tim", "tio", "tito", "to", "tor", "torius", "trix", "trum", "tudo", "tura", "turio", "tus", "ucus", "ugo", "ula", "uleius", "ulentus", "uleus", "ulum", "ulus", "unculus", "undus", "urio", "urnus", "us", "uus", "ve", "vocus", "vorus", "vus"]  

	latinPrefixes = ["a", "ab", "abs", "ac", "ad", "al", "angusti", "ante", "archi", "arthr", "bi", "ce", "centi", "circum", "co", "col", "com", "con", "cor", "de", "dif", "dir", "dis", "dys", "e", "ec", "ef", "ex", "hebe", "hexa", "i", "ig", "il", "im", "in", "inter", "ir", "ne", "ob", "parvo", "per", "po", "por", "prae", "pseudo", "ptilo", "re", "red", "se", "sem", "semi", "sesqui", "sub", "super", "the", "theo", "tri", "uni", "ve", "xeno"]

	englishSuffixes = ["a", "apalooza", "athon", "ab", "ability", "able", "ably", "ac", "acal", "acean", "aceous", "acharya", "acious", "acity", "ad", "ade", "adelic", "adenia", "adic", "ae", "aemia", "age", "agog", "agogue", "agogy", "aholic", "al", "algia", "algy", "ality", "all", "ally", "ambulist", "amic", "amine", "amundo", "an", "ana", "ance", "ancy", "and", "ander", "andrian", "androus", "andry", "ane", "aneous", "angle", "angular", "ant", "anth", "anthropy", "ar", "arch", "archy", "ard", "arian", "arium", "ary", "ase", "ass", "assed", "ast", "aster", "astic", "ate", "athlon", "athon", "atim", "ation", "ative", "ator", "atory", "ay", "beaked", "bie", "bility", "biont", "biosis", "biotic", "blast", "blastic", "born", "boro", "borough", "bot", "bound", "burg", "burger", "burgh", "bury", "by", "cade", "caine", "cardia", "care", "carp", "carpic", "carpous", "ce", "cele", "cene", "centesis", "centric", "centrism", "cephalic", "cephalous", "cephaly", "ception", "cha", "chan", "chezia", "chore", "choron", "chory", "chrome", "cidal", "cide", "clase", "clast", "clinal", "cline", "clinic", "cocci", "coccus", "coel", "coele", "colous", "core", "corn", "cracy", "craft", "crasy", "crat", "cratic", "crete", "cy", "cycle", "cyte", "'d", "'d", "d", "dar", "derm", "derma", "dermatous", "diene", "dipsia", "dom", "drome", "dromous", "dynia", "ean", "ectomy", "ed", "ee", "een", "eer", "eh", "el", "elect", "elle", "eme", "emia", "en", "ence", "enchyma", "ency", "end", "ene", "ennial", "ent", "enyl", "eous", "'er", "er", "ergic", "ergy", "ers", "ery", "es", "esce", "escence", "escent", "ese", "esque", "ess", "est", "et", "eth", "etic", "ette", "ex", "exia", "ey", "facient", "faction", "fag", "ferous", "fest", "fication", "fier", "fix", "fold", "ford", "form", "forsaken", "free", "fu", "fugal", "ful", "furter", "fy", "gamous", "gamy", "gasm", "gate", "gaze", "geddon", "gen", "genesis", "genic", "genin", "genous", "geny", "gerous", "gnathous", "gon", "gonal", "gony", "gram", "gramme", "graph", "grapher", "graphical", "graphy", "grave", "gyny", "head", "hedra", "hedral", "hedron", "henge", "holic", "holism", "hood", "i", "i", "ia", "ial", "ian", "iana", "iasis", "iatric", "iatrician", "iatrics", "iatry", "ibility", "ible", "ibly", "ic", "ica", "ical", "ice", "ician", "icide", "icism", "icity", "ick", "icle", "ics", "id", "ide", "idine", "ie", "ienne", "ier", "ies", "iety", "iferous", "ific", "ification", "iform", "ify", "ile", "illion", "ily", "imundo", "in", "in'", "inda", "ine", "ing", "ino", "ion", "iot", "iour", "ious", "isation", "ise", "ish", "ism", "ismus", "ist", "ista", "istic", "istical", "istically", "ite", "itis", "itol", "itude", "ity", "ium", "ive", "ization", "ize", "izer", "izzle", "ja", "ji", "k", "kin", "kin", "kind", "kinesis", "kini", "kins", "kun", "lalia", "land", "landia", "latry", "le", "lect", "lepsy", "lept", "leptic", "less", "let", "licious", "like", "lin", "ling", "lings", "lingual", "lite", "lith", "lock", "log", "logic", "logical", "logist", "logue", "logues", "logy", "lol", "long", "loquy", "ly", "lysis", "lytic", "'m", "mab", "machy", "mageddon", "malacia", "man", "mance", "mancer", "mancy", "mane", "mania", "maniac", "mans", "manship", "mantic", "mas", "max", "meal", "megaly", "meister", "men", "ment", "mentum", "mer", "mere", "merous", "meter", "metre", "metric", "metry", "micin", "mo", "mobile", "mony", "more", "morph", "morphic", "morphism", "morphous", "morphy", "most", "mycete", "mycin", "n", "nado", "nap", "nasty", "naut", "nazi", "nd", "nema", "ness", "nik", "nom", "nomics", "nomy", "n't", "nym", "nymy", "o", "orama", "oate", "ock", "ocracy", "ode", "odont", "odontia", "oecious", "off", "ogony", "oholic", "oi", "oic", "oic acid", "oid", "ol", "ola", "ole", "ologist", "ology", "oma", "omas", "omata", "ome", "ometer", "ometry", "omics", "on", "one", "onium", "onomics", "onomy", "onym", "onymy", "oon", "opia", "opsia", "opsy", "or", "orama", "ory", "os", "ose", "osin", "osis", "osity", "ostomy", "oth", "otic", "otomy", "ous", "ov", "oxy", "oyl", "pants", "parous", "partite", "path", "pathic", "pathy", "pause", "pedia", "penia", "person", "pexy", "phage", "phagia", "phagous", "phagy", "phasia", "phil", "phile", "philia", "philiac", "philic", "philous", "phily", "phobe", "phobia", "phobic", "phone", "phonic", "phony", "phor", "phore", "phoresis", "phrenia", "phyl", "phyll", "phyte", "plasia", "plast", "plasty", "ple", "plegia", "plegic", "plex", "plinerved", "pnea", "pnoea", "pod", "poeia", "poiesis", "polis", "polises", "poly", "pounder", "preneur", "proof", "pter", "pteran", "pterous", "ptile", "punk", "R Us", "rama", "rd", "'re", "'re", "red", "rel", "ren", "ress", "ric", "rices", "ridden", "riffic", "rix", "rrhagia", "rrhaphy", "rrhea", "rrhexis", "rrhoea", "ry", "'s", "s", "safe", "sama", "san", "sauce", "saur", "saurus", "scape", "scope", "scopy", "self", "selves", "sexual", "ship", "sicle", "side", "sies", "sion", "sis", "ski", "sky", "soft", "sol", "some", "something", "son", "sophy", "speak", "sphere", "splain", "sploitation", "sson", "st", "stan", "stasis", "stat", "static", "statin", "ster", "stock", "stomy", "strophy", "style", "styly", "t", "tacular", "tainment", "tard", "tastic", "teen", "tene", "terol", "th", "therm", "thermal", "thermic", "thermy", "thon", "tide", "tinib", "tion", "tobe", "tome", "tomy", "ton", "topia", "tort", "town", "treme", "tron", "trope", "troph", "trophic", "trophy", "tropic", "tropism", "tropy", "tude", "tuple", "ty", "type", "ual", "ule", "um", "ure", "uret", "uretic", "urgy", "uria", "valent", "verse", "ville", "vir", "vore", "vorous", "wad", "ward", "wards", "ware", "way", "ways", "wear", "wich", "wick", "wide", "wise", "woman", "women", "work", "works", "worth", "worthy", "x", "xeny", "xor", "y", "yearold", "yer", "yl", "ylene", "ylidene", "yne", "z", "zilla", "zoan", "zoic", "zygous", "zza"]

	tags = sorted(["I", "O", "B"])
	features = sorted(["C3PO", "AllUpper", "AllLower", "Proper", "Punc", "Number", "Roman", "Greek", "Determiner", "Preposition", "LatinSuffix", "LatinPrefix", "EnglishSuffix"])
	featuresByTag = { t : { f : 0 for f in features } for t in tags }

	for taggedSentence in lFormat.deserialize(labeledFilePath):
		for taggedWord in taggedSentence.taggedWords:
			word = taggedWord.word
			tag = taggedWord.tag

			if re.search(containsLetter, word)  != None and re.search(containsNumber, word) != None:
				featuresByTag[tag]["C3PO"] += 1
	 
			if word.upper() == word:
				featuresByTag[tag]["AllUpper"] += 1
			  
			if word.lower() == word:
				featuresByTag[tag]["AllLower"] += 1
			  
			if word[0].isupper():
				featuresByTag[tag]["Proper"] += 1
		  
			if re.match(isPunc, word):
				featuresByTag[tag]["Punc"] += 1

			if isNumber(word):
				featuresByTag[tag]["Number"] += 1

			if re.match(isRomanNumeral, word):
				featuresByTag[tag]["Roman"] += 1
		  
			if word.lower() in greekAlphabet:
				featuresByTag[tag]["Greek"] += 1

			if word.lower() in determiners:
				featuresByTag[tag]["Determiner"] += 1

			if word.lower() in prepositions:
				featuresByTag[tag]["Preposition"] += 1

			for latinSuffix in latinSuffixes:
				if len(latinSuffix) < len(word) and word.lower().endswith(latinSuffix):
					featuresByTag[tag]["LatinSuffix"] += 1
					break # only count one even though could have multiple matches

			for latinPrefix in latinPrefixes:
				if len(latinPrefix) < len(word) and word.lower().startswith(latinPrefix):
					featuresByTag[tag]["LatinPrefix"] += 1
					break # only count one even though could have multiple matches

			for englishSuffix in englishSuffixes:
				if len(englishSuffix) < len(word) and word.lower().endswith(englishSuffix):
					featuresByTag[tag]["EnglishSuffix"] += 1
					break # only count one even though could have multiple matches

	for feature in features:
		s = 0.0
		for tag in tags:
			s += featuresByTag[tag][feature]

		if s > 0:
			for tag in tags:
				featuresByTag[tag][feature] /= s

	prev = numpy.zeros( len(features) )
	for tag in tags:
		S = featuresByTag[tag]
		sortedKeys = features
		sortedValuesByKeys = [ S[k] for k in sortedKeys ]
		
		indices = range(len(sortedKeys))
		plot.bar(indices, sortedValuesByKeys, label=tag, bottom=prev, width=1)
		plot.xticks(indices, sortedKeys)

		prev = numpy.add(prev, sortedValuesByKeys)

	plot.ylabel("P(tag | feature)")
	plot.xlabel("Feature")
	plot.legend(loc = "upper right") 
	plot.show()

def histInitVecGridStateTrans(labeledFilePath):
	lFormat = common.LabeledFormat()
	corpusStats = hmm.CorpusStatistics(
		[ taggedSentence for taggedSentence in lFormat.deserialize(labeledFilePath) ],
		True
		)

	tags = corpusStats.initVec.keys()
	sortedTags = sorted(tags)
	numTags = len(sortedTags)
	
	sortedPi = [ corpusStats.initVec[k] for k in sortedTags ]
	T = numpy.zeros((numTags, numTags))

	indices = range(numTags)
	for a in indices:
		for p in indices:
			# these indicies are swapped so it matches with the chart labels
			T[p, a] = corpusStats.stateTrans[sortedTags[a]][sortedTags[p]]

	f, subPlots = plot.subplots(1, 2)

	subPlots[0].bar(indices, sortedPi, width=1)
	subPlots[0].set_xticks(indices)
	subPlots[0].set_xticklabels(sortedTags)
	subPlots[0].set_xlabel("Tag")
	subPlots[0].set_ylabel("P($q_0$ = tag)")

	# Want to center the labels so shift indices to the right half a unit
	indices = [ i + 0.5 for i in indices]

	#subPlots[1].imshow(T, origin="lower")
	subPlots[1].set_xticks(indices)
	subPlots[1].set_xticklabels(sortedTags)
	subPlots[1].set_xlabel("Tag")
	subPlots[1].set_yticks(indices)
	subPlots[1].set_yticklabels(sortedTags)
	subPlots[1].set_ylabel("Next Tag")

	f.colorbar(subPlots[1].pcolormesh(T), ax=subPlots[1])
	f.tight_layout()

	plot.show()

def mostCommonUnigrams(labeledFilePath):
	lFormat = common.LabeledFormat()
	corpusStats = hmm.CorpusStatistics(
		[ taggedSentence for taggedSentence in lFormat.deserialize(labeledFilePath) ],
		True	
		)

	numProbs = 10
	numExamplesPerProb = 5
	
	for tag in corpusStats.wordGivenTag:
		print("%s" % tag)

		wordsByProb = {}
		for word in corpusStats.wordGivenTag[tag]:
			prob = round(corpusStats.wordGivenTag[tag][word], 3)
			if not prob in wordsByProb:
				wordsByProb.update({ prob : [] })

			wordsByProb[prob].append(word)

		descProbs = sorted(wordsByProb.keys(), reverse=True)
		topProbs = descProbs[:numProbs]
		for prob in topProbs:
			print("\t%.3f\t(%d): %s" % (
				prob, 
				len(wordsByProb[prob]), 
				", ".join(wordsByProb[prob][:numExamplesPerProb])
			))

def mostCommonBigrams(labeledFilePath):
	tags = sorted(["I", "O", "B"])
	indices = range(len(tags))

	bigrams = { u : { v : collections.Counter() for v in tags } for u in tags }

	lFormat = common.LabeledFormat()
	for taggedSentence in lFormat.deserialize(labeledFilePath):
		W = taggedSentence.taggedWords
		for (u, v) in zip(W, W[1:]):
			bigram = "%s %s" % (u.word, v.word)
			bigrams[u.tag][v.tag].update([bigram])

	for u in tags:
		for v in tags:
			mostCommon = bigrams[u][v].most_common(10)
			mostCommon = map(lambda (bigram, freq) : "\"%s\"" % bigram, mostCommon)
			summary = ", ".join(mostCommon)
			print("%s %s: %s" % (u, v, summary))


def mostCommonTrigrams(labeledFilePath):
	tags = sorted(["I", "O", "B"])
	indices = range(len(tags))

	trigrams = { u : { v : { w : collections.Counter() for w in tags } for v in tags } for u in tags }

	lFormat = common.LabeledFormat()
	for taggedSentence in lFormat.deserialize(labeledFilePath):
		W = taggedSentence.taggedWords
		for (u, v, w) in zip(W, W[1:], W[2:]):
			trigram = "%s %s %s" % (u.word, v.word, w.word)
			trigrams[u.tag][v.tag][w.tag].update([trigram])

	for u in tags:
		for v in tags:
			for w in tags:
				mostCommon = trigrams[u][v][w].most_common(8)
				mostCommon = map(lambda (trigram, freq) : "\"%s\"" % trigram, mostCommon)
				summary = ", ".join(mostCommon)
				print("%s %s %s: %s" % (u, v, w, summary))

if __name__ == "__main__":
	labeledFilePath = "res/genetag.labeled"

	# Insights on tokens
	histTokenLenBySemanticLabel(labeledFilePath)
	histSymbolByTag(labeledFilePath)
	featuresByTag(labeledFilePath)

	# HMM insight
	histInitVecGridStateTrans(labeledFilePath)

	# n-gram insights
	mostCommonUnigrams(labeledFilePath)
	mostCommonBigrams(labeledFilePath)
	mostCommonTrigrams(labeledFilePath)
