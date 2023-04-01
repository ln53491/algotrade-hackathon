from api import *

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



def algorithm():
    resetBalance()
    counter = 0
    newClosedDict = dict()
    newVolumeDict = dict()
    reverseClosedDict = dict()
    reverseVolumeDict = dict()
    while counter != 2:
        if counter == 0:
            currBalance = getBalance()
            if not counter:
                closedDict, volumeDict = getAllPairs()
                for pair in list(closedDict.keys()):
                    if pair.inCurr == "USDT" and volumeDict[pair] >= 10**4:
                        newClosedDict[pair] = closedDict[pair]  #dolar -> newCurr
                        newVolumeDict[pair] = volumeDict[pair]  #dolar -> newCurr

                        reversePair = CurrencyPair(pair.outCurr, pair.inCurr)
                        if closedDict[reversePair] <= currBalance["USDT"]:
                            reverseClosedDict[reversePair] = closedDict[reversePair]    #newCurr -> dolar
                            reverseVolumeDict[reversePair] = volumeDict[reversePair]    #newCurr -> dolar
                sortedCurrencies = dict(sorted(reverseClosedDict.items(), key=lambda x:x[1]))
                currency1 = list(sortedCurrencies.keys())[-1]
                currency2 = list(sortedCurrencies.keys())[-2]
            
                newNode_1 = Node(currency=currency1.inCurr,
                             volume=volumeDict[CurrencyPair("USDT", currency1.inCurr)],
                             rate_in=sortedCurrencies[currency1],
                             rate_out=closedDict[CurrencyPair("USDT", currency1.inCurr)])
                newNode_2 = Node(currency=currency2.inCurr,
                             volume=volumeDict[CurrencyPair("USDT", currency2.inCurr)],
                             rate_in=sortedCurrencies[currency2],
                             rate_out=closedDict[CurrencyPair("USDT", currency2.inCurr)])
                currNodes.append(newNode_1)
                currNodes.append(newNode_2)
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
        else:
            print(len(closedDict))
        counter += 1
        
        
        

    return