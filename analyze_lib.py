import sys
import math
from scipy.interpolate import spline
from scipy.ndimage.filters import gaussian_filter1d
import matplotlib.pyplot as plt
import datetime
import matplotlib.ticker as mticker
import copy

def safeLog(a):
  if (a == 0):
    return -1E5
  else:
    return math.log(a)

def smoothPlot(ax, x, y, major, should_label, log):
  ysmoothed = gaussian_filter1d(y, sigma=1.5)
  if (log):
    ax.set_yscale("log")
  if (should_label):
    ax.plot(x, ysmoothed, label=major)
  else:
    ax.plot(x, ysmoothed, color=[0.9, 0.9, 0.9])

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
        if ((idx-idx2 >= 0) and (logData[key][idx-idx2] > -1E5)):
          slope = logData[key][idx]-logData[key][idx-idx2]
      slopeData[key].append(slope)

  return (slopeData)

def showSingleData(CSC, deathsData, majors, labeledMajors, data_date, data_secs):  
  fig, axs = plt.subplots(1, 1)

  max_length = 0
  for major in majors:
    max_length = max(max_length, len(deathsData[major]))
 
  deathsDailyData = getSlopeData(deathsData, False, 1)
  for major in majors:
    smoothPlot(axs, range(max_length-len(deathsDailyData[major]), max_length), deathsDailyData[major], major, major in labeledMajors, False)
  axs.set_title("Daily deaths")

  plt.suptitle(CSC+" COVID-19 stats, Date:"+data_date)

  fig.tight_layout(pad=1.0)
  plt.grid()
  plt.subplots_adjust(top=0.85)
  plt.savefig("/var/www/html/"+CSC+"_"+data_secs+".png")
  plt.close()
  print("Image saved.")


def showData(CSC, confirmedData, deathsData, majors, labeledMajors, data_date, data_secs):  
  fig, axs = plt.subplots(2, 2)

  max_length = 0
  for major in majors:
    max_length = max(max_length, max(len(confirmedData[major]), len(deathsData[major])))
 
  for major in majors:
    smoothPlot(axs[0][0], range(max_length-len(confirmedData[major]), max_length), confirmedData[major], major, major in labeledMajors, True)
  axs[0][0].legend(loc='best')
  axs[0][0].set_title("Log total confirmed")
  axs[0][0].yaxis.set_major_formatter(mticker.ScalarFormatter())
  
  confirmedDailyData = getSlopeData(confirmedData, False, 1)
  for major in majors:
    smoothPlot(axs[0][1], range(max_length-len(confirmedDailyData[major]), max_length), confirmedDailyData[major], major, major in labeledMajors, False)
  axs[0][1].set_title("Daily confirmed")

  for major in majors:
    smoothPlot(axs[1][0], range(max_length-len(deathsData[major]), max_length), deathsData[major], major, major in labeledMajors, True)
  axs[1][0].set_title("Log total deaths")
  axs[1][0].yaxis.set_major_formatter(mticker.ScalarFormatter())
  
  deathsDailyData = getSlopeData(deathsData, False, 1)
  for major in majors:
    smoothPlot(axs[1][1], range(max_length-len(deathsDailyData[major]), max_length), deathsDailyData[major], major, major in labeledMajors, False)
  axs[1][1].set_title("Daily deaths")

  plt.suptitle(CSC+" COVID-19 stats, % of population, Date:"+data_date)

  fig.tight_layout(pad=1.0)
  plt.subplots_adjust(top=0.85)
  plt.savefig("/var/www/html/"+CSC+"_"+data_secs+".png")
  plt.close()
  print("Image saved.")
