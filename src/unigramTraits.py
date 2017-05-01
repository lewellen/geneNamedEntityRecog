import operator
import re

import jointFreqMatrix

class UnigramTrait:
	def getName(self):
		return None

	def isAMatch(self, word):
		return False, None

	def rewriteWord(self, match):
		return self.getName()

	def selfSelect(self, taggedSentences, tag):
		pass

class RegExUnigramTrait(UnigramTrait):
	def isAMatch(self, word):
		if word is None:
			return False

		return re.match(self.getRegEx(), word), word

	def getRegEx(self):
		return None

class AllLowerLettersUnigramTrait(RegExUnigramTrait):
	def __init__(self):
		self.regex = re.compile("^[a-z]+$")

	def getName(self):
		return "AllLowerLetters"

	def getRegEx(self):
		return self.regex

class AllUpperLettersUnigramTrait(RegExUnigramTrait):
	def __init__(self):
		self.regex = re.compile("^[A-Z]+$")

	def getName(self):
		return "AllUpperLetters"

	def getRegEx(self):
		return self.regex

class AlphaNumericUnigramTrait(RegExUnigramTrait):
	def __init__(self):
		self.containsLetter= re.compile("[A-Z]|[a-z]")
		self.containsDigit = re.compile("[0-9]")

	def getName(self):
		return "AlphaNumeric"

	def getRegEx(self):
		return None

	def isAMatch(self, word):
		if word is None:
			return False

		# want all words that contain both letters and digits, not either or
		# E.g., accept 'C3PO' but reject '124' and 'foo'.
		return re.search(self.containsLetter, word) and re.search(self.containsDigit, word), word	

class CapitalizedUnigramTrait(RegExUnigramTrait):
	def __init__(self):
		self.regex = re.compile("^[A-Z][a-z]*$")

	def getName(self):
		return "Capitalized"

	def getRegEx(self):
		return self.regex

class PositiveIntegerUnigramTrait(RegExUnigramTrait):
	def __init__(self):
		self.regex = re.compile("^\+?[1-9][0-9]*$")

	def getName(self):
		return "PositiveInteger"

	def getRegEx(self):
		return self.regex

class PositiveRealUnigramTrait(RegExUnigramTrait):
	def __init__(self):
		self.regex = re.compile("^\+?[0-9]+\.[0-9]+$")

	def getName(self):
		return "PositiveReal"

	def getRegEx(self):
		return self.regex

class PuncUnigramTrait(RegExUnigramTrait):
	def __init__(self):
        	self.regex = re.compile("^[^\w\s]+$")

	def getName(self):
		return "Punc"

	def getRegEx(self):
		return self.regex

	def rewriteWord(self, match):
		return match

class RomanNumUnigramTrait(RegExUnigramTrait): 
	def __init__(self):
		# Obviously not robust and may accept false positives
		self.regex = re.compile("^[IVXLCDM]+$")

	def getName(self):
		return "Roman"

	def getRegEx(self):
		return self.regex

class WordPartUnigramTrait(UnigramTrait):
	def __init__(self):
		self.accepted = None

	def calcJointFreq(self, taggedSentences, tags, candidates):
		candidates = self.getCandidates()
		D = { d : { s : 0 for s in candidates } for d in tags }

		for taggedSentence in taggedSentences:
			for taggedWord in taggedSentence.taggedWords:
				tag = taggedWord.tag
				word = taggedWord.word
				satisfied, match = self.satisfies(candidates, word)
				if satisfied:
					D[tag][match] += 1

		return D

	def selfSelect(self, taggedSentences, tags):
		if not self.accepted is None:
			return

		candidates = self.getCandidates()
		D = self.calcJointFreq(taggedSentences, tags, candidates)
		E = jointFreqMatrix.toProbColGivenRow(D, tags, candidates)

		accepted = []
		for r in tags:
			byProbDesc = sorted(E[r].items(), key = operator.itemgetter(1), reverse = True)
			accepted += map(lambda (suffix, prob) : suffix, byProbDesc[:10])

		self.accepted = list(set(accepted))

		print("%s:\t" % self.getName()),
		print self.accepted

	def isAMatch(self, word):
		candidates = self.accepted
		if candidates is None:
			candidates = self.getCandidates()

		return self.satisfies(candidates, word)

	def satisfies(self, word):
		return (False, None)

