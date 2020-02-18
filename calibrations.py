import cv2
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import matplotlib
from helperFunctions import getFileNames, reProjectionError, findCorners

def singleCamera(folderName):

    # Find Corners
    imgShape, objP,imgP,fails,success,fN = findCorners(folderName)

    # Perform Calibration
    ret, cmtx, distCoeff, rVecs, tVecs, = cv2.calibrateCamera(objP,imgP, \
            imgShape[::-1],None,None)

    print('OUTPUT -------------')
    print('Camera Matrix: \n',cmtx)
    print('Distortion Coefficients: \n',distCoeff)

    # Reprojection
    error, avgError = reProjectionError(objP,imgP,rVecs,tVecs,cmtx,distCoeff)

    # IF WANT TO REMOVE THE IMAGE WITH THE MAXIMUM PROJECTION ERROR SET TO 1
    removeMaxError = 0 # set to 0 if do not want to remove
    if removeMaxError == 1:

        maxEr1 = max(error) #max error in RGB
        idx1 = error.index(maxEr1) #index of max error in RGB

        del objP[idx1]
        del imgP[idx1]
        del success[idx1]
        del rVecs[idx1]
        del tVecs[idx1]
        del error[idx1]

        ret, cmtx, distCoeff, rVecs, tVecs, = cv2.calibrateCamera(objP,imgP, \
                imgShape[::-1],None,None)
        print('UDATED OUTPUT ----------')
        print('Camera Matrix: \n',cmtx)
        print('Distortion Coefficients: \n',distCoeff)
        # new reprojection error
        error, avgError = reProjectionError(objP,imgP,rVecs,tVecs,cmtx,distCoeff)

    return cmtx,avgError, error, distCoeff, objP, imgP, imgShape, fails,success,rVecs,tVecs,fN

def stereoCamera(folder1,folder2):

    # Perform single camera calibration for each camera to get initialized parameters
    # for stereo calibration
    cm1,avgError1, error1, dc1, objP1, imgP1, imgShape1, fail1,success1,rVecs1,tVecs1, fN1 = \
            singleCamera(folder1)
    cm2,avgError2, error2, dc2, objP2, imgP2, imgShape2, fail2,success2,rVecs2,tVecs2, fN2 = \
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

    # redefine parameters that are the same for both image sets
    objP = objP1
    imgShape = imgShape1

    ret, c1,d1,c2,d2,R,T,_,_ = cv2.stereoCalibrate(objP,imgP1,imgP2,cm1,dc1,cm2,dc2, \
            imgShape)

    print('OUTPUT -------------------')
    print('Camera 1 Matrix (RGB): \n',c1)
    print('Camera 2 Matrix (IR): \n',c2)
    print('Rotation Matrix Camera1 -> Camera2: \n',R)
    print('Translation Matrix Camera1 -> Camera2: \n',T)

    error1_final, avgError1_final = reProjectionError(objP,imgP1,rVecs1,tVecs1,cm1,dc1)
    error2_final, avgError2_final = reProjectionError(objP,imgP2,rVecs2,tVecs2,cm2,dc2)


    removeMaxError = 0 # set to 0 if do not want to remove
    if removeMaxError == 1:

        maxEr1 = max(error1_final) #max error in RGB
        idx1 = error1_final.index(maxEr1) #index of max error in RGB

        del objP1[idx1]
        del imgP1[idx1]
        del success1[idx1]
        del rVecs1[idx1]
        del tVecs1[idx1]
        del error1[idx1]

        del objP2[idx1]
        del imgP2[idx1]
        del success2[idx1]
        del rVecs2[idx1]
        del tVecs2[idx1]
        del error2[idx1]

        maxEr2 = max(error2_final) #max error in IR
        idx2 = error2_final.index(maxEr2) #max error in IR

        del objP1[idx2]
        del imgP1[idx2]
        del success1[idx2]
        del rVecs1[idx2]
        del tVecs1[idx2]
        del error1[idx2]

        del objP2[idx2]
        del imgP2[idx2]
        del success2[idx2]
        del rVecs2[idx2]
        del tVecs2[idx2]
        del error2[idx2]

        objP = objP1
        imgShape = imgShape1

        ret, c1,d1,c2,d2,R,T,_,_ = cv2.stereoCalibrate(objP,imgP1,imgP2,cm1,dc1,cm2,dc2, \
                imgShape)

        print('UPDATED OUTPUT --------')
        print('Camera 1 Matrix (RGB): \n',c1)
        print('Camera 2 Matrix (IR): \n',c2)
        print('Rotation Matrix Camera1 -> Camera2: \n',R)
        print('Translation Matrix Camera1 -> Camera2: \n',T)

        error1_final, avgError1_final = reProjectionError(objP,imgP1,rVecs1,tVecs1,cm1,dc1)
        error2_final, avgError2_final = reProjectionError(objP,imgP2,rVecs2,tVecs2,cm2,dc2)

    return error1_final,error2_final,success1,success2,avgError1_final,avgError2_final,fN1,fN2
