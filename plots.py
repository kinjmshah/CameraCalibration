import matplotlib.pyplot as plt
import matplotlib
import cv2
import numpy as np
import os
import sys

def Plots(success,error,avgError,allFileNames,dataSet,folderName):
    numImg = len(allFileNames)

    fig = plt.figure()

    plotError = [0]*numImg
    xtic = []

    for name in allFileNames:
        xtic.append(name[0:2])

    for entry in success:
        idx = allFileNames.index(entry)
        successIdx = success.index(entry)
        plotError[idx] = error[successIdx]


    x = list(range(numImg))
    yavg = [avgError]*numImg

    plt.bar(x,plotError)
    plt.plot(x,yavg,'r-')
    plt.xticks(x,xtic)
    plt.xlabel('Image File Number')
    plt.ylabel('Re-projection Error')
    fig.savefig('DataSet' + dataSet + folderName + 'Plot.png')