class InSetUnigramTrait(WordPartUnigramTrait):
	def satisfies(self, candidates, word):
		return (word.lower() in candidates, word.lower())

class PrefixUnigramTrait(WordPartUnigramTrait):
	def satisfies(self, candidates, word):
		for prefix in candidates:
			if len(prefix) < len(word) and word.lower().startswith(prefix):
				return (True, prefix)
		return (False, None)

class SuffixUnigramTrait(WordPartUnigramTrait):
	def satisfies(self, candidates, word):
		for suffix in candidates:
			if len(suffix) < len(word) and word.lower().endswith(suffix):
				return (True, suffix)
		return (False, None)

class EnglishSuffixUnigramTrait(SuffixUnigramTrait):
	def getCandidates(self):
		return  ["a", "apalooza", "athon", "ab", "ability", "able", "ably", "ac", "acal", "acean", "aceous", "acharya", "acious", "acity", "ad", "ade", "adelic", "adenia", "adic", "ae", "aemia", "age", "agog", "agogue", "agogy", "aholic", "al", "algia", "algy", "ality", "all", "ally", "ambulist", "amic", "amine", "amundo", "an", "ana", "ance", "ancy", "and", "ander", "andrian", "androus", "andry", "ane", "aneous", "angle", "angular", "ant", "anth", "anthropy", "ar", "arch", "archy", "ard", "arian", "arium", "ary", "ase", "ass", "assed", "ast", "aster", "astic", "ate", "athlon", "athon", "atim", "ation", "ative", "ator", "atory", "ay", "beaked", "bie", "bility", "biont", "biosis", "biotic", "blast", "blastic", "born", "boro", "borough", "bot", "bound", "burg", "burger", "burgh", "bury", "by", "cade", "caine", "cardia", "care", "carp", "carpic", "carpous", "ce", "cele", "cene", "centesis", "centric", "centrism", "cephalic", "cephalous", "cephaly", "ception", "cha", "chan", "chezia", "chore", "choron", "chory", "chrome", "cidal", "cide", "clase", "clast", "clinal", "cline", "clinic", "cocci", "coccus", "coel", "coele", "colous", "core", "corn", "cracy", "craft", "crasy", "crat", "cratic", "crete", "cy", "cycle", "cyte", "'d", "'d", "d", "dar", "derm", "derma", "dermatous", "diene", "dipsia", "dom", "drome", "dromous", "dynia", "ean", "ectomy", "ed", "ee", "een", "eer", "eh", "el", "elect", "elle", "eme", "emia", "en", "ence", "enchyma", "ency", "end", "ene", "ennial", "ent", "enyl", "eous", "'er", "er", "ergic", "ergy", "ers", "ery", "es", "esce", "escence", "escent", "ese", "esque", "ess", "est", "et", "eth", "etic", "ette", "ex", "exia", "ey", "facient", "faction", "fag", "ferous", "fest", "fication", "fier", "fix", "fold", "ford", "form", "forsaken", "free", "fu", "fugal", "ful", "furter", "fy", "gamous", "gamy", "gasm", "gate", "gaze", "geddon", "gen", "genesis", "genic", "genin", "genous", "geny", "gerous", "gnathous", "gon", "gonal", "gony", "gram", "gramme", "graph", "grapher", "graphical", "graphy", "grave", "gyny", "head", "hedra", "hedral", "hedron", "henge", "holic", "holism", "hood", "i", "i", "ia", "ial", "ian", "iana", "iasis", "iatric", "iatrician", "iatrics", "iatry", "ibility", "ible", "ibly", "ic", "ica", "ical", "ice", "ician", "icide", "icism", "icity", "ick", "icle", "ics", "id", "ide", "idine", "ie", "ienne", "ier", "ies", "iety", "iferous", "ific", "ification", "iform", "ify", "ile", "illion", "ily", "imundo", "in", "in'", "inda", "ine", "ing", "ino", "ion", "iot", "iour", "ious", "isation", "ise", "ish", "ism", "ismus", "ist", "ista", "istic", "istical", "istically", "ite", "itis", "itol", "itude", "ity", "ium", "ive", "ization", "ize", "izer", "izzle", "ja", "ji", "k", "kin", "kin", "kind", "kinesis", "kini", "kins", "kun", "lalia", "land", "landia", "latry", "le", "lect", "lepsy", "lept", "leptic", "less", "let", "licious", "like", "lin", "ling", "lings", "lingual", "lite", "lith", "lock", "log", "logic", "logical", "logist", "logue", "logues", "logy", "lol", "long", "loquy", "ly", "lysis", "lytic", "'m", "mab", "machy", "mageddon", "malacia", "man", "mance", "mancer", "mancy", "mane", "mania", "maniac", "mans", "manship", "mantic", "mas", "max", "meal", "megaly", "meister", "men", "ment", "mentum", "mer", "mere", "merous", "meter", "metre", "metric", "metry", "micin", "mo", "mobile", "mony", "more", "morph", "morphic", "morphism", "morphous", "morphy", "most", "mycete", "mycin", "n", "nado", "nap", "nasty", "naut", "nazi", "nd", "nema", "ness", "nik", "nom", "nomics", "nomy", "n't", "nym", "nymy", "o", "orama", "oate", "ock", "ocracy", "ode", "odont", "odontia", "oecious", "off", "ogony", "oholic", "oi", "oic", "oic acid", "oid", "ol", "ola", "ole", "ologist", "ology", "oma", "omas", "omata", "ome", "ometer", "ometry", "omics", "on", "one", "onium", "onomics", "onomy", "onym", "onymy", "oon", "opia", "opsia", "opsy", "or", "orama", "ory", "os", "ose", "osin", "osis", "osity", "ostomy", "oth", "otic", "otomy", "ous", "ov", "oxy", "oyl", "pants", "parous", "partite", "path", "pathic", "pathy", "pause", "pedia", "penia", "person", "pexy", "phage", "phagia", "phagous", "phagy", "phasia", "phil", "phile", "philia", "philiac", "philic", "philous", "phily", "phobe", "phobia", "phobic", "phone", "phonic", "phony", "phor", "phore", "phoresis", "phrenia", "phyl", "phyll", "phyte", "plasia", "plast", "plasty", "ple", "plegia", "plegic", "plex", "plinerved", "pnea", "pnoea", "pod", "poeia", "poiesis", "polis", "polises", "poly", "pounder", "preneur", "proof", "pter", "pteran", "pterous", "ptile", "punk", "R Us", "rama", "rd", "'re", "'re", "red", "rel", "ren", "ress", "ric", "rices", "ridden", "riffic", "rix", "rrhagia", "rrhaphy", "rrhea", "rrhexis", "rrhoea", "ry", "'s", "s", "safe", "sama", "san", "sauce", "saur", "saurus", "scape", "scope", "scopy", "self", "selves", "sexual", "ship", "sicle", "side", "sies", "sion", "sis", "ski", "sky", "soft", "sol", "some", "something", "son", "sophy", "speak", "sphere", "splain", "sploitation", "sson", "st", "stan", "stasis", "stat", "static", "statin", "ster", "stock", "stomy", "strophy", "style", "styly", "t", "tacular", "tainment", "tard", "tastic", "teen", "tene", "terol", "th", "therm", "thermal", "thermic", "thermy", "thon", "tide", "tinib", "tion", "tobe", "tome", "tomy", "ton", "topia", "tort", "town", "treme", "tron", "trope", "troph", "trophic", "trophy", "tropic", "tropism", "tropy", "tude", "tuple", "ty", "type", "ual", "ule", "um", "ure", "uret", "uretic", "urgy", "uria", "valent", "verse", "ville", "vir", "vore", "vorous", "wad", "ward", "wards", "ware", "way", "ways", "wear", "wich", "wick", "wide", "wise", "woman", "women", "work", "works", "worth", "worthy", "x", "xeny", "xor", "y", "yearold", "yer", "yl", "ylene", "ylidene", "yne", "z", "zilla", "zoan", "zoic", "zygous", "zza"]

	def getName(self):
		return "EnglishSuffix"

