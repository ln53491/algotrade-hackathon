from typing import NamedTuple

class CurrencyPair(NamedTuple):
    inCurr: str
    outCurr: str

class Order(NamedTuple):
    currencyPair: CurrencyPair
    amount: int
    
global closedDict
global volumeDict
closedDict = dict()
volumeDict = dict()

closedDict_prevTick = dict()
volumeDict_prevTick = dict()

currNodes = []