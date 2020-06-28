import sys
import math
from scipy.interpolate import spline
from scipy.ndimage.filters import gaussian_filter1d
import matplotlib
import matplotlib.pyplot as plt
import datetime
import matplotlib.ticker as mticker
import copy
import numpy as np
import matplotlib.dates as mdates

def safeLog(a):
  if (a == 0):
    return -1E5
  else:
    return math.log(a)

def smoothPlot(ax, x, y, major, should_label, logX, logY):
  ysmoothed = gaussian_filter1d(y, sigma=1.5)
  if (logX):
    ax.set_xscale("log")
  if (logY):
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
    for idx in range(0, len(logData[key])):
      slope = 0
      for idx2 in range(0, dayDist+1):
        if ((idx-idx2 >= 0) and (logData[key][idx-idx2] > -1E5)):
          slope = logData[key][idx]-logData[key][idx-idx2]
      slopeData[key].append(slope)

  return (slopeData)

def majorSort(e):
  return e[1][-1]

def getLabeledShown(data):
  sortedMajors = [(k, v) for k, v in data.items()]
  sortedMajors.sort(reverse=True, key=majorSort)
  sortedMajors = [k for (k, v) in sortedMajors]

  mandatory = ["Massachusetts", "Germany", "US", "Middlesex", "Suffolk"]
  totalLabeled = 7
  totalShown = 2*totalLabeled
  labeled_majors = []
  shown_majors = []
  for man in mandatory:
    if (man in sortedMajors):
      labeled_majors.append(man)
      shown_majors.append(man)
  for idx in range(len(sortedMajors)):
    if ((sortedMajors[idx] not in labeled_majors) and (len(labeled_majors) < totalLabeled)):
      labeled_majors.append(sortedMajors[idx])
    if ((sortedMajors[idx] not in shown_majors) and (len(shown_majors) < totalShown)):
      shown_majors.append(sortedMajors[idx])
  labeled_majors.reverse()
  shown_majors.reverse()
  return (labeled_majors, shown_majors)
 
def showSingleData(CSC, deathsData, data_date, data_secs):  
  deathsDailyData = getSlopeData(deathsData, False, 1)
  (labeledMajors, shownMajors) = getLabeledShown(deathsDailyData)
  fig, axs = plt.subplots(1, 1)

  max_length = 0
  for major in shownMajors:
    max_length = max(max_length, len(deathsData[major]))

  base = datetime.datetime.today()
  date_list = [base - datetime.timedelta(days=max_length-x) for x in range(max_length)]
 
  max_val = 0
  for major in shownMajors:
    max_val = max(max_val, np.max(deathsDailyData[major]))
  for major in shownMajors:
    smoothPlot(axs, date_list, deathsDailyData[major], major, major in labeledMajors, False, False)
  locator = mdates.AutoDateLocator()
  formatter = mdates.AutoDateFormatter(locator)
  axs.xaxis.set_major_locator(locator)
  axs.xaxis.set_major_formatter(formatter)
  axs.set_ylim(0, max_val)
  axs.set_title("Daily deaths")

  plt.suptitle(CSC+" COVID-19 stats, Date:"+data_date)

  fig.tight_layout(pad=1.0)
  fig.autofmt_xdate()
  plt.grid()
  plt.subplots_adjust(top=0.85)
  plt.savefig("/var/www/html/"+CSC+"_"+data_secs+".png")
  plt.close()
  print("Image saved.")


def showData(CSC, confirmedData, deathsData, data_date, data_secs):  
  confirmedDailyData = getSlopeData(confirmedData, False, 7)
  (labeledConfirmedMajors, shownConfirmedMajors) = getLabeledShown(confirmedDailyData)
  fig, axs = plt.subplots(1, 2)

  max_length = 0
  for major in shownConfirmedMajors:
    max_length = max(max_length, max(len(confirmedData[major]), len(deathsData[major])))
 
  for major in shownConfirmedMajors:
    smoothPlot(axs[0], confirmedData[major], confirmedDailyData[major], major, major in labeledConfirmedMajors, True, True)
  axs[0].set_title("Confirmed")
  axs[0].legend(loc='best')

  deathsDailyData = getSlopeData(deathsData, False, 7)
  (labeledDeathsMajors, shownDeathsMajors) = getLabeledShown(deathsDailyData)
  for major in shownDeathsMajors:
    smoothPlot(axs[1], deathsData[major], deathsDailyData[major], major, major in labeledDeathsMajors, True, True)
  axs[1].set_title("Deaths")
  axs[1].legend(loc='best')

  fig.tight_layout(pad=1.0)
  plt.subplots_adjust(top=0.85)
  plt.suptitle(CSC+" COVID-19 stats, Date:"+data_date)
  plt.savefig("/var/www/html/"+CSC+"_"+data_secs+".png")
  plt.close()
  print("Image saved.")