class LatinSuffixUnigramTrait(SuffixUnigramTrait):
	def getCandidates(self):
		return ["a", "abilis", "aceus", "acis", "acium", "acius", "ago", "algia", "alia", "alis", "aneus", "antia", "anus", "archa", "arches", "archia", "aria", "aris", "arium", "arius", "aster", "astrum", "aticus", "atim", "atio", "atum", "atus", "ax", "bam", "bas", "bat", "bilis", "bo", "bra", "brum", "bula", "bulum", "bundus", "c", "ce", "cen", "ceps", "cida", "cidium", "cipes", "clus", "cola", "culum", "culus", "cum", "cumque", "cus", "decim", "dem", "e", "edo", "eius", "ela", "ellus", "ensis", "entia", "entus", "eo", "es", "esco", "esso", "etum", "eus", "fer", "fex", "ficatio", "fico", "ficus", "formis", "genus", "gnus", "graphia", "graphus", "ia", "ianus", "ibilis", "icus", "idus", "ies", "ifer", "ificus", "iger", "igo", "ilentus", "ilis", "illo", "illus", "inus", "io", "ior", "is", "iscus", "isma", "ismus", "issimus", "ista", "itas", "iter", "ites", "itia", "itis", "ito", "ittus", "ium", "ius", "ivius", "ivus", "legus", "logia", "loquium", "lus", "men", "mentum", "met", "metria", "monia", "monium", "nam", "nomia", "nus", "o", "olentus", "olum", "olus", "or", "osus", "phila", "polis", "por", "pte", "que", "rnus", "sco", "sor", "sorius", "sura", "sus", "tas", "ter", "theca", "ticus", "tim", "tio", "tito", "to", "tor", "torius", "trix", "trum", "tudo", "tura", "turio", "tus", "ucus", "ugo", "ula", "uleius", "ulentus", "uleus", "ulum", "ulus", "unculus", "undus", "urio", "urnus", "us", "uus", "ve", "vocus", "vorus", "vus"] 

	def getName(self):
		return "LatinSuffix"

