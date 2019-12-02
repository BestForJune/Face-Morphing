import os
import sys
import numpy as np
import scipy
from scipy.spatial import Delaunay
import scipy.interpolate
from scipy import ndimage
import imageio
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.path as mpltPath
import tempfile

from pprint import pprint as pp
import timeit
from PIL import Image
from PIL import ImageDraw

##############################################################################################
#input: leftPointFilePath: full file paths of the text files containing the (x,y) coordinates
#       from starting image
#       rightPointFilePath: full file paths of the text files containing the (x,y) coordinates
#       from ending image
#output: (leftTriangles, rightTriangles) list of Triangle class: triangles form by the given
#       coordinates
##############################################################################################
def loadTriangles(leftPointFilePath, rightPointFilePath):
    leftPointArr = np.loadtxt(leftPointFilePath, dtype="float64")
    rightPointArr = np.loadtxt(rightPointFilePath, dtype="float64")
    endindex = Delaunay(rightPointArr).simplices #generate triangle
    leftTriangles = [Triangle(n) for n in leftPointArr[endindex]]
    rightTriangles = [Triangle(n) for n in rightPointArr[endindex]]
    #leftTriangles = []
    #rightTriangles = []
    #for i in range(len(endindex)):
        #leftTriangles.append(Triangle(leftPointArr[endindex][i]))
        #rightTriangles.append(Triangle(rightPointArr[endindex][i]))
    return (leftTriangles, rightTriangles)

##############################################################################################
#input: xy: point (x,y) from source image
#       xytra: point (x',y') from the target image
#Calculation in this function based on the formula below
#       A       .  h   =   b
#[x1 y1 1 0 0 0] [h11]   [x1']
#[0 0 0 x1 y1 1] [h12]   [y1']
# ...           .[h13] = ...
# ...            [h21]   ...
#[xn yn 1 0 0 0] [h22]   [xn']
#[0 0 0 xn yn 1] [h23]   [yn']
#output: H: affine projection matrix
#       [h11 h12 h13]
# H =   [h21 h22 h23]
#       [0 0 1]
##############################################################################################
def MatrixH(xy,xytra):
    A = np.array([[xy[0][0],xy[0][1],1,0,0,0], [0,0,0,xy[0][0],xy[0][1],1],
                  [xy[1][0],xy[1][1],1,0,0,0], [0,0,0,xy[1][0],xy[1][1],1],
                  [xy[2][0],xy[2][1],1,0,0,0], [0,0,0,xy[2][0],xy[2][1],1]])
    b = np.array([[xytra[0][0]], [xytra[0][1]], [xytra[1][0]], [xytra[1][1]], [xytra[2][0]], [xytra[2][1]]])
    h = np.linalg.solve(A,b)
    H = np.array([[h[0][0], h[1][0], h[2][0]],
                  [h[3][0], h[4][0], h[5][0]],
                  [0, 0, 1]])
    H = np.linalg.inv(H) ##H^(-1)
    return H

class Triangle:
    def __init__(self, vertices):
        if not isinstance(vertices, np.ndarray) or vertices.shape != (3,2):
            raise ValueError("Input argument does not have the expected dimensions.")
        if vertices.dtype != 'float64':
            raise ValueError("Input argument is not float64 type.")
        self.vertices = vertices
        self.path = mpltPath.Path(self.vertices)

    ##############################################################################################
    # input: none
    # output: trianglepointsarray: list of (x,y) coordinates that contained inside the self
    #         triangle
    ##############################################################################################
    def getPoints(self):
        minx = self.vertices.min(0)[0] #(0)column (1)row [0]first column : y
        maxx = self.vertices.max(0)[0]
        miny = self.vertices.min(0)[1] #[1]second column:x
        maxy = self.vertices.max(0)[1]

        trianglepoints = []
        for x in range(np.int(minx), np.int(maxx+1)):
            for y in range(np.int(miny), np.int(maxy+1)):
                trianglepoints.append((x,y))
        trianglepointsarray = np.array(trianglepoints, dtype=np.float64)
        ##Point in Polygon - check if all the points in the triangles
        indexarr = self.path.contains_points(trianglepointsarray)
        trianglepointsarray = trianglepointsarray[indexarr]
        return trianglepointsarray

