# DetectPlates.py

import cv2
import numpy as np
import math
import ProcessPlate
import random

import Preprocess
import DetectChars
import PossiblePlate
import PossibleChar

# module level variables ##########################################################################
PLATE_WIDTH_PADDING_FACTOR = 1.3
PLATE_HEIGHT_PADDING_FACTOR = 1.5

###################################################################################################


def detectPlatesInScene(imgOriginalScene):
    listOfPossiblePlates = []                   # this will be the return value

    height, width, numChannels = imgOriginalScene.shape

    imgGrayscaleScene = np.zeros((height, width, 1), np.uint8)
    imgThreshScene = np.zeros((height, width, 1), np.uint8)
    imgContours = np.zeros((height, width, 3), np.uint8)

    cv2.destroyAllWindows()

    if ProcessPlate.showSteps == True:  # show steps #######################################################
        cv2.imshow("0", imgOriginalScene)
    # end if # show steps #########################################################################

    imgGrayscaleScene, imgThreshScene = Preprocess.preprocess(
        imgOriginalScene)         # preprocess to get grayscale and threshold images

    if ProcessPlate.showSteps == True:  # show steps #######################################################
        cv2.imshow("1a", imgGrayscaleScene)
        cv2.imshow("1b", imgThreshScene)
    # end if # show steps #########################################################################

        # find all possible chars in the scene,
        # this function first finds all contours, then only includes contours that could be chars (without comparison to other chars yet)
    listOfPossibleCharsInScene = findPossibleCharsInScene(imgThreshScene)

    if ProcessPlate.showSteps == True:  # show steps #######################################################
        print("step 2 - len(listOfPossibleCharsInScene) = " + str(
            len(listOfPossibleCharsInScene)))  # 131 with MCLRNF1 image

        imgContours = np.zeros((height, width, 3), np.uint8)

        contours = []

        for possibleChar in listOfPossibleCharsInScene:
            contours.append(possibleChar.contour)
        # end for

        cv2.drawContours(imgContours, contours, -1, ProcessPlate.SCALAR_WHITE)
        cv2.imshow("2b", imgContours)
    # end if # show steps #########################################################################

        # given a list of all possible chars, find groups of matching chars
        # in the next steps each group of matching chars will attempt to be recognized as a plate
    listOfListsOfMatchingCharsInScene = DetectChars.findListOfListsOfMatchingChars(
        listOfPossibleCharsInScene)

    if ProcessPlate.showSteps == True:  # show steps #######################################################
        print("step 3 - listOfListsOfMatchingCharsInScene.Count = " + str(
            len(listOfListsOfMatchingCharsInScene)))  # 13 with MCLRNF1 image

        imgContours = np.zeros((height, width, 3), np.uint8)

        for listOfMatchingChars in listOfListsOfMatchingCharsInScene:
            intRandomBlue = random.randint(0, 255)
            intRandomGreen = random.randint(0, 255)
            intRandomRed = random.randint(0, 255)

            contours = []

            for matchingChar in listOfMatchingChars:
                contours.append(matchingChar.contour)
            # end for

            cv2.drawContours(imgContours, contours, -1,
                             (intRandomBlue, intRandomGreen, intRandomRed))
        # end for

        cv2.imshow("3", imgContours)
    # end if # show steps #########################################################################

    # for each group of matching chars
    for listOfMatchingChars in listOfListsOfMatchingCharsInScene:
        # attempt to extract plate
        possiblePlate = extractPlate(imgOriginalScene, listOfMatchingChars)

        if possiblePlate.imgPlate is not None:                          # if plate was found
            # add to list of possible plates
            listOfPossiblePlates.append(possiblePlate)
        # end if
    # end for

    print("\n" + str(len(listOfPossiblePlates)) +
          " possible plates found")  # 13 with MCLRNF1 image

    if ProcessPlate.showSteps == True:  # show steps #######################################################
        print("\n")
        cv2.imshow("4a", imgContours)

        for i in range(0, len(listOfPossiblePlates)):
            p2fRectPoints = cv2.boxPoints(
                listOfPossiblePlates[i].rrLocationOfPlateInScene)

            cv2.line(imgContours, tuple(p2fRectPoints[0]), tuple(
                p2fRectPoints[1]), ProcessPlate.SCALAR_RED, 2)
            cv2.line(imgContours, tuple(p2fRectPoints[1]), tuple(
                p2fRectPoints[2]), ProcessPlate.SCALAR_RED, 2)
            cv2.line(imgContours, tuple(p2fRectPoints[2]), tuple(
                p2fRectPoints[3]), ProcessPlate.SCALAR_RED, 2)
            cv2.line(imgContours, tuple(p2fRectPoints[3]), tuple(
                p2fRectPoints[0]), ProcessPlate.SCALAR_RED, 2)

            cv2.imshow("4a", imgContours)

            print("possible plate " + str(i) +
                  ", click on any image and press a key to continue . . .")

            cv2.imshow("4b", listOfPossiblePlates[i].imgPlate)
            cv2.waitKey(0)
        # end for

        print("\nplate detection complete, click on any image and press a key to begin char recognition . . .\n")
        cv2.waitKey(0)
    # end if # show steps #########################################################################

    return listOfPossiblePlates
