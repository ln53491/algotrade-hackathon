import requests
import json
from api_models import *
import time

user = "fertrade"
secret = "43b50579b79eafb9403f92cb4c6f9e64"
rootApi = "http://192.168.1.101:3000"

#counter tickova
def getTime():
    response_API = requests.get(rootApi + "/getTime")
    return int(response_API.text)

def getAllPairs():
    response_API = requests.get(rootApi + "/getAllPairs")
    allPairs = json.loads(response_API.text)
    for pair in allPairs.keys():
        currPair = pair.split("_")
        value = allPairs[pair]
        currencies = currPair[1].split(",")
        if len(currencies) == 2:
            newPair = CurrencyPair(inCurr=currencies[0], outCurr=currencies[1])
            if currPair[0] == "close":
                closedDict[newPair] = value
            if currPair[0] == "volume":
                volumeDict[newPair] = value       
    return closedDict, volumeDict

#predati listu klasa CurrencyPairova
#pulla nove vrijednosti i spremi u Close i Volume dictove
def getPairs(pairs):
    if not pairs: return dict(), dict()
    stringPairs: str = "|".join([",".join([pair.inCurr, pair.outCurr]) for pair in pairs])
    response_API = requests.get(rootApi + "/getPairs/" + stringPairs)
    allPairs = json.loads(response_API.text)
    returnClosed = dict()
    returnVolume = dict()
    for pair in allPairs.keys():
        currPair = pair.split("_")
        value = allPairs[pair]
        currencies = currPair[1].split("s,")
        if len(currencies) == 2:
            newPair = CurrencyPair(inCurr=currencies[0], outCurr=currencies[1])
            if currPair[0] == "close":
                closedDict[newPair] = value
                returnClosed[newPair] = int(value)
            if currPair[0] == "volume":
                volumeDict[newPair] = int(value) 
                returnVolume = value 
    return returnClosed, returnVolume

#predati listu klasa Order
#vraca true ili false
def createOrders(orders):
    t0 = time.time()
    stringOrder: str = "|".join([",".join([order.currencyPair.inCurr, order.currencyPair.outCurr, str(order.amount)]) for order in orders])
    response_API = requests.get(rootApi + "/createOrders/" + user + "/" + secret + "/" + stringOrder)
    print(time.time() - t0)
    return response_API.status_code == 200

def getBalance():
    response_API = requests.get(rootApi + "/balance/" + user)
    allCurrencies = json.loads(response_API.text)          
    return allCurrencies

def resetBalance():
    response_API = requests.get(rootApi + "/resetBalance/" + user + "/" + secret)   
    return response_API.status_code == 200

# createOrders([Order(currencyPair=CurrencyPair("USDT", "ACA"), amount=100), Order(currencyPair=CurrencyPair("USDT", "ACA"), amount=1000), Order(currencyPair=CurrencyPair("USDT", "ACA"), amount=1000)])