class Morpher:
    def __init__(self, leftImage, leftTriangles, rightImage, rightTriangles):
        if not all(isinstance(n, Triangle) for n in leftTriangles) or not all(isinstance(n, Triangle) for n in rightTriangles):
            raise TypeError("Input argument leftTriangles and rightTriangles should be Triangle type.")
        if not isinstance(leftImage, np.ndarray) or not isinstance(rightImage,np.ndarray):
            raise TypeError("Input argument leftImage and rightImage should be numpy array.")
        if leftImage.dtype != "uint8" or rightImage.dtype != "uint8":
            raise TypeError("Input argument leftImage and rightImage should be type unit8.")
        self.leftImage = leftImage
        self.leftTriangles = leftTriangles
        self.rightImage = rightImage
        self.rightTriangles = rightTriangles
        #Bilinear Interpolation
        #avoid by using inter directly (4 better performance)
        #x = np.arange(np.shape(rightImage)[0])
        #y = np.arange(np.shape(rightImage)[1])
        #self.leftpoint = scipy.interpolate.RectBivariateSpline(x, y, self.leftImage)
        #self.rightpoint = scipy.interpolate.RectBivariateSpline(x, y, self.rightImage)

    ##############################################################################################
    # input: alpha: Alpha blending, a value between 0 and 1
    #               controls how much of each image we are adding in the final blended version
    # formula used in this function: B = (1-alpha)*I1 + alpha*I2
    # output: midgraph: result of blending between the two target images
    ##############################################################################################
    def getImageAtAlpha(self, alpha):
        if alpha == 0:
            return self.leftImage
        if alpha == 1:
            return self.rightImage
        midgraph = np.zeros(dtype=np.uint8, shape=self.rightImage.shape) #empty image

        for i in range(len(self.rightTriangles)):
            midtriangle = Triangle((1-alpha) * self.leftTriangles[i].vertices + alpha * self.rightTriangles[i].vertices)
            HFromLeft = MatrixH(self.leftTriangles[i].vertices, midtriangle.vertices)
            HFromright = MatrixH(self.rightTriangles[i].vertices, midtriangle.vertices)

            #OLD version: find out all points in the given triangle
            #midpoints = midtriangle.getPoints()
            #NEW version: generate a new image with the given triangle fill in with white color
            #             use np.where to find out all the int points within the triangle
            tmpimag = Image.new('L', (self.rightImage.shape[1], self.rightImage.shape[0]), 0)
            pointsToBeFill = (tuple(midtriangle.vertices[0]),tuple(midtriangle.vertices[1]), tuple(midtriangle.vertices[2]))
            ImageDraw.Draw(tmpimag).polygon(pointsToBeFill, fill = 255, outline = 255)

            (indy, indx) = np.where(np.array(tmpimag) == 255)
            midpoints = np.concatenate((indx[None].T, indy[None].T), axis = 1)
            b = np.insert(midpoints,2,1,axis = 1).transpose()
            targetleft = np.matmul(HFromLeft, b).astype(int)
            targetright = np.matmul(HFromright, b).astype(int)

            #OLD version: use for loop to find out the value in the source images with the given coordinates
            #             use formula B = (1-alpha)*I1 + alpha*I2 to blend it
            # lval = list(self.leftImage[x,y] for x,y in zip(targetleft[1], targetleft[0]))
            # val = list(self.rightImage[x,y] for x,y in zip(targetright[1], targetright[0]))
            # for index in range(len(b[0])):
            #   lval = self.leftImage[targetleft[1][index],targetleft[0][index]] #[1]column:x [0]row:y
            #   rval = self.rightImage[targetright[1][index],targetright[0][index]]
            #   midgraph[int(midpoints[index][1])][int(midpoints[index][0])] = np.float64(lval) * (1.0 - alpha) + np.float64(rval) * (alpha)
            #NEW version: solve everything above with a single function:)
            self.combineimage(midgraph, targetleft, targetright, indy, indx, alpha)
        return np.uint8(midgraph)

    def combineimage(self, midgraph, targetleft, targetright, indy, indx, alpha):
        lval = scipy.ndimage.map_coordinates(self.leftImage, [targetleft[1], targetleft[0]], order = 1)
        rval = scipy.ndimage.map_coordinates(self.rightImage, [targetright[1], targetright[0]], order=1)
        midgraph[indy, indx] = (1.0-alpha) * lval + alpha * rval
        pass

    def saveVideo(self, targetFilePath, frameCount, frameRate, includeReversed):
        #if not os.path.exists(targetFilePath):
            #os.makedirs(targetFilePath)
        with tempfile.TemporaryDirectory(dir='/tmp/') as f:
            for i in range(0,frameCount + 1):
                temp = self.getImageAtAlpha(i/frameCount)
                imageio.imsave(f+'%03d'%(i)+'.png',temp)
                if includeReversed:
                    imageio.imsave(f + '%03d' % (2*frameCount-i) + '.png', temp)
            os.system("ffmpeg -framerate {0} -i {1} {2}".format(frameRate, f+'%03d.png', targetFilePath))
            for i in range(0, frameCount + 1):
                os.remove(f+'%03d'%(i)+'.png')
                if includeReversed and i != 2*frameCount-i:
                    os.remove(f + '%03d' % (2*frameCount-i) + '.png')
    pass

