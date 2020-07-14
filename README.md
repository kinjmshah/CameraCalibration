# Camera Calibration

For Single Camera Calibration:
1. Take pictures of checkerboard placed in different locations with respect to the camera 15 to 20 times and place in folder called `singleCamCalib`
2. Execute the file `main.py` with a 1 as the only command line argument

For Stereo Camera Calibration:
1. Create folder called `stereoCamCalib` and create `camera1` and `camera2` folders as subdirectories
2. Take 15-20 pictures of the checkerboard in different locations with respect to the cameras. The cameras should stay in the same place. Ensure that the files are labeled such that the corresponding images in the `camera1` folder and `camera2` folder are the same (e.g. `camera1/01.png`,`camera2/01.png`)
3. Execute `main.py` with a `2` as the only command line argument

FILE OVERVIEW:
1. **main.py**: execute this file
2. **calibrations.py**: contains the two calibration functions for the single and stereo calibrations
- `singleCamera`
- `stereoCamera`
3. **helperFunctions.py**: contains support functions to modularize the calibration code
- `getFileNames`: allows extraction of all file names in a directory
- `reProjectionError`: calculates the re-projection error if given the object points, image points, rotation vector, translation vector, camera matrix, and distortion coefficients
- `findCorners`: checks to make sure corners are detectable and then initializes the object points and image points

Requirements:
1. ensure you are in a python3 enabled environment with OpenCV dependencies installed.

SPECIAL FEATURE:
1. In the calibrations.py file, in either function if you change "removeMaxError" value from 0 to 1, you will be able to observe the effect shown in the report of removing images with the maximum error from the calibration.
