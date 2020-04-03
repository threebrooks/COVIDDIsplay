import sys
import csv
import math
import numpy as np
import analyze_lib as al
import re
import os
import time
import matplotlib.pyplot as plt

def majorSort(e):
  return deathsData[e][-1]

while(True):
  if (os.path.isdir("covid-19-data")):
    os.system("cd covid-19-data; git pull; cd ..")
  else:
    os.system("git clone https://github.com/nytimes/covid-19-data")

  with open("covid-19-data/us-states.csv") as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    lineData = list(csvreader)
    major_col = 1
    confirmed_col = 3
    deaths_col = 4
   
    confirmedData = {}
    deathsData = {}
    for rowIdx in range(len(lineData)):
      if (rowIdx == 0):
        continue
      row = lineData[rowIdx]
      major = row[major_col] 
      if (major not in confirmedData):
        confirmedData[major] = []
        deathsData[major] = []
      try:
        confirmedData[major].append(int(row[confirmed_col]))
        deathsData[major].append(int(row[deaths_col]))
      except :
        print(str(sys.exc_info()[0]))
        sys.exit(-1)
  
  sortedMajors = list(deathsData.keys())
  sortedMajors.sort(reverse=True, key=majorSort)
  majors = []
  
  for idx in range(len(sortedMajors)):
    if (idx < 3 or sortedMajors[idx] == "US" or sortedMajors[idx] == "Germany" or sortedMajors[idx] == "Massachusetts"):
      majors.append(sortedMajors[idx])
  
  for major in majors:
    confirmedData[major] = [x/al.population[major] for x in confirmedData[major]]
    deathsData[major] = [x/al.population[major] for x in deathsData[major]]
  
  al.showData(confirmedData, deathsData, majors)
  time.sleep(10)
  plt.close()
   
