import sys
import math
from scipy.interpolate import spline
from scipy.ndimage.filters import gaussian_filter1d
import matplotlib.pyplot as plt

def safeLog(a):
  if (a == 0):
    return -1E20
  else:
    return math.log(a)

def smoothPlot(ax, x, y, major, log):
  ysmoothed = gaussian_filter1d(y, sigma=1)
  if (log):
    ax.set_yscale("log")
  ax.plot(x, ysmoothed, label=major)

def getSlopeData(hashData, applyLog, dayDist):
  logData = {}
  for key in hashData:
    logData[key] = []
    for idx in range(len(hashData[key])):
      curr = hashData[key][idx]
      if (applyLog):
        logData[key].append(safeLog(curr))
      else:
        logData[key].append(curr)

  slopeData = {}
  for key in logData:
    slopeData[key] = []
    for idx in range(1, len(logData[key])):
      slope = 0
      for idx2 in range(1, dayDist+1):
        if ((idx-idx2 >= 0) and (logData[key][idx-idx2] > -1E15)):
          slope = logData[key][idx]-logData[key][idx-idx2]
      slopeData[key].append(slope)

  return (slopeData)

population = {
  "New York":  19E6,
  "New Jersey":  8.9E6,
  "Michigan":  8.9E6,
  "Louisiana": 4.6E6,
  "Washington": 7.54E6,
  "Massachusetts": 6.9E6,
  "California": 39E6,
  "Florida": 21E6,

  "Italy": 60E6,
  "Spain": 46E6,
  "US": 327E6,
  "France": 67E6,
  "China": 1386E6,
  "Germany": 83E6,
}


def showData(confirmedData, deathsData, majors):  
  fig, axs = plt.subplots(2, 2)

  max_length = 0
  for major in majors:
    max_length = max(max_length, max(len(confirmedData[major]), len(deathsData[major])))
  
  for major in majors:
    smoothPlot(axs[0][0], range(max_length-len(confirmedData[major]), max_length), confirmedData[major], major, True)
  axs[0][0].legend(loc='best')
  axs[0][0].set_title("Log total confirmed")
  
  confirmedDailyData = getSlopeData(confirmedData, False, 1)
  for major in majors:
    smoothPlot(axs[0][1], range(max_length-len(confirmedDailyData[major]), max_length), confirmedDailyData[major], major, False)
  axs[0][1].set_title("Daily confirmed")

  for major in majors:
    smoothPlot(axs[1][0], range(max_length-len(deathsData[major]), max_length), deathsData[major], major, True)
  axs[1][0].legend(loc='best')
  axs[1][0].set_title("Log total deaths")
  
  deathsDailyData = getSlopeData(deathsData, False, 1)
  for major in majors:
    smoothPlot(axs[1][1], range(max_length-len(deathsDailyData[major]), max_length), deathsDailyData[major], major, False)
  axs[1][1].set_title("Daily deaths")

  mng = plt.get_current_fig_manager()
  mng.resize(*mng.window.maxsize())
  plt.show(block=False)
  plt.pause(0.001)
