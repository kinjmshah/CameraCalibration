import cv2
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import matplotlib

# this function enables me to extract file names from a folder
def getFileNames(FolderName):
    cwd = os.getcwd()
    imageFolderPath = cwd + '/' + FolderName
    fileNames = os.listdir(imageFolderPath)

    fext = '.png'

    for name in fileNames:
        if (fext in name) == False:
            fileNames.remove(name)

    return fileNames,imageFolderPath

# referenced opencv camera calibration tutorials to understand the openCV functions available
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html
# some of the optimizations employed were suggested by the tutorial to improve code performance

# This function is to evaluate the images and identify the corners
def evaluateImages(folderName):
    termCond = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    row = 6
    col = 7

    # initialize object points array
    objPoint_singleImage = np.zeros((row*col, 3),np.float32)
    objectLen = len(objPoint_singleImage)

    countRows = 0
    countCols = 0
    failCount = 0

    for i in range(objectLen): # total array len
        objPoint_singleImage[i,0] = countRows
        objPoint_singleImage[i,1] = countCols

        countRows += 1

        if countRows == row:
            countRows = 0
            countCols += 1

    # initialize final point storage

    objectPoints = [] #3D
    objectPointsOrig = []
    imagePoints = [] #2D

    # read in image file names
    imagesAllFileNames,folderPath = getFileNames(folderName)
    imagesAllFileNames.sort()

    for fileName in imagesAllFileNames:
        filePath = folderPath + '/' + fileName

        image = cv2.imread(filePath) # read in image
        #print(image)

        grayScale = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY) # convert to gray scale
        #print(grayScale)
        # find corners
        retval,corners = cv2.findChessboardCorners(grayScale,(row,col),None)

        objectPointsOrig.append(objPoint_singleImage)

        # if pattern was found execute below
        if retval == True:

            # store the object points
            objectPoints.append(objPoint_singleImage)

            # find the corresponding corners in image space
            imgCorners = cv2.cornerSubPix(grayScale,corners,(11,11),(-1,-1),termCond)

            # store image coordinates
            imagePoints.append(imgCorners)
        else:
            failCount += 1

    imgShape = grayScale.shape

    return imgShape, objectPoints,imagePoints,objectPointsOrig,failCount

# calculates reprojection error
def reProjectionError(objectPoints,imagePoints,rotVec,transVec,camMtx,distCoeff):
    totalError = 0
    errorStore = []

    for i in range(len(objectPoints)):
        projectionPoints, _ = cv2.projectPoints(objectPoints[i], rotVec[i], transVec[i], camMtx, distCoeff)
        error = cv2.norm(imagePoints[i],projectionPoints, cv2.NORM_L2)/len(projectionPoints)
        errorStore.append(error)
        totalError += error
        #print(totalError)

    avgError = totalError/len(objectPoints)
    print("average error: ", avgError)

    return errorStore,avgError

# performs single camera calibration
def singleCamCalibration(folderName):

    imgShape, objectPoints,imagePoints,objectPointsOriginal,failCount = evaluateImages(folderName)

    ret,camMtx, distCoeff, rotVec, transVec = cv2.calibrateCamera(objectPoints, imagePoints, imgShape[::-1],None,None)
    print('Camera Matrix: \n',camMtx)
    print('Distortion Coefficients: \n',distCoeff)
    # reprojection error
    errorAll,avgError = reProjectionError(objectPoints,imagePoints,rotVec,transVec,camMtx,distCoeff)
    return camMtx,avgError,distCoeff,objectPoints,imagePoints,imgShape,objectPointsOriginal,failCount,errorAll,rotVec,transVec


def stereoCalib_2cam(folder1,folder2):

    #termCriteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 30, 0.00001)

    print('----------------CAMERA 1--------------')
    c1,e1,d1,objP1,imgP1,imgShape,ogPoints,f1count,errorArray1,rVec1,tVec1 = singleCamCalibration(folder1)
    print('----------------CAMERA 2--------------')
    c2,e2,d2,objP2,imgP2,_,_,f2count,errorArray2,rVec2,tVec2 = singleCamCalibration(folder2)

    imgP2_stereo = imgP2
    imgP1_stereo = imgP1
    ogP_stereo = ogPoints
    idxStore =[]
    # if you need to trim, trim images resulting in highest error
    if (f1count or f2count) > 0:
        nE2 = errorArray2
        nE1 = errorArray1
        if f1count > f2count:
            ogP_stereo = ogPoints[:-f1count]
            for i in range(f1count):
                maxval = max(nE2)
                maxidx = nE2.index(maxval)
                del nE2[maxidx]
                del imgP2_stereo[maxidx]
                del rVec2[maxidx]
                del tVec2[maxidx]
                idxStore.append(maxidx)
        elif f1count < f2count:
            ogP_stereo = ogPoints[:-f2count]
            for i in range(f2count):
                maxval = max(nE1)
                maxidx = nE1.index(maxval)
                del nE1[maxidx]
                del imgP1_stereo[maxidx]
                del rVec1[maxidx]
                del tVec1[maxidx]
                idxStore.append(maxidx)

    ret, cm1,dc1,cm2,dc2,R,T,E,F = cv2.stereoCalibrate(ogP_stereo,\
            imgP1_stereo,imgP2_stereo,c1,d1,c2,d2,imgShape)#,termCriteria,flags=flags)
    print('----------------FINAL OUTPUTS------------')
    print('Camera Matrix 1: \n',cm1)
    print('Camera Matrix 2: \n',cm2)
    print('Rotation Matrix Between Camera 1 and 2: \n',R)
    print('Translation Matrix Between Camera 1 and 2: \n',T)

    errorAll1, avgError1 = reProjectionError(ogP_stereo,imgP1_stereo,rVec1,tVec1,cm1,dc1)
    errorAll2, avgError2 = reProjectionError(ogP_stereo,imgP2_stereo,rVec2,tVec2,cm2,dc2)

    return errorAll1, errorAll2, avgError1, avgError2, idxStore

