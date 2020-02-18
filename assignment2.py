import cv2
import numpy as np
import os
import sys

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
    print(imagesAllFileNames)

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
            print('Pattern not found for ',fileName)
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
    print('All Error: \n',errorAll)
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
        elif f1count < f2count:
            ogP_stereo = ogPoints[:-f2count]
            for i in range(f2count):
                maxval = max(nE1)
                maxidx = nE1.index(maxval)
                del nE1[maxidx]
                del imgP1_stereo[maxidx]
                del rVec1[maxidx]
                del tVec1[maxidx]

    ret, cm1,dc1,cm2,dc2,R,T,E,F = cv2.stereoCalibrate(ogP_stereo,\
            imgP1_stereo,imgP2_stereo,c1,d1,c2,d2,imgShape)#,termCriteria,flags=flags)
    print('----------------FINAL OUTPUTS------------')
    print('Camera Matrix 1: \n',cm1)
    print('Camera Matrix 2: \n',cm2)
    print('Rotation Matrix Between Camera 1 and 2: \n',R)
    print('Translation Matrix Between Camera 1 and 2: \n',T)

    errorAll1, avgError1 = reProjectionError(ogP_stereo,imgP1_stereo,rVec1,tVec1,cm1,dc1)
    errorAll2, avgError2 = reProjectionError(ogP_stereo,imgP2_stereo,rVec2,tVec2,cm2,dc2)

if __name__ == "__main__":
    print('############### Data Set 1 #########################\n')
    folder = 'RBG'
    imagesAllFileNames,folderPath = getFileNames(folder)
    imagesAllFileNames.sort()
    _,avgError,_,_,_,_,_,_,error,_,_ = singleCamCalibration(folder)

    print('############### Data Set 2 #########################\n')
    folder1 = '2-Intel/RGB'
    folder2 = '2-Intel/IR'
    stereoCalib_2cam(folder1,folder2)

    print('############### Data Set 3 #########################\n')
    folder1 = '3-Kinect2/RGB'
    folder2 = '3-Kinect2/IR'
    stereoCalib_2cam(folder1,folder2)

