# Augmented Reality Assignment 2

FUNCTION OVERVIEW:
1. main.py: exceute this file
2. calibrations.py: contains the two calibration functions for the single and stereo calibrations
- singleCamera
- stereoCamera
3. helperFunctions.py: contains support functions to modularize the calibration code
- getFileNames: allows extraction of all file names in a directory
- reProjectionError: calculates the re-projection error if given the object points, image points, rotation vector, translation vector, camera matrix, and distortion coefficients
- findCorners: checks to make sure corners are detectable and then initializes the object points and image points

TO RUN:
1. ensure you are in a python3 enabled environment with OpenCV dependencies installed.
2. execute the command python3 main.py dataSetNum
- here dataSetNum is a number between 1 and 3
3. the final outputs for all files will be printed on the command line and plots will be generated

SPECIAL FEATURE:
1. In the calibrations.py file, in either function if you change "removeMaxError" value from 0 to 1, you will be able to observe the effect shown in the report of removing images with the maximum error from the calibration.