class ColorMorpher(Morpher):
    def __init__(self, leftImage, leftTriangles, rightImage, rightTriangles):
        super().__init__(leftImage, leftTriangles, rightImage, rightTriangles)

    def getImageAtAlpha(self, alpha):
        return super().getImageAtAlpha(alpha)

    def combineimage(self, midgraph, targetleft, targetright, indy, indx, alpha):
        lval = scipy.ndimage.map_coordinates(self.leftImage[:, :, 0], [targetleft[1], targetleft[0]], order=1)
        rval = scipy.ndimage.map_coordinates(self.rightImage[:,:,0], [targetright[1], targetright[0]], order=1)
        midgraph[indy, indx, np.zeros(len(indy), dtype=np.uint8)] = (1.0 - alpha) * lval + alpha * rval
        lval = scipy.ndimage.map_coordinates(self.leftImage[:,:,1], [targetleft[1], targetleft[0]], order=1)
        rval = scipy.ndimage.map_coordinates(self.rightImage[:,:,1], [targetright[1], targetright[0]], order=1)
        midgraph[indy, indx, np.ones(len(indy), dtype=np.uint8)] = (1.0 - alpha) * lval + alpha * rval
        lval = scipy.ndimage.map_coordinates(self.leftImage[:,:,2], [targetleft[1], targetleft[0]], order=1)
        rval = scipy.ndimage.map_coordinates(self.rightImage[:,:,2], [targetright[1], targetright[0]], order=1)
        midgraph[indy, indx, np.full(len(indy), 2, dtype=np.uint8)] = (1.0 - alpha) * lval + alpha * rval
        pass

    def saveVideo(self, targetFilePath, frameCount, frameRate, includeReversed):
        super().saveVideo(targetFilePath, frameCount, frameRate, includeReversed)
    pass

if __name__=='__main__':
    start = timeit.default_timer()
    # (starttri, endtri) = loadTriangles("points.left.txt", "points.right.txt")
    # leftImage = imageio.imread('LeftGray.png')
    # rightImage = imageio.imread('RightGray.png')
    # morpher = Morpher(leftImage, starttri, rightImage, endtri)
    # final = morpher.getImageAtAlpha(.75)
    # stop = timeit.default_timer()
    # print('Time: ', stop - start) #time for grey pic: 2.077s
    # Image.fromarray(final).show()
    #morpher.saveVideo("./Result/video.mp4", 15, 8, True)

    # tmpimag = Image.new('L', (1440, 1080), 0)
    # pointsToBeFill = (tuple([538.2, 541.9]), tuple([0.0, 540.0]), tuple([0.0, 1080.0]))
    # ImageDraw.Draw(tmpimag).polygon(pointsToBeFill, fill=255, outline=255)
    # tmpimag.show()

    (starttri, endtri) = loadTriangles("points.source.txt", "points.dest.txt")
    leftImage = imageio.imread('source.JPG')
    rightImage = imageio.imread('dest.JPG')
    colormorpher = ColorMorpher(leftImage, starttri, rightImage, endtri)
    final = colormorpher.getImageAtAlpha(.1)
    # Image.fromarray(final).show()
    # stop = timeit.default_timer()
    # print('Time: ', stop - start) #time for color pic: 4.161s
    #colormorpher.saveVideo("./Result/video.mp4", 15, 8, True)

    # (starttri, endtri) = loadTriangles("points.source.txt", "points.dest.txt")
    # leftImage = imageio.imread('source.JPG')
    # rightImage = imageio.imread('dest.JPG')
    # colormorpher = ColorMorpher(leftImage, starttri, rightImage, endtri)
    # colormorpher.saveVideo("./Result/video.mp4", 15, 8, True)

    stop = timeit.default_timer()
    print('Time: ', stop - start)