from api import *
import copy

class Node:
    def __init__(self, currency, volume, rate_in, rate_out):
        self.currency = currency
        self.volume = volume
        self.rate_in_curr = rate_in
        self.rate_out_curr = rate_out
        self.balance = None
        self.coef = None

    def refreshNode(self, newRateIn, newRateOut, newVolume):
        self.coef = newRateIn/self.rate_in_curr
        self.rate_in_curr = newRateIn
        self.rate_out_curr = newRateOut
        self.volume = newVolume

    def setBalance(self, balance):
        self.balance = balance

    def __str__(self):
        return f"{self.currency}, {self.volume}, {self.coef}, {self.balance}, {self.rate_in_curr}, {self.rate_out_curr}"

    def __repr__(self):
        return f"{self.currency}"
    
    def __hash__(self):
        return hash(self.currency)
    
    def __eq__(self, other):
        return self.currency == other.currency

global first
first = False

def algorithm():
    global first
    global closedDict
    global volumeDict
    newClosedDict = dict()
    newVolumeDict = dict()
    reverseClosedDict = dict()
    reverseVolumeDict = dict()
    calculatedClosedDict = dict()
    currBalance = getBalance()
    if not first:
        closedDict, volumeDict = getAllPairs()
        for pair in list(closedDict.keys()):
            if pair.inCurr == "USDT" and volumeDict[pair] >= currBalance["USDT"]:
                newClosedDict[pair] = closedDict[pair]  #dolar -> newCurr
                newVolumeDict[pair] = volumeDict[pair]  #dolar -> newCurr

                reversePair = CurrencyPair(pair.outCurr, pair.inCurr)
                            # if closedDict[reversePair] <= currBalance["USDT"]:
                reverseClosedDict[reversePair] = closedDict[reversePair]    #newCurr -> dolar
                reverseVolumeDict[reversePair] = volumeDict[reversePair]    #newCurr -> dolar

                calculatedClosedDict[pair] = currBalance["USDT"] * newClosedDict[pair] / 10**16 * reverseClosedDict[reversePair]

        sortedCalculatedClosedDict = dict(sorted(calculatedClosedDict.items(), key=lambda x:x[1]))

        curr1temp = list(sortedCalculatedClosedDict.keys())[-1]
        curr2temp = list(sortedCalculatedClosedDict.keys())[-2]
        currency1 = CurrencyPair(curr1temp.outCurr, curr1temp.inCurr)
        currency2 = CurrencyPair(curr2temp.outCurr, curr2temp.inCurr)
                
        newNode_1 = Node(currency=currency1.inCurr,
                                volume=volumeDict[CurrencyPair("USDT", currency1.inCurr)],
                                rate_in=closedDict[currency1],
                                rate_out=closedDict[CurrencyPair("USDT", currency1.inCurr)])
        newNode_2 = Node(currency=currency2.inCurr,
                                volume=volumeDict[CurrencyPair("USDT", currency2.inCurr)],
                                rate_in=closedDict[currency2],
                                rate_out=closedDict[CurrencyPair("USDT", currency2.inCurr)])
        ratio = 0
        if newNode_1.rate_out_curr > newNode_2.rate_out_curr:
            ratio = newNode_2.rate_out_curr / newNode_1.rate_out_curr
            buyFirst = int(ratio * currBalance["USDT"])
            buySecond = currBalance["USDT"] - buyFirst
        else:
            ratio = newNode_1.rate_out_curr / newNode_2.rate_out_curr
            buyFirst = int(ratio * currBalance["USDT"])
            buySecond = currBalance["USDT"] - buyFirst
        createOrders([Order(currencyPair=CurrencyPair("USDT", currency1.inCurr), amount=buyFirst),
                                Order(currencyPair=CurrencyPair("USDT", currency2.inCurr), amount=buySecond)])
        print("USDT balance: "+ str(currBalance["USDT"]))
        newNode_1.setBalance(int(buyFirst * newNode_1.rate_out_curr / 10**8))
        newNode_2.setBalance(int(buySecond * newNode_2.rate_out_curr / 10**8))
        currNodes.append(newNode_1)
        currNodes.append(newNode_2)
        newBalance = getBalance()
        print(int(newBalance[newNode_1.currency] / 10**8 * newNode_1.rate_in_curr + newBalance[newNode_2.currency] / 10**8 * newNode_2.rate_in_curr))   
        first = True
    else:
        oldClosedDict = copy.deepcopy(closedDict)
        oldVolumeDict = copy.deepcopy(volumeDict)
        closedDict, volumeDict = getAllPairs()
        deepCopyCurrNodes = copy.deepcopy(currNodes)
        for currNode2 in deepCopyCurrNodes:
            print(currNodes)
            
            currNode2 = currNodes.pop(0)
            print(currNode2)
            newClosedDict = dict()
            newVolumeDict = dict()
            reverseClosedDict = dict()
            reverseVolumeDict = dict()
            calculatedClosedDict = dict()
            for pair in list(closedDict.keys()):
                if pair.inCurr == currNode2.currency and volumeDict[pair] >= currBalance[currNode2.currency]:
                    newClosedDict[pair] = closedDict[pair]  #currNode2.currency -> newCurr
                    newVolumeDict[pair] = volumeDict[pair]  #currNode2.currency -> newCurr

                    reversePair = CurrencyPair(pair.outCurr, pair.inCurr)
                    reverseClosedDict[reversePair] = closedDict[reversePair]    #newCurr -> currNode2.currency
                    reverseVolumeDict[reversePair] = volumeDict[reversePair]    #newCurr -> currNode2.currency

                    larinaFormula = currBalance[currNode2.currency] * newClosedDict[pair] / 10**16 * reverseClosedDict[reversePair]
                    koeficijent = closedDict[pair]/oldClosedDict[pair]
                    staminTeorem = larinaFormula * koeficijent
                    calculatedClosedDict[pair] = staminTeorem
            # currNode2.refreshNode()
            sortedCalculatedClosedDict = dict(sorted(calculatedClosedDict.items(), key=lambda x:x[1]))
            if len(list(sortedCalculatedClosedDict.keys())) != 0:
                curr1temp = list(sortedCalculatedClosedDict.keys())[-1]
                currency1 = CurrencyPair(curr1temp.outCurr, curr1temp.inCurr)
                newNode_1 = Node(currency=currency1.inCurr,
                                volume=volumeDict[CurrencyPair(currency1.outCurr, currency1.inCurr)],
                                rate_in=closedDict[currency1],
                                rate_out=closedDict[CurrencyPair(currency1.outCurr, currency1.inCurr)])
                print("pareee: " + str(currBalance[currNode2.currency]))
                createOrders([Order(currencyPair=CurrencyPair(currency1.outCurr, currency1.inCurr), amount=currBalance[currNode2.currency])])
                print(f"Kupljeno dijete {currNode2.currency} balance: "+ str(currBalance[currNode2.currency]))
                print(f"KUPIOOOSIIII: {currBalance[currNode2.currency] * newNode_1.rate_out_curr / 10**8}")
                newNode_1.setBalance(int(currBalance[currNode2.currency] * newNode_1.rate_out_curr / 10**8)) ###########
                currNodes.append(newNode_1)
                newBalance = getBalance()
                print(int(newBalance[newNode_1.currency] / 10**8 * newNode_1.rate_in_curr))
            else:
                currNodes.append(currNode2)   
    return

def returnToUSDT():
    global closedDict
    global volumeDict
    for 
    return