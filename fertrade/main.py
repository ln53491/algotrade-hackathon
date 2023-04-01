from graph import *
import threading

tickSecondDuration = 30
allowedPerSecond = 5
pingInterval = 1 / allowedPerSecond + 0.05

global currStartTime
currStartTime = 0
currTick = getTime()
time.sleep(pingInterval)

def startAlgorithm():
    algorithm()
    threading.Timer(tickSecondDuration, startAlgorithm).start()

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
# algorithm()
synchronize()