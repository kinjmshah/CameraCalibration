import cv2
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import matplotlib
from helperFunctions import getFileNames, reProjectionError, findCorners
from calibrations import singleCamera,stereoCamera
from plots import Plots

def main():
    dataSet = sys.argv[1]
    if dataSet == '1':
        folder = 'singleCamCalib'
        _,avgError,error,_,_,_,_,_,success,_,_,fN = singleCamera(folder)
        Plots(success,error,avgError,fN,dataSet,folder)

    elif dataSet == '2':
        folder1 = 'stereoCamCalib/camera1'
        folder2 = 'stereoCamCalib/camers2'

        f1 = folder1[-7:]
        f2 = folder2[-7:]

        error1,error2,success1,success2,avgError1,avgError2,fN1,fN2 = stereoCamera(folder1,folder2)
        Plots(success1,error1,avgError1,fN1,dataSet,f1)
        Plots(success2,error2,avgError2,fN2,dataSet,f2)

    else:
        print('please enter valid value')

    return 0

if __name__ == "__main__":
    main()