if __name__ == "__main__":
    print('############### Data Set 1 #########################\n')
    folder = 'RGB'
    imagesAllFileNames,folderPath = getFileNames(folder)
    imagesAllFileNames.sort()
    _,avgError,_,_,_,_,_,_,error,_,_ = singleCamCalibration(folder)
    aE = np.ones(len(imagesAllFileNames))*avgError
    fig1 = plt.figure()
    plt.plot(range(len(imagesAllFileNames)),error,'o')
    plt.plot(range(len(imagesAllFileNames)),aE,'-')
    x = list(range(len(imagesAllFileNames)))
    plt.xticks(range(len(imagesAllFileNames)),x)
    plt.xlabel('Image File Number')
    plt.ylabel('Re-Projection Error')
    fig1.savefig('DataSet1')

    print('############### Data Set 2 #########################\n')
    folder1 = '2-Intel/RGB'
    folder2 = '2-Intel/IR'
    error1,error2,avgError1,avgError2,idxStore=stereoCalib_2cam(folder1,folder2)

    imagesAllFileNames1,_ = getFileNames(folder1)
    imagesAllFileNames1.sort()
    imagesAllFileNames2,_ = getFileNames(folder2)
    imagesAllFileNames2.sort()

    x1 = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
    for idx in idxStore:
        del imagesAllFileNames1[idx]
        del x1[idx]

    del imagesAllFileNames2[14]
    del imagesAllFileNames2[15]

    aE1 = np.ones(len(imagesAllFileNames1))*avgError1
    aE2 = np.ones(len(imagesAllFileNames2))*avgError2

    aE = aE1
    imagesAllFileNames = imagesAllFileNames1
    error = error1
    fig = plt.figure()
    plt.plot(range(len(imagesAllFileNames)),error,'o')
    plt.plot(range(len(imagesAllFileNames)),aE,'-')
    plt.xticks(range(len(imagesAllFileNames)),x1)
    plt.xlabel('Image File Number')
    plt.ylabel('Re-Projection Error')
    fig.savefig('DataSet2_RGB')

    aE = aE2
    imagesAllFileNames = imagesAllFileNames2
    error = error2
    fig = plt.figure()
    plt.plot(range(len(imagesAllFileNames)),error,'o')
    plt.plot(range(len(imagesAllFileNames)),aE,'-')
    x = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,16,17,18,19,20]
    plt.xticks(range(len(imagesAllFileNames)),x)
    plt.xlabel('Image File Number')
    plt.ylabel('Re-Projection Error')
    fig.savefig('DataSet2_IR')

    print('############### Data Set 3 #########################\n')
    folder1 = '3-Kinect2/RGB'
    folder2 = '3-Kinect2/IR'
    error1,error2,avgError1,avgError2,idxStore=stereoCalib_2cam(folder1,folder2)

    imagesAllFileNames1,_ = getFileNames(folder1)
    imagesAllFileNames1.sort()
    imagesAllFileNames2,_ = getFileNames(folder2)
    imagesAllFileNames2.sort()

    for idx in idxStore:
        del imagesAllFileNames1[idx]

    aE1 = np.ones(len(imagesAllFileNames1))*avgError1
    aE2 = np.ones(len(imagesAllFileNames2))*avgError2

    aE = aE1
    imagesAllFileNames = imagesAllFileNames1
    error = error1
    fig = plt.figure()
    plt.plot(range(1,21),error,'o')
    plt.plot(range(1,21),aE,'-')
    x = list(range(1,21))
    plt.xticks(range(1,21),x)
    plt.xlabel('Image File Number')
    plt.ylabel('Re-Projection Error')
    fig.savefig('DataSet3_RGB')

    aE = aE2
    imagesAllFileNames = imagesAllFileNames2
    error = error2
    fig = plt.figure()
    plt.plot(range(1,21),error,'o')
    plt.plot(range(1,21),aE,'-')
    x = list(range(1,21))
    plt.xticks(range(1,21),x)
    plt.xlabel('Image File Number')
    plt.ylabel('Re-Projection Error')
    fig.savefig('DataSet3_IR')