class LatinPrefixUnigramTrait(PrefixUnigramTrait):
	def getCandidates(self):
		return ["a", "ab", "abs", "ac", "ad", "al", "angusti", "ante", "archi", "arthr", "bi", "ce", "centi", "circum", "co", "col", "com", "con", "cor", "de", "dif", "dir", "dis", "dys", "e", "ec", "ef", "ex", "hebe", "hexa", "i", "ig", "il", "im", "in", "inter", "ir", "ne", "ob", "parvo", "per", "po", "por", "prae", "pseudo", "ptilo", "re", "red", "se", "sem", "semi", "sesqui", "sub", "super", "the", "theo", "tri", "uni", "ve", "xeno"]

	def getName(self):
		return "LatinPrefix"

class GreekLetterUnigramTrait(InSetUnigramTrait):
	def getCandidates(self):
 	       return ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho", "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega"]

	def getName(self):
		return "GreekLetter"

class DeterminerUnigramTrait(InSetUnigramTrait):
	def getCandidates(self):
		return ["all", "alotta", "anny", "anoda", "anotha", "another", "any", "atta", "beaucoup", "bofe", "bolth", "both", "bothe", "certain", "couple", "dat", "dem", "dese", "dis", "each", "ebery", "either", "em", "enny", "enough", "enuf", "enuff", "eny", "eeuerie", "euery", "ever", "everie", "everwhat", "every", "few", "fewer", "fewest", "fewscore", "fiew", "he", "hecka", "hella", "her", "hes", "hevery", "his", "hits", "how many", "how much", "hundredsome", "hys", "it", "itits", "last", "least", "little", "ma", "mah", "mai", "many", "manye", "me", "mickle", "more", "most", "much", "muchee", "muh", "my", "neither", "next", "nil", "no", "none", "other", "our", "overmuch", "owne", "plenty", "quodque", "said", "several", "severall", "she", "some", "such", "sufficient", "that", "thatt", "their", "them", "there", "these", "they", "theytheythilk", "thine", "this", "those", "thousandsome", "thy", "Thy", "umpteen", "us", "various", "vich", "wat", "we", "what", "whatewhatevah", "whatever", "whatevuh", "whath", "which", "whichever", "whose", "whosesoever", "whosever", "whoze", "wor", "yer", "yo", "yonder", "you", "your", "yure", "zis", "the"]

	def getName(self):
		return "Determiner"

