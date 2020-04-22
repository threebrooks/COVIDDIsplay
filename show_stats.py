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
import shutil
from lxml import etree
import glob

def replaceImgTags(date):
  with open("show.html") as fp:
    allLines = fp.read()
    allLines = re.sub("\.png","_"+date+".png", allLines)
  with open("/var/www/html/index.html","wb") as fp:
    fp.write(str.encode(allLines))

def majorSort(e):
  return e[1][-1]

def loadNYTUS():
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

def loadNYTMA():
  with open("covid-19-data/us-counties.csv") as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    lineData = list(csvreader)
    major_col = 1
    confirmed_col = 4
    deaths_col = 5
   
    confirmedData = {}
    deathsData = {}
    for rowIdx in range(len(lineData)):
      if (rowIdx == 0):
        continue
      row = lineData[rowIdx]
      if (row[2] != "Massachusetts"):
        continue
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

def loadCSSEWorld():
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

def getPopulation(country, CSC):
  if (CSC == "World"):
    minPop = 1E6
  elif (CSC == "US"):
    minPop = 1E6
  else:
    minPop = 1
  if country in pd.population_data:
    if (pd.population_data[country] < minPop):
      return 1E20
    else:
      return pd.population_data[country] 
  else:
    #print("Making up population of"+country)
    return 1E20

if (os.geteuid() != 0):
  print("Not sudo")
  sys.exit(-1)

while(True):
  for f in glob.glob("/var/www/html/*.png"):
    os.unlink(f)

  data_secs = str(time.time())

  for CSC in ["World", "US", "MA"]:
    if (CSC == "US" or CSC == "MA"):
      print("Pulling NYT data")
      gitRepo = "https://github.com/nytimes/covid-19-data"
      gitDir = "covid-19-data"
    else:
      print("Pulling CSSE data")
      gitRepo = "https://github.com/CSSEGISandData/COVID-19"
      gitDir = "COVID-19"
  
    if (os.path.isdir(gitDir)):
      os.system("cd "+gitDir+"; git pull; cd ..")
    else:
      os.system("git clone "+gitRepo)
    data_date = subprocess.check_output(['sh', '-c', 'cd '+gitDir+'; git log -1 --format="%at" | xargs -I{} date -d @{} "+%m/%d %H:%M"; cd ..']).decode("UTF-8")
  
    if (CSC == "World"):
      (confirmedData, deathsData) = loadCSSEWorld()
    elif (CSC == "US"):
      (confirmedData, deathsData) = loadNYTUS()
    else:
      (confirmedData, deathsData) = loadNYTMA()
  
    for major in confirmedData.keys():
      confirmedData[major] = [100.0*x/getPopulation(major, CSC) for x in confirmedData[major]]
      deathsData[major] = [100.0*x/getPopulation(major, CSC) for x in deathsData[major]]

    trimDays = 31
    for major in confirmedData.keys():
      confirmedData[major] = confirmedData[major][-trimDays:]
      deathsData[major] = deathsData[major][-trimDays:]
  
    sortedMajors = [(k, v) for k, v in deathsData.items()]
    sortedMajors.sort(reverse=True, key=majorSort)
    sortedMajors = [k for (k, v) in sortedMajors]

    mandatory = ["Massachusetts", "Germany", "US", "Middlesex", "Suffolk"]
    totalLabeled = 6
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
  
    al.showData(CSC, confirmedData, deathsData, shown_majors, labeled_majors, data_date, data_secs)
  replaceImgTags(data_secs)
  time.sleep(60*60)
   
