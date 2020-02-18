import cv2
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import matplotlib
from helperFunctions import getFileNames, reProjectionError, findCorners

def singleCamera(folderName):
    imgShape, objP,imgP,fails,success,_ = findCorners(folderName)

    ret, cmtx, distCoeff, rVecs, tVecs, = cv2.calibrateCamera(objP,imgP, \
            imgShape[::-1],None,None)

    print('Camera Matrix: \n',cmtx)
    print('Distortion Coefficients: \n',distCoeff)

    # reprojection error
    error, avgError = reProjectionError(objP,imgP,rVecs,tVecs,cmtx,distCoeff)

    return cmtx,avgError, error, distCoeff, objP, imgP, imgShape, fails,success,rVecs,tVecs

def stereoCamera(folder1,folder2):

    cm1,avgError1, error1, dc1, objP1, imgP1, imgShape1, fail1,success1,rVecs1,tVecs1 = \
            singleCamera(folder1)
    cm2,avgError2, error2, dc2, objP2, imgP2, imgShape2, fail2,success2,rVecs2,tVecs2 = \
            singleCamera(folder2)

    # delete images if corners are not detected in one of the image sets
    if len(fail1) != 0:
        for entry in fail1:
            if entry in success2:
                idx = success2.index(entry)
                del objP2[idx]
                del imgP2[idx]
                del success2[idx]
                del rVecs2[idx]
                del tVecs2[idx]
                del error2[idx]
    if len(fail2) != 0:
        for entry in fail2:
            if entry in success1:
                idx = success1.index(entry)
                del objP1[idx]
                del imgP1[idx]
                del success1[idx]
                del rVecs1[idx]
                del tVecs1[idx]
                del error1[idx]

    objP = objP1
    imgShape = imgShape1

    ret, c1,d1,c2,d2,R,T,_,_ = cv2.stereoCalibrate(objP,imgP1,imgP2,cm1,dc1,cm2,dc2, \
            imgShape)

    print('Camera 1 Matrix (RGB): \n',c1)
    print('Camera 2 Matrix (RGB): \n',c2)
    print('Rotation Matrix Camera1 -> Camera2: \n',R)
    print('Translation Matrix Camera1 -> Camera2: \n',T)

    return error1,error2,success1,success2,avgError1,avgError2

def main():
    dataSet = sys.argv[1]
    print(type(dataSet))
    if dataSet == '1':
        folder = 'RGB'
        singleCamera(folder)

    elif dataSet == '2':
        folder1 = '2-Intel/RGB'
        folder2 = '2-Intel/IR'
        error1,error2,success1,success2,avgError1,avgError2 = stereoCamera(folder1,folder2)

    elif dataSet == '3':
        folder1 = '3-Kinect2/RGB'
        folder2 = '3-Kinect2/IR'
        error1,error2,success1,success2,avgError1,avgError2 = stereoCamera(folder1,folder2)
    else:
        print('please enter valid value')
    return 0

if __name__ == "__main__":
    main()