class PrepositionUnigramTrait(InSetUnigramTrait):
	def getCandidates(self):
		return ["of", "to", "in", "for", "on", "by", "about", "like"] # obviously more

	def getName(self):
		return "Preposition"

class ConjunctionUnigramTrait(InSetUnigramTrait):
	def getCandidates(self):
		return ["and", "or", "but", "nor", "so", "for", "yet", "after", "although", "as", "because", "before", "once", "since", "though", "till", "unless", "until", "what", "when", "whenever", "wherever", "whether", "while"]

	def getName(self):
		return "Conjunction"

class KeywordUnigramTrait(InSetUnigramTrait):
	def getCandidates(self):
		return ["kinase", "c", "human", "mouse", "rat", "gene", "protein", "genes", "proteins", "cdna", "rdna", "dna", "family", "receptor"]

	def getName(self):
		return "Keyword"

	def rewriteWord(self, match):
		return match

class ChemicalFormulaUnigramTrait(RegExUnigramTrait):
	def __init__(self):
		symbols = ["Ac", "Al", "Am", "Sb", "Ar", "As", "At", "Ba", "Bk", "Be", "Bi", "Bh", "B", "Br", "Cd", "Ca", "Cf", "C", "Ce", "Cs", "Cl", "Cr", "Co", "Cu", "Cm", "Ds", "Db", "Dy", "Es", "Er", "Eu", "Fm", "F", "Fr", "Gd", "Ga", "Ge", "Au", "Hf", "Hs", "He", "Ho", "H", "In", "I", "Ir", "Fe", "Kr", "La", "Lr", "Pb", "Li", "Lu", "Mg", "Mn", "Mt", "Md", "Hg", "Mo", "Nd", "Ne", "Np", "Ni", "Nb", "N", "No", "Os", "O", "Pd", "P", "Pt", "Pu", "Po", "K", "Pr", "Pm", "Pa", "Ra", "Rn", "Re", "Rh", "Rg", "Rb", "Ru", "Rf", "Sm", "Sc", "Sg", "Se", "Si", "Ag", "Na", "Sr", "S", "Ta", "Tc", "Te", "Tb", "Tl", "Th", "Tm", "Sn", "Ti", "W", "Uub", "Uuh", "Uuo", "Uup", "Uuq", "Uus", "Uut", "Uuu", "U", "V", "Xe", "Yb", "Y", "Zn", "Zr"]

		symbols = "|".join(symbols)
		expr = "((%s)\d*)+" % (symbols)
		self.regex = re.compile(expr)

	def getName(self):
		return "ChemicalFormula"

	def getRegEx(self):
		return self.regex

#	def isAMatch(self, word):
#		if word is None:
#			return False
#
#		S = []
#		fullMatch = True
#		for i, c in enumerate(word):
#			if c == '(':
#				S.append((i,c))
#			elif c == ')':
#				(j, d) = S.pop()
#				sub = word[j + 1:i - 1]
#				fullMatch = fullMatch and re.match(self.getRegEx(), word)
#
#		return fullMatch, word

unigramTraitList = [
	KeywordUnigramTrait(), PuncUnigramTrait(), # Most specific match
	ChemicalFormulaUnigramTrait(),
	RomanNumUnigramTrait(), PositiveIntegerUnigramTrait(), PositiveRealUnigramTrait(), GreekLetterUnigramTrait(),
	AlphaNumericUnigramTrait(), AllUpperLettersUnigramTrait(), CapitalizedUnigramTrait(), 
	ConjunctionUnigramTrait(), DeterminerUnigramTrait(), PrepositionUnigramTrait(), 
	EnglishSuffixUnigramTrait(), LatinPrefixUnigramTrait(), LatinSuffixUnigramTrait(),
	AllLowerLettersUnigramTrait() # to least specific match
]
