from collections import Counter
import random
import csv

CARD_TYPES = ["power", "unit", "spell", "site", "att"]
KEY_CARD = "Key Card"
STARTING_HAND_SIZE = 7
MIN_INITIAL_POWER = 1
MAX_INITIAL_POWER = 6
MIN_REDRAW_POWER = 2
MAX_REDRAW_POWER = 4

class Player:
	def __init__(self, deck):
		self.deck = deck
		self.hand = Hand([])

	def newHand(self, handSize=STARTING_HAND_SIZE):
		self.deck.reset()
		self.hand = self.deck.drawCards(handSize)
		#print self.hand.size()

	def draw(self, minPower, maxPower, handSize=STARTING_HAND_SIZE):
		self.newHand(handSize)
		while(minPower > self.powerInHand() or self.powerInHand() > maxPower):
			self.newHand(handSize)

	def initialDraw(self, handSize=STARTING_HAND_SIZE):
		self.draw(MIN_INITIAL_POWER, MAX_INITIAL_POWER, handSize)

	def reDraw(self, handSize=STARTING_HAND_SIZE):
		self.draw(MIN_REDRAW_POWER, MAX_REDRAW_POWER, handSize)

	def desperateGambit(self):
		self.reDraw(STARTING_HAND_SIZE-1)

	def drawCard(self):
		self.hand.drawCard(self.deck.drawCard())

	def cardsInHand(self):
		return len(self.hand)

	def powerInHand(self):
		return self.hand.nPower()

	def hasCard(self, cardName):
		return self.hand.containsCard(cardName)

class Card:
	def __init__(self, name, cardType):
		self.name = name
		self.type = cardType

	def getType(self):
		return self.type

	def getName(self):
		return self.name

	def __str__(self):
		return self.name

class Hand:
	def __init__(self, cards):
		self.cards = cards

	def containsCard(self, cardName):
		return cardName in map(Card.getName, self.cards)

	def nPower(self):
		return map(Card.getType, self.cards).count("power")

	def addCard(self, card):
		self.cards += [card]

	def size(self):
		return len(self.cards)

	def __str__(self):
		return str(map(Card.getName, self.cards))

	def __add__(self, otherHand):
		return Hand(self.cards + otherHand.cards)


class EternalDeck:
	def __init__(self, nKeyCards, nPower, keyCardName=KEY_CARD, keyCardType="unit", nCards=75):
		self.mainDeck = [Card("Power", "power") for x in xrange(nPower)] + \
					 [Card(keyCardName, keyCardType) for x in xrange(nKeyCards)] +\
					 [Card("Filler Card", "spell") for x in xrange(nCards - nPower - nKeyCards)]
		self.market = [Card("Market Card" + str(x+1), "att") for x in xrange(5)]
		self.reset()

	def reset(self):
		self.deck = self.mainDeck[:]
		self.shuffle()

	def typeCount(self, typeName):
		return map(Card.getType, self.mainDeck).count(typeName)

	def shuffle(self):
		random.shuffle(self.deck)

	def showDeck(self):
		print str(len(self.deck))
		print str(map(str, self.deck))

	def drawCard(self):
		return self.deck.pop(0)

	def drawCards(self, nCards):
		drawnCards = self.deck[0:nCards]
		del self.deck[0:nCards]
		return Hand(drawnCards)

	def __str__(self):
		printString = ""
		countedDeck = Counter(map(str, self.mainDeck))
		for card in countedDeck:
			printString += str(countedDeck[card]) + "\t" + str(card) + "\n"
		printString += "-----MARKET-----\n"
		countedMarket = Counter(map(str, self.market))
		for card in countedMarket:
			printString += str(countedMarket[card]) + "\t" + str(card) + "\n"
		printString += "-----SUMMARY----\n"
		printString += "Total:\t" + str(len(self.mainDeck)) + "\n"
		for cardType in CARD_TYPES:
			printString += cardType.capitalize() + ":\t" + str(self.typeCount(cardType)) + "\n"
		return printString

def runTrial(player, gambit=True):
	"""
	returns True if player finds key-card in opening hand, redraw, or desperate gambit redraw
	otherwise False
	"""
	player.initialDraw()
	#print "Opening Hand: " + str(player.hand)
	if player.hasCard(KEY_CARD):
		return True
	else:
		player.reDraw()
		#print "Redraw Hand: " + str(player.hand)
		if player.hasCard(KEY_CARD):
			return True
		elif gambit:
			player.desperateGambit()
			#print "Desperate Gambit Hand: " + str(player.hand)
			return player.hasCard(KEY_CARD)
		else:
			return False

def runTrials(player, gambit=True, nTrials=100):
	successCount = 0
	for trial in xrange(nTrials):
		if runTrial(player, gambit):
			successCount += 1

	return successCount

def runTrialSet(minKeyCards, maxKeyCards, nPower, gambit=True, nTrials=1000):
	results = {}
	for t in xrange(minKeyCards, maxKeyCards+1):
		successes = runTrials(Player(EternalDeck(t, nPower)), gambit, nTrials)
		estimatedProbability = round(float(successes) / nTrials, 4)
		results[t] = estimatedProbability
	return results

def main():

	# testPlayer = Player(EternalDeck(1, 25))
	# successes = runTrials(testPlayer, False, nTrials)
	# percentSuccess = round(float(successes) / nTrials * 100, 2)
	# print str(successes) + " out of " + str(nTrials) + " trials were successful. (" + \
	# 	str(percentSuccess) + "%)"

	nTrials = 100000
	nPower = 32
	minKeyCards = 1
	maxKeyCards = 20
	gambit = True

	results = runTrialSet(minKeyCards, maxKeyCards, nPower, gambit, nTrials)
	print "With " + str(nPower) + " power:"
	for nKeyCards in results:
		print str(nKeyCards) + " Key Cards: \t" + str(results[nKeyCards]*100) + "% success"
	with open('results.csv', 'wb') as outputFile:
		writer = csv.writer(outputFile)
		writer.writerow(["nKeyCards", "Est. Probability"])
		for nKeyCards in results:
			writer.writerow([nKeyCards, results[nKeyCards]])

main()
