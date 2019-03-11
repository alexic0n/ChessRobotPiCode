import cv2 as cv
import numpy as np
import math
import datetime
from util.util import *

class coordinateFinder:


    def __init__(self):
        self.coordinates = {}


    def getBoardState(self, topleft,bottomright,vc,bypass = False):
        if not bypass:
            x = input("Enter y to confirm you have made your move, or q to quit: ")
            if(x == "q"):
                return "q"
        counter = 0
        while(counter < 5):
            ret,img = vc.read()
            counter += 1
        if img is None:
            return "imagereadfail"
        now = datetime.datetime.now()
        cv.imwrite("{}.jpg".format(str(now)),img)

        # dimensions = [bottomright[1] - topleft[1], bottomright[0], topleft[0]]

        boardShapeY = img.shape[0]
        boardShapeX = img.shape[1]
            
        img = img[topleft[1]:bottomright[1], topleft[0]:bottomright[0]]
        # !!! [y, x]
        dimensions = img.shape

        cv.imwrite("{}x2.jpg".format(str(now)),img)

        print(dimensions)
        hsvImg = self.convertHSV(img)
        redCoor, redNames = self.processRed(hsvImg,dimensions)
        blueCoor, blueNames = self.processBlue(hsvImg,dimensions)
        bwFenTemp = "********/********/********/********/********/********/********/********"
        bwFen = []
        counter = 0
        self.coordinates = {}
        while (counter < 71):
            bwFen.insert(counter,bwFenTemp[counter])
            counter += 1
        for i in range(len(blueCoor)):
            blueLocation = blueCoor[i]
            blueName = blueNames[i]
            x,y = blueName
            blueNameString = coordinatesToSquare({"x": x, "y": y})
            self.coordinates[blueNameString] = {"x": blueLocation[0], "y": blueLocation[1]}
            pos = y*9 + x
            bwFen[pos] = "b"
        for i in range(len(redCoor)):
            whiteLocation = redCoor[i]
            redName = redNames[i]
            x,y = redName
            redNameString = coordinatesToSquare({"x": x, "y": y})
            self.coordinates[redNameString] = {"x": whiteLocation[0], "y": whiteLocation[1]}
            pos = y*9 + x
            bwFen[pos] = "w"
        print("")
        print("Current board interpreted as: ","".join(bwFen))
        return "".join(bwFen)

    def processRed(self,hsvImg,dimensions):
        redfilter = self.convertRed(hsvImg)
        forGaus = int(dimensions[0]*0.01)
        forRed = cv.blur(redfilter, (forGaus,forGaus))
        toWrite = forRed.copy()
        cv.imwrite("x.jpg",self.drawgrid(toWrite,dimensions))
        coordinatesRed = []
        self.getCentres(forRed, coordinatesRed)
        redNames = self.whichSquare(coordinatesRed,dimensions)
        return coordinatesRed, redNames

    def processBlue(self,hsvImg,dimensions):
        bluefilter = self.convertBlue(hsvImg)
        forGaus = int(dimensions[0]*0.01)
        forBlue = cv.blur(bluefilter, (forGaus,forGaus))
        toWrite = forBlue.copy()
        cv.imwrite("y.jpg",self.drawgrid(toWrite,dimensions))
        coordinatesBlue = []
        self.getCentres(forBlue, coordinatesBlue)
        blueNames = self.whichSquare(coordinatesBlue,dimensions)
        return coordinatesBlue, blueNames

    def convertHSV(self,image):
        hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
        return hsv

    def whichSquare(self,coordinates, dimensions):
        #letterCoor = "abcdefgh"
        sq_height = dimensions[0]/8
        sq_width = dimensions[1]/8
        gridCoor = []
        for coor in coordinates:
            x,y = coor
            print(x, y)
            xClass = x/sq_width
            yClass = y/sq_height
            print("X:", xClass)
            print("Y:", yClass)
            #gridCoor.insert(0, (letterCoor[math.floor(xClass)],(8-math.floor(yClass))))
            gridCoor.append((math.floor(xClass),math.floor(yClass)))
        return gridCoor


    #this function isn't used but can be useful for debugging
    def drawgrid(self,img,dimensions):
        #img = cv.cvtColor(img,cv.COLOR_HSV2BGR)
        sq_height = dimensions[0]/8
        sq_width = dimensions[1]/8
        counter = 0
        while (counter != 9):
            cv.line(img,(int(counter*sq_width),0),(int(counter*sq_width),dimensions[0]),(60,255,255),5)
            counter += 1
        counter = 0
        while (counter != 9):
            cv.line(img,(0,int(counter*sq_height)),(dimensions[1],int(counter*sq_height)),(60,255,255),5)
            counter += 1
        return img

    def getCentres(self,colourImg,coordinates):
        contours, _ = cv.findContours(colourImg,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
        for c in contours:
            # calculate moments for each contour
            M = cv.moments(c)
            # calculate x,y coordinate of center
            if(M["m00"] != 0):
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                coordinates.insert(0,(cX,cY))
        # display the image
        return

    def convertBlue(self,image):
        lower_blue = np.array([100,120,120],dtype=np.uint8)
        upper_blue = np.array([130,255,255],dtype=np.uint8)
        mask = cv.inRange(image, lower_blue, upper_blue)
        return mask

    def convertRed(self,image):
        # lower mask (0-10)
        lower_red = np.array([0,140,140])
        upper_red = np.array([10,255,255])
        mask0 = cv.inRange(image, lower_red, upper_red)

        # upper mask (170-180)
        lower_red = np.array([160,100,100])
        upper_red = np.array([180,255,255])
        mask1 = cv.inRange(image, lower_red, upper_red)

        # join my masks
        mask = mask0+mask1
        return mask
