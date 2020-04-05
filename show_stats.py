import sys
import csv
import math
import numpy as np
import analyze_lib as al
import re
import os
import time
import matplotlib.pyplot as plt
import population_data as pd
import subprocess

def majorSort(e):
  return e[1][-1]

def loadNYT():
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
  return (confirmedData, deathsData)

def loadCSSE():
  for mode in ["confirmed", "deaths"]:
    with open("COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_"+mode+"_global.csv") as csvfile:
      csvreader = csv.reader(csvfile, delimiter=',')
      lineData = list(csvreader)
      hashData = {}
      major_col = -1
      first_date_col = -1
     
      for rowIdx in range(len(lineData)):
        if (rowIdx == 0):
          for idx in range(len(lineData[0])):
            column = lineData[0][idx]
            if (re.match(".*country.*", column, flags=re.IGNORECASE)):
              major_col = idx
            elif (first_date_col == -1 and re.match(".*[0-9]+\/[0-9]+\/[0-9]+.*", column, flags=re.IGNORECASE)):
              first_date_col = idx
          continue
        if (major_col == -1 or first_date_col == -1):
          print("Couldn't find all columns!")
          sys.exit(-1)
        row = lineData[rowIdx]
        major = row[major_col] 
        if (major not in hashData):
          hashData[major] = [0]*(len(row)-first_date_col)
        try:
          for colIdx in range(first_date_col, len(row)):
            el = row[colIdx]
            if (el == ""):
              el = "0"
            elif (int(el) < 0):
              el = str(hashData[major][colIdx-first_date_col-1])
            hashData[major][colIdx-first_date_col] += int(el)
        except:
          print(str(row))
          sys.exit(-1)
    if (mode == "confirmed"):
      confirmedData = hashData
    else:
      deathsData = hashData
    
  return (confirmedData, deathsData)


while(True):
  for StateCountry in [False, True]:
    if (StateCountry):
      print("Running US data")
      gitRepo = "https://github.com/nytimes/covid-19-data"
      gitDir = "covid-19-data"
    else:
      print("Running World data")
      gitRepo = "https://github.com/CSSEGISandData/COVID-19"
      gitDir = "COVID-19"
  
    if (os.path.isdir(gitDir)):
      os.system("cd "+gitDir+"; git pull; cd ..")
    else:
      os.system("git clone "+gitRepo)
    data_date = subprocess.check_output(['sh', '-c', 'cd '+gitDir+'; git log -1 --format="%at" | xargs -I{} date -d @{} "+%m/%d %H:%M"; cd ..']).decode("UTF-8")
  
    if (StateCountry):
      (confirmedData, deathsData) = loadNYT()
    else:
      (confirmedData, deathsData) = loadCSSE()
  
    trimDays = 31
    for major in confirmedData.keys():
      confirmedData[major] = confirmedData[major][-trimDays:]
      deathsData[major] = deathsData[major][-trimDays:]
  
    sortedMajors = [(k, v) for k, v in deathsData.items()]
    sortedMajors.sort(reverse=True, key=majorSort)
    sortedMajors = [k for (k, v) in sortedMajors]
    majors = []
  
    mandatory = ["Massachusetts", "Germany", "Norway", "Sweden", "US"]
    totalNumDisplayed = 5
    numMandatory = 0
    for man in mandatory:
      numMandatory += sortedMajors.count(man)
    for idx in range(len(sortedMajors)):
      if ((sortedMajors[idx] not in mandatory) and (len(majors) < (totalNumDisplayed-numMandatory))):
        majors.append(sortedMajors[idx])
    for man in mandatory:
      if (sortedMajors.count(man) > 0):
        majors.append(man)
    
    for major in majors:
      confirmedData[major] = [100.0*x/pd.population_data[major] for x in confirmedData[major]]
      deathsData[major] = [100.0*x/pd.population_data[major] for x in deathsData[major]]
   
    if (StateCountry):
      outFname = "US.png"
    else:
      outFname = "World.png"
    al.showData(StateCountry, outFname, confirmedData, deathsData, majors, data_date)
  time.sleep(60*60)
   
