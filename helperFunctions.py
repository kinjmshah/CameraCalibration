import cv2
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import matplotlib as mpl

# function enables extraction of file names from folder
def getFileNames(folderName):
    cwd = os.getcwd()
    imageFolderPath = cwd + '/' + folderName
    fileNames = os.listdir(imageFolderPath)

    fext = '.png'

    # check for non image files and remove from list
    for name in fileNames:
        if (fext in name) == False:
            fileNames.remove(name)

    # return list of fileNames and the image folder path
    return fileNames,imageFolderPath

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

# finds the corners for a single dataset
def findCorners(folderName):

    row = 6
    col = 7
    # initialize object points array
    objPoint_singleImage = np.zeros((row*col, 3),np.float32)
    imgLength = len(objPoint_singleImage)

    countRows = 0
    countCols = 0

    for i in range(imgLength): # total array len
        objPoint_singleImage[i,0] = countRows
        objPoint_singleImage[i,1] = countCols

        countRows += 1

        if countRows == row:
            countRows = 0
            countCols += 1

    # initialize final point storage

    objectPoints = [] #3D
    imagePoints = [] #2D
    failFile = []
    sucess = []
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

        # if pattern was found execute below
        if retval == True:
            sucess.append()
            # store the object points
            objectPoints.append(objPoint_singleImage)

            # find the corresponding corners in image space
            imgCorners = cv2.cornerSubPix(grayScale,corners,(11,11),(-1,-1),termCond)

            # store image coordinates
            imagePoints.append(imgCorners)
        else:
            print('Pattern not found for ',fileName)
            failFile.append(fileName)

    imgShape = grayScale.shape

    return imgShape, objectPoints,imagePoints,failFile,success,imagesAllFileNames

