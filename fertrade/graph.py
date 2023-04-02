from api import *
import copy
import time

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

allValues = []
def drawGraph(currency):
    global closedDict
    oldClosedDict = copy.deepcopy(closedDict)
    closedDict, volumeDict = getAllPairs()
    if not oldClosedDict.__contains__(CurrencyPair("USDT", currency)):
        return 0
    return (closedDict[CurrencyPair("USDT", currency)] - oldClosedDict[CurrencyPair("USDT", currency)]) / oldClosedDict[CurrencyPair("USDT", currency)] * 100

def algorithm():
    global first
    global closedDict
    global volumeDict
    global currNodes
    newClosedDict = dict()
    newVolumeDict = dict()
    reverseClosedDict = dict()
    reverseVolumeDict = dict()
    calculatedClosedDict = dict()
    currBalance = getBalance()
    print(f"Tick: {getTime()}")
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
        orderStatus, errorMsg = createOrders([Order(currencyPair=CurrencyPair("USDT", currency1.inCurr), amount=buyFirst),
                                Order(currencyPair=CurrencyPair("USDT", currency2.inCurr), amount=buySecond)])
        newBalance = getBalance()
        print(f"Order Status: {'SUCCESS' if orderStatus == 200 else errorMsg}")
        print("Initial Balance: "+ str(currBalance["USDT"]))
        print(f"==> {newNode_1.currency} - {newBalance[newNode_1.currency]}")
        print(f"==> {newNode_2.currency} - {newBalance[newNode_2.currency]}\n")
        first = True
    else:
        oldClosedDict = copy.deepcopy(closedDict)
        closedDict, volumeDict = getAllPairs()
        currBalance = {x:y for x,y in currBalance.items() if y!=0}
        orders = []
        for currNode in list(currBalance.keys()):
            newClosedDict = dict()
            newVolumeDict = dict()
            reverseClosedDict = dict()
            reverseVolumeDict = dict()
            calculatedClosedDict = dict()
            for pair in list(closedDict.keys()):
                if pair.inCurr == currNode and volumeDict[pair] >= currBalance[currNode] and pair.inCurr != "USDT":
                    newClosedDict[pair] = closedDict[pair]  #currNode2.currency -> newCurr
                    newVolumeDict[pair] = volumeDict[pair]  #currNode2.currency -> newCurr

                    reversePair = CurrencyPair(pair.outCurr, pair.inCurr)
                    reverseClosedDict[reversePair] = closedDict[reversePair]    #newCurr -> currNode2.currency
                    reverseVolumeDict[reversePair] = volumeDict[reversePair]    #newCurr -> currNode2.currency

                    larinaFormula = currBalance[currNode] * newClosedDict[pair] / 10**16 * reverseClosedDict[reversePair]
                    koeficijent = closedDict[pair]/oldClosedDict[pair]
                    staminTeorem = larinaFormula * koeficijent
                    calculatedClosedDict[pair] = larinaFormula
            sortedCalculatedClosedDict = dict(sorted(calculatedClosedDict.items(), key=lambda x:x[1]))
            if len(list(sortedCalculatedClosedDict.keys())) >= 2:
                if len(currBalance.keys()) < 5:
                    firstNode = int(currBalance[currNode]/2)
                    orders.append(Order(CurrencyPair(inCurr=currNode, outCurr=list(sortedCalculatedClosedDict.keys())[-1].outCurr), currBalance[currNode]/2))
                    orders.append(Order(CurrencyPair(inCurr=currNode, outCurr=list(sortedCalculatedClosedDict.keys())[-2].outCurr), currBalance[currNode] - firstNode))
                else:
                    orders.append(Order(CurrencyPair(inCurr=currNode, outCurr=list(sortedCalculatedClosedDict.keys())[-1].outCurr), currBalance[currNode]))
        for order in orders:
            orderStatus, errorMsg = createOrders([order])
            print(f"Order Status: {'SUCCESS' if orderStatus == 200 else errorMsg}")
            newBalance = getBalance()
            if orderStatus == 200:
                print(f"==> {order.currencyPair.outCurr} - {newBalance[order.currencyPair.outCurr]}")
            else:
                print()
    return

def returnToUSDT():
    global closedDict
    global volumeDict
    global currNodes
    print("\n!!!!! Start going back to usd !!!!!")
    currBalance = getBalance()
    currBalance = {x:y for x,y in currBalance.items() if y!=0}
    closedDict, volumeDict = getAllPairs()
    if list(currBalance.keys()) == ["USDT"]: return
    for currNode in list(currBalance.keys()):
        if currNode == "USDT": continue
        wantedPair = CurrencyPair(inCurr=currNode, outCurr="USDT")
        if closedDict.__contains__(wantedPair):
            statusCode, errMsg = createOrders([Order(currencyPair=wantedPair, amount=currBalance[currNode])])
            if statusCode != 200:
                print(errMsg)
                time.sleep(3)
                algorithm()
                returnToUSDT()
            else:
                for idx,node in enumerate(copy.deepcopy(currNodes)):
                    if node.currency == currNode:
                        del currNodes[idx]
        else:
            time.sleep(3)
            algorithm()
            returnToUSDT()
    return