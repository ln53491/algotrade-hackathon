from graph import *
import threading
import matplotlib.pyplot as plt
global ticks

tickSecondDuration = 3
allowedPerSecond = 5
pingInterval = 1 / allowedPerSecond + 0.05
currency = "ILV"
ticks = [0]

global currStartTime
global startReturningToUSDT
startReturningToUSDT = False
currStartTime = 0
currTick = getTime()
time.sleep(pingInterval)

def startAlgorithm():
    global startReturningToUSDT
    if not startReturningToUSDT:
        ticks.append(ticks[-1] + 1)
        algorithm()

        threading.Timer(tickSecondDuration, startAlgorithm).start()
        threading.Timer(60*10, setReturningToTrue).start()
    else:
        returnToUSDT()

def setReturningToTrue():
    global startReturningToUSDT
    startReturningToUSDT = True

def synchronize():
    global currStartTime
    timer = threading.Timer(pingInterval, synchronize)
    timer.start()
    if getTime() != currTick:
        currStartTime = time.time()
        timer.cancel()
        startAlgorithm()

# pokrece sinkronizaciju tickova
resetBalance()
algorithm()
synchronize()