# end function

###################################################################################################


def findPossibleCharsInScene(imgThresh):
    listOfPossibleChars = []                # this will be the return value

    intCountOfPossibleChars = 0

    imgThreshCopy = imgThresh.copy()

    contours, npaHierarchy = cv2.findContours(
        imgThreshCopy, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)   # find all contours

    height, width = imgThresh.shape
    imgContours = np.zeros((height, width, 3), np.uint8)

    for i in range(0, len(contours)):                       # for each contour

        if ProcessPlate.showSteps == True:  # show steps ###################################################
            cv2.drawContours(imgContours, contours, i,
                             ProcessPlate.SCALAR_WHITE)
        # end if # show steps #####################################################################

        possibleChar = PossibleChar.PossibleChar(contours[i])

        # if contour is a possible char, note this does not compare to other chars (yet) . . .
        if DetectChars.checkIfPossibleChar(possibleChar):
            intCountOfPossibleChars = intCountOfPossibleChars + \
                1           # increment count of possible chars
            # and add to list of possible chars
            listOfPossibleChars.append(possibleChar)
        # end if
    # end for

    if ProcessPlate.showSteps == True:  # show steps #######################################################
        # 2362 with MCLRNF1 image
        print("\nstep 2 - len(contours) = " + str(len(contours)))
        print("step 2 - intCountOfPossibleChars = " +
              str(intCountOfPossibleChars))  # 131 with MCLRNF1 image
        cv2.imshow("2a", imgContours)
    # end if # show steps #########################################################################

    return listOfPossibleChars
# end function


###################################################################################################
def extractPlate(imgOriginal, listOfMatchingChars):
    # this will be the return value
    possiblePlate = PossiblePlate.PossiblePlate()

    # sort chars from left to right based on x position
    listOfMatchingChars.sort(key=lambda matchingChar: matchingChar.intCenterX)

    # calculate the center point of the plate
    fltPlateCenterX = (listOfMatchingChars[0].intCenterX + listOfMatchingChars[len(
        listOfMatchingChars) - 1].intCenterX) / 2.0
    fltPlateCenterY = (listOfMatchingChars[0].intCenterY + listOfMatchingChars[len(
        listOfMatchingChars) - 1].intCenterY) / 2.0

    ptPlateCenter = fltPlateCenterX, fltPlateCenterY

    # calculate plate width and height
    intPlateWidth = int((listOfMatchingChars[len(listOfMatchingChars) - 1].intBoundingRectX + listOfMatchingChars[len(
        listOfMatchingChars) - 1].intBoundingRectWidth - listOfMatchingChars[0].intBoundingRectX) * PLATE_WIDTH_PADDING_FACTOR)

    intTotalOfCharHeights = 0

    for matchingChar in listOfMatchingChars:
        intTotalOfCharHeights = intTotalOfCharHeights + matchingChar.intBoundingRectHeight
    # end for

    fltAverageCharHeight = intTotalOfCharHeights / len(listOfMatchingChars)

    intPlateHeight = int(fltAverageCharHeight * PLATE_HEIGHT_PADDING_FACTOR)

    # calculate correction angle of plate region
    fltOpposite = listOfMatchingChars[len(
        listOfMatchingChars) - 1].intCenterY - listOfMatchingChars[0].intCenterY
    fltHypotenuse = DetectChars.distanceBetweenChars(
        listOfMatchingChars[0], listOfMatchingChars[len(listOfMatchingChars) - 1])
    fltCorrectionAngleInRad = math.asin(fltOpposite / fltHypotenuse)
    fltCorrectionAngleInDeg = fltCorrectionAngleInRad * (180.0 / math.pi)

    # pack plate region center point, width and height, and correction angle into rotated rect member variable of plate
    possiblePlate.rrLocationOfPlateInScene = (
        tuple(ptPlateCenter), (intPlateWidth, intPlateHeight), fltCorrectionAngleInDeg)

    # final steps are to perform the actual rotation

    # get the rotation matrix for our calculated correction angle
    rotationMatrix = cv2.getRotationMatrix2D(
        tuple(ptPlateCenter), fltCorrectionAngleInDeg, 1.0)

    # unpack original image width and height
    height, width, numChannels = imgOriginal.shape

    # rotate the entire image
    imgRotated = cv2.warpAffine(imgOriginal, rotationMatrix, (width, height))

    imgCropped = cv2.getRectSubPix(
        imgRotated, (intPlateWidth, intPlateHeight), tuple(ptPlateCenter))

    # copy the cropped plate image into the applicable member variable of the possible plate
    possiblePlate.imgPlate = imgCropped

    return possiblePlate
# end